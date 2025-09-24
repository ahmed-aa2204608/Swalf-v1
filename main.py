from data.persona_db  import personas
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
model = SentenceTransformer("all-mpnet-base-v2")  # Load once globally 

from topic_classify import classify_topic
from api_init import get_deployment
from outline_gen import generate_outline
from outline_enhance_persona import enhance_outline_with_personas
from outline_enhance_culture import enhance_outline_with_culture
from script_generator import script_generator
from test2 import getTTS
import asyncio
def persona_to_text(p):
    return (
        f"{p['JobDescription']} Speaking style: {p['SpeakingStyle']}. "
        f"OCEAN traits: {', '.join(f'{k}:{v}' for k, v in p['OCEAN_Persona'].items())}."
    )

topic = input("Enter topic: ")
info = input("Enter info: ")
query = f"{topic}. {info}".strip()
print(query)
topic = "الطاقة المتجددة"
info = "تُشير الطاقة المتجددة إلى مصادر الطاقة التي تتجدد طبيعيًّا ولا تنفد مع الاستهلاك، مثل الطاقة الشمسية والرياح والمياه. تعتمد هذه المصادر على العمليات الطبيعية المستمرة، وتُعدّ خيارًا مهمًّا للحدّ من انبعاثات الكربون وتحقيق الاستدامة البيئية على المدى الطويل."# Encode query and personas
query_vec = model.encode([query])[0]
persona_texts = [persona_to_text(p) for p in personas]
persona_vecs = model.encode(persona_texts)

scores = cosine_similarity([query_vec], persona_vecs)[0]
sorted_indices = scores.argsort()[::-1]
top_personas = [personas[i] for i in sorted_indices[:2]]
print("Top 2 Personas:")
print(top_personas)
top_personas = [{'age': 'Adult', 'gender': 'Male', 'OCEAN_Persona':
                 {'O': 'Low', 'C': 'High', 'E': 'Medium', 'A': 'Low', 'N': 'High'},
                 'SpeakingStyle': 'Concise and reluctant to engage deeply.', 'JobDescription':
                 'An ethical hacker providing cybersecurity guidance for small businesses.'},
                 {'age': 'Teenager', 'gender': 'Male', 'OCEAN_Persona': {'O': 'High', 'C': 'Low', 'E': 'Low', 'A': 'Medium', 'N': 'High'},
'SpeakingStyle': 'Reserved and introspective, with a focus on authenticity', 'JobDescription': 'A tech-savvy student interested in developing Arabic-language AI tools to connect communities.'}]

top_personas

arabic_persona = {'host': {'age': 'Adult', 'gender': 'Male', 'OCEAN_Persona':
                           {'O': 'Medium', 'C': 'Medium', 'E': 'Medium', 'A': 'Medium', 'N': 'Medium'},
                           'JobDescription': 'مهندس ذكاء اصطناعي', 'SpeakingStyle': 'متحدث طبيعي ومباشر، يستخدم لغة واضحة ومفهومة', 'role': 'host', 'fallback_used': True},
                           'guest': {'age': 'Adult', 'gender': 'Male', 'OCEAN_Persona': {'O': 'High', 'C': 'Medium', 'E': 'High', 'A': 'Medium', 'N': 'Low'},
                                     'JobDescription': 'مهندس طاقة متجددة، يعمل على تطوير وتنفيذ حلول مستدامة في مجال التقنية الخضراء.',
                                     'SpeakingStyle': 'يتمتع بأسلوب حديث واضح ومباشر مع قدر من الاحترافية.', 'role': 'guest', 'raw_output':
                                     '{\n  "age": "Adult",\n  "gender": "Male", \n  "OCEAN_Persona": {\n    "O": "High",\n    "C": "Medium",\n    "E": "High",\n    "A": "Medium", \n    "N": "Low"\n  },\n  "JobDescription": "مهندس طاقة متجددة، يعمل على تطوير وتنفيذ حلول مستدامة في مجال التقنية الخضراء.",\n  "SpeakingStyle": "يتمتع بأسلوب حديث واضح ومباشر مع قدر من الاحترافية."\n}'}, 'chemistry_note': 'توازن جيد - تفاعل متوازن بين الشخصيتين'}
deployment = get_deployment()
classification = classify_topic(topic, info, deployment)
print("Classification:", classification)
outline = generate_outline(topic, info, classification, deployment)
print("Outline:", outline)
persona_outline = enhance_outline_with_personas(outline, arabic_persona['host'], arabic_persona['guest'], deployment)
print("Persona Outline:", persona_outline)
culture_outline = enhance_outline_with_culture(persona_outline, classification, deployment)
print("Culture Outline:", culture_outline)
script = script_generator(culture_outline, arabic_persona, classification, deployment)
print("Script:", script)

# Generate TTS audio
print("\n=== Generating TTS Audio ===")
audio_file = asyncio.run(getTTS(script))
print(f"✅ Audio file generated: {audio_file}")

#command to make venv
# python -m venv .venv
#command to activate venv
# .venv\Scripts\activate

#how to use reuirements.txt
# pip install -r requirements.txt