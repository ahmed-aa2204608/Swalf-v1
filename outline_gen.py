import json


class OutlineContentGenerator:
    def __init__(self, deployment, model="fanar"):
        self.deployment = deployment
        self.model = model
    
    def generate_outline(self, topic, information, classification):
        """Generate content-focused outline based on topic and classification"""
        domain = classification['domain']
        style = classification['style']
        
        # Adjust tone based on style
        tone_instructions = {
            'رسمي': 'Use formal, professional tone',
            'عادي': 'Use clear, straightforward tone',
            'ودود': 'Use friendly, welcoming tone'
        }
        tone = tone_instructions.get(style, 'Use clear tone')
        
        prompt = f"""Create a structured podcast outline for this topic: {topic}

Information: {information}
Domain: {domain}
Tone: {tone}

Generate ALL CONTENT in Modern Standard Arabic (MSA). Keep JSON keys in English but all values in Arabic.

Return this exact JSON format:

{{
    "Intro1": {{
        "description": "وصف مختصر للبودكاست والترحيب العام",
        "script": ["بيان افتتاحي عن البودكاست", "رسالة ترحيب للمستمعين"]
    }},
    "Intro2": {{
        "description": "تقديم موضوع اليوم والإعداد",
        "script": ["تقديم موضوع اليوم", "لماذا هذا الموضوع مهم", "ما سيتعلمه المستمعون"]
    }},
    "Points": {{
        "talking_points": {{
            "النقطة الرئيسية الأولى": {{
                "discussion": "نقطة نقاش رئيسية حول الموضوع",
                "questions": [
                    "سؤال ذي صلة؟",
                    "سؤال متابعة؟"
                ],
                "response_hint": "الاتجاه المتوقع للإجابات"
            }},
            "النقطة الرئيسية الثانية": {{
                "discussion": "جانب مهم آخر للمناقشة",
                "questions": [
                    "سؤال ذي صلة آخر؟",
                    "سؤال تفصيلي؟"
                ],
                "response_hint": "الاتجاه المتوقع للإجابات"
            }},
            "النقطة الرئيسية الثالثة": {{
                "discussion": "النقطة الأساسية الأخيرة أو التطبيقات العملية",
                "questions": [
                    "سؤال عملي؟",
                    "سؤال حول التأثيرات المستقبلية؟"
                ],
                "response_hint": "الاتجاه المتوقع للإجابات"
            }}
        }}
    }},
    "Con": {{
        "description": "ملخص وخاتمة مدروسة",
        "script": ["ملخص النقاط الرئيسية", "سؤال ختامي يثير التفكير للجمهور"]
    }}
}}

Generate content that fits {domain} domain. All text content must be in Arabic."""

        try:
            response = self.deployment.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a podcast content planner. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.choices[0].message.content.strip()
            return self._parse_outline(result, topic, domain)
            
        except Exception as e:
            print(f"Outline generation error: {e}")
            return self._get_fallback_outline(topic, domain)
    
    def print_outline(self, outline):
        """Pretty print the outline in readable format"""
        print(json.dumps(outline, ensure_ascii=False, indent=2))
    
    def _parse_outline(self, result, topic, domain):
        """Parse and validate outline JSON"""
        try:
            # Clean up response
            result = result.replace('```json', '').replace('```', '').strip()
            
            outline = json.loads(result)
            
            # Validate structure
            required_sections = ['Intro1', 'Intro2', 'Points', 'Con']
            if all(section in outline for section in required_sections):
                outline['raw_output'] = result
                outline['topic'] = topic
                outline['domain'] = domain
                return outline
            else:
                return self._get_fallback_outline(topic, domain)
                
        except Exception:
            return self._get_fallback_outline(topic, domain)
    
    def _get_fallback_outline(self, topic, domain):
        """Generate simple fallback outline when LLM fails"""
        return {
            "Intro1": {
                "description": "نظرة عامة مختصرة عن البودكاست وترحيب عام",
                "script": [
                    "أهلاً وسهلاً بكم في بودكاستنا",
                    "اليوم نستكشف موضوعاً شيقاً ومهماً"
                ]
            },
            "Intro2": {
                "description": "تقديم موضوع اليوم",
                "script": [
                    f"موضوعنا اليوم هو {topic}",
                    "هذا موضوع مهم يستحق النقاش",
                    "دعونا نتعمق في الجوانب الرئيسية"
                ]
            },
            "Points": {
                "talking_points": {
                    "فهم الأساسيات": {
                        "discussion": f"ما هي المفاهيم الأساسية لـ {topic}؟",
                        "questions": [
                            f"ما هو {topic} بالضبط؟",
                            "لماذا هذا الموضوع مهم اليوم؟"
                        ],
                        "response_hint": "شرح واضح للمفاهيم الأساسية"
                    },
                    "التطبيقات الحالية": {
                        "discussion": f"كيف يتم استخدام {topic} في الممارسة العملية؟",
                        "questions": [
                            "ما هي بعض الأمثلة من الواقع؟",
                            "ما هي الفوائد التي نراها؟"
                        ],
                        "response_hint": "أمثلة عملية وفوائد"
                    },
                    "النظرة المستقبلية": {
                        "discussion": f"ما هو مستقبل {topic}؟",
                        "questions": [
                            "إلى أين ترى هذا المجال متجهاً؟",
                            "ما الذي يجب على الناس متابعته؟"
                        ],
                        "response_hint": "الاتجاهات والآثار المستقبلية"
                    }
                }
            },
            "Con": {
                "description": "ملخص وخاتمة مدروسة",
                "script": [
                    f"النقاط الرئيسية حول {topic} التي يجب تذكرها",
                    "ما الذي يجب أن يفكر فيه مستمعونا بعد هذه المناقشة؟"
                ]
            },
            "fallback_used": True,
            "topic": topic,
            "domain": domain
        }


def generate_outline(topic, information, classification, deployment=None):
    outline_generator = OutlineContentGenerator(deployment, "Fanar-C-1-8.7B")
    outline = outline_generator.generate_outline(topic, information, classification)
    return outline
