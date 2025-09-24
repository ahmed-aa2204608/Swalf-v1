# -*- coding: utf-8 -*-
"""
persona_selector.py
-------------------
Encapsulates persona selection for the Arabic podcast generator:
- Multilingual embeddings (Arabic-ready)
- Optional domain pre-filter using keywords
- Cosine ranking
- MMR diversification
- Host/Guest assignment (prefers higher Extraversion & presenter cues for Host)
"""

import os
import re
import json
import hashlib
from typing import List, Dict, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def _to_text(x) -> str:
    """Safely convert strings/dicts/lists to a flat string for keyword checks."""
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        # Prefer common fields if present; else fallback to JSON dump
        fields = ["label", "domain", "category", "type", "topic", "style", "tone", "keywords"]
        parts = []
        for k in fields:
            if k in x:
                v = x[k]
                if isinstance(v, str):
                    parts.append(v)
                elif isinstance(v, (list, tuple, set)):
                    parts.extend([str(i) for i in v])
                else:
                    parts.append(str(v))
        return " ".join(parts) if parts else json.dumps(x, ensure_ascii=False)
    if isinstance(x, (list, tuple, set)):
        return " ".join([str(i) for i in x])
    return str(x)


# =========================
# Embedding Model (Arabic-ready)
# =========================

EMBED_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
_EMBED_MODEL = None  # lazy init


def _get_embed_model():
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        _EMBED_MODEL = SentenceTransformer(EMBED_MODEL_NAME)
    return _EMBED_MODEL


# =========================
# Utilities
# =========================

OCEAN_MAP = {"Low": 1, "Medium": 2, "High": 3}


def _ocean_val(p: Dict, trait: str, default="Medium") -> int:
    """Map textual OCEAN level to numeric for comparisons."""
    return OCEAN_MAP.get(p.get("OCEAN_Persona", {}).get(trait, default), 2)


def _persona_valid(p: Dict) -> bool:
    """Ensure required keys exist to avoid crashes."""
    return all(k in p for k in ["JobDescription", "SpeakingStyle", "OCEAN_Persona"])


def _persona_to_text(p: Dict) -> str:
    """Flatten persona into a single string for embedding."""
    o = p.get("OCEAN_Persona", {})
    ocean_str = ", ".join(f"{k}:{o.get(k, '')}" for k in ["O", "C", "E", "A", "N"])
    return (
        f"{p.get('JobDescription', '')}. "
        f"أسلوب الحديث: {p.get('SpeakingStyle', '')}. "
        f"سمات OCEAN: {ocean_str}."
    )


def _stable_hash(obj) -> str:
    """Stable hash for caching vectors (invalidates cache when DB text changes)."""
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(blob.encode("utf-8")).hexdigest()


def _cache_vecs(texts: List[str], key: str, cache_dir: str = ".cache") -> np.ndarray:
    """Cache embeddings to disk for speed."""
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f"{key}.npy")
    if os.path.exists(path):
        return np.load(path)
    model = _get_embed_model()
    vecs = model.encode(texts, convert_to_numpy=True, batch_size=32, show_progress_bar=False)
    np.save(path, vecs)
    return vecs


# =========================
# Domains (expandable)
# =========================

def _topic_domain_keywords(topic: str, classification: str = "") -> List[str]:
    """
    Return domain keywords based on topic/classification to pre-filter personas.
    Extend easily by adding new blocks.
    """
    # NEW:
    text = (_to_text(topic) + " " + _to_text(classification)).lower()
    # Renewable energy / environment / sustainability
    if re.search(r"طاقة|متجددة|بيئة|كربون|شمس|رياح|مياه|استدامة", text):
        return ["طاقة", "طاقة متجددة", "استدامة", "بيئة",
                "سياسات الطاقة", "كفاءة الطاقة", "الهندسة المستدامة"]

    # Politics / diplomacy / governance
    if re.search(r"سياسة|دبلوماسي|حكومة|انتخابات|علاقات دولية|حَوكمة|دولة|اتفاق|مفاوضات", text):
        return ["سياسة", "دبلوماسية", "حكومة", "علاقات دولية", "مفاوضات", "اتفاقيات", "حوكمة"]

    # Economics / entrepreneurship / finance
    if re.search(r"اقتصاد|ريادة|شركات|تمويل|استثمار|نمو|سوق|مال|مشروع", text):
        return ["اقتصاد", "استثمار", "تمويل", "ريادة الأعمال", "شركات", "أسواق", "سياسات اقتصادية"]

    # Education / learning / youth
    if re.search(r"تعليم|مدرسة|جامعة|تعلم|شباب|طلاب|مناهج", text):
        return ["تعليم", "جامعة", "طلاب", "مناهج", "تعلم", "تدريس", "تنمية مهارات"]

    # Health / digital health / nursing / public health
    if re.search(r"صحة|طبي|رعاية|تمريض|صحة رقمية|وقاية|تغذية|مستشفى", text):
        return ["صحة", "رعاية صحية", "تمريض", "صحة رقمية", "وقاية", "تغذية", "سياسات صحية"]

    # Cybersecurity / software / AI
    if re.search(r"أمن|سيبراني|اختراق|برمجة|ذكاء اصطناعي|تعلم عميق|نموذج|خوارزمية|تطبيق|سحابة", text):
        return ["أمن سيبراني", "اختراق أخلاقي", "برمجة", "ذكاء اصطناعي", "تعلم آلي", "تعلم عميق", "حوسبة سحابية"]

    # Culture / heritage / arts / media
    if re.search(r"ثقافة|تراث|فن|إعلام|صحافة|محتوى|تقاليد|أدب|فولكلور|موسيقى|خط", text):
        return ["ثقافة", "تراث", "فن", "إعلام", "صحافة", "محتوى", "أدب", "موسيقى", "خط عربي"]

    # Sports / fitness
    if re.search(r"رياضة|كرة|لياقة|مباراة|بطولة|منتخب|تمرين", text):
        return ["رياضة", "كرة قدم", "لياقة", "بطولة", "منتخب", "تمارين", "تدريب"]

    # Architecture / urban planning / sustainability design
    if re.search(r"عمارة|معماري|عمران|تخطيط|مستدام|تصميم حضري|مباني", text):
        return ["عمارة", "تصميم مستدام", "تخطيط عمراني", "مباني خضراء", "تصميم حضري"]

    # Archaeology / history / anthropology
    if re.search(r"تاريخ|آثار|أنثروبولوجيا|حضارة|تنقيب", text):
        return ["تاريخ", "آثار", "حضارات", "تنقيب", "متحف", "تراث"]

    # Food / culinary / nutrition
    if re.search(r"طعام|مطبخ|وصفة|طهي|تغذية|مطعم", text):
        return ["طبخ", "وصفات", "مطبخ", "تغذية", "مأكولات تقليدية"]

    # Default: no pre-filter
    return []


# =========================
# Filtering / Ranking / MMR
# =========================

def _filter_candidates(personas_list: List[Dict], kws: List[str]) -> List[int]:
    """Return candidate indices matching domain keywords; relax if too few."""
    if not kws:
        return list(range(len(personas_list)))
    idxs = []
    for i, p in enumerate(personas_list):
        text = f"{p.get('JobDescription','')} {p.get('SpeakingStyle','')}"
        if any(kw in text for kw in kws):
            idxs.append(i)
    # if too few, relax filter
    return idxs if len(idxs) >= 5 else list(range(len(personas_list)))


def _rank_personas(query: str, vecs: np.ndarray, cand: List[int]) -> List[Tuple[int, float]]:
    """Rank candidates by cosine similarity to the query."""
    model = _get_embed_model()
    qv = model.encode([query], convert_to_numpy=True)[0]
    sims = cosine_similarity([qv], vecs[cand])[0]
    ranked = sorted(zip(cand, sims), key=lambda x: x[1], reverse=True)
    return ranked


def _mmr_select(vecs: np.ndarray, ranked: List[Tuple[int, float]], k: int = 2, lam: float = 0.7) -> List[int]:
    """
    Maximal Marginal Relevance to diversify selected personas:
    score = lam * relevance - (1 - lam) * similarity_to_selected
    """
    if not ranked:
        return []
    selected = [ranked[0][0]]
    remaining = [i for i, _ in ranked[1:]]
    while len(selected) < k and remaining:
        best, best_score = None, -1e9
        for c in remaining:
            rel = next(s for i, s in ranked if i == c)
            div = max(cosine_similarity([vecs[c]], vecs[selected])[0])
            score = lam * rel - (1 - lam) * div
            if score > best_score:
                best, best_score = c, score
        selected.append(best)
        remaining.remove(best)
    return selected


def _choose_host_guest(personas_list: List[Dict], selected_idxs: List[int]) -> Tuple[Dict, Dict]:
    """
    Host: prefer higher Extraversion and 'presenter' style cues.
    Guest: the other selected (often the topical expert).
    """
    if not selected_idxs:
        return None, None
    if len(selected_idxs) == 1:
        return personas_list[selected_idxs[0]], personas_list[selected_idxs[0]]

    a, b = selected_idxs[0], selected_idxs[1]

    def style_bonus(p: Dict) -> int:
        s = p.get("SpeakingStyle", "")
        cues = ["كاريزمي", "جذّاب", "حازم", "نشِط", "مرح", "واثق", "مقنع", "حيوي", "مهنية"]
        return 1 if any(c in s for c in cues) else 0

    score_a = _ocean_val(personas_list[a], "E") + style_bonus(personas_list[a])
    score_b = _ocean_val(personas_list[b], "E") + style_bonus(personas_list[b])

    host_idx = a if score_a >= score_b else b
    guest_idx = b if host_idx == a else a
    return personas_list[host_idx], personas_list[guest_idx]


# =========================
# Public API
# =========================

def select_personas(topic: str, info: str, personas_db: List[Dict], classification: str = "", k: int = 2):
    """
    High-level function used by main.py.

    Steps:
    - validate personas & embed (with caching)
    - optional domain pre-filter via keywords
    - rank by similarity to "topic | info"
    - diversify with MMR
    - choose host vs guest
    Returns: (host_dict, guest_dict, selected_indices_in_valid_list)
    """
    valid_personas = [p for p in personas_db if _persona_valid(p)]
    if len(valid_personas) < 2:
        # Fallback if DB is too small or malformed
        return (personas_db[0] if personas_db else None,
                personas_db[1] if len(personas_db) > 1 else personas_db[0],
                [0, 1])

    texts = [_persona_to_text(p) for p in valid_personas]
    vec_key = "personas_" + _stable_hash(texts)
    vecs = _cache_vecs(texts, vec_key)

    query = f"{topic.strip()} | {info.strip()}"
    kws = _topic_domain_keywords(topic, classification)
    cand = _filter_candidates(valid_personas, kws)
    ranked = _rank_personas(query, vecs, cand)
    sel = _mmr_select(vecs, ranked, k=k, lam=0.7)

    host, guest = _choose_host_guest(valid_personas, sel)

    # Safety fallback
    if host is None or guest is None:
        host = valid_personas[0]
        guest = valid_personas[1 if len(valid_personas) > 1 else 0]
        sel = [0, 1]

    return host, guest, sel
