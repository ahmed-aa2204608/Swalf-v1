# -*- coding: utf-8 -*-
"""
main.py — Arabic Podcast Script Generator (uses persona_selector.py)

Pipeline:
1) Read topic + info from user (terminal)
2) Select personas (host + guest)
3) Classify topic
4) Generate outline
5) Enhance outline with personas
6) Enhance with cultural context
7) Generate final script
"""

import asyncio
from data.persona_db import personas
from api_init import get_deployment
from test2 import getTTS
from topic_classify import classify_topic
from outline_gen import generate_outline
from outline_enhance_persona import enhance_outline_with_personas
from outline_enhance_culture import enhance_outline_with_culture
from script_generator import script_generator

# NEW: import the whole selection from a separate file
from persona_selector import select_personas


def main():
    # 1) Input
    topic = input("أدخل الموضوع (Topic): ").strip()
    info = input("أدخل وصفاً أو معلومات عن الموضوع (Info): ").strip()

    # 2) Deployment / LLM routing
    deployment = get_deployment()

    # 3) Classification (can help selector's domain filter)
    classification = classify_topic(topic, info, deployment)

    # 4) Persona selection
    host, guest, sel = select_personas(topic, info, personas, classification=classification, k=2)

    # 5) Outline
    outline = generate_outline(topic, info, classification, deployment)
    # 6) Persona-enhanced outline
    persona_outline = enhance_outline_with_personas(outline, host, guest, deployment)

    # 7) Cultural enhancement
    culture_outline = enhance_outline_with_culture(persona_outline, classification, deployment)

    # 8) Final script
    arabic_persona = {"host": host, "guest": guest, "chemistry_note": "متكاملان دوراً وأسلوباً"}
    script = script_generator(culture_outline, arabic_persona, classification, deployment)
    print("\n=== Generating TTS Audio ===")
    audio_file = asyncio.run(getTTS(script))
    print(f"✅ Audio file generated: {audio_file}")

    # 9) Outputs
    print("\n================= PERSONA SELECTION =================")
    def brief(p):
        return f"{p.get('JobDescription','')} | أسلوب: {p.get('SpeakingStyle','')} | OCEAN(E)={p.get('OCEAN_Persona',{}).get('E','')}"
    print(f"Host : {brief(host)}")
    print(f"Guest: {brief(guest)}")

    print("\n================= CLASSIFICATION ====================")
    print(classification)

    print("\n================= OUTLINE ===========================")
    print(outline)

    print("\n================= PERSONA OUTLINE ===================")
    print(persona_outline)

    print("\n================= CULTURE OUTLINE ===================")
    print(culture_outline)

    print("\n================= FINAL SCRIPT ======================")
    print(script)
    print("\n✅ Done.")


if __name__ == "__main__":
    main()
