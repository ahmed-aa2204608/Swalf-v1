"""
Test file for persona enhancement functionality
Allows testing with static outline, host and guest personas
Prints raw results before JSON parsing for debugging
"""

import json
from outline_enhance_persona import PersonaEnhancer
from api_init import get_deployment

def test_persona_enhancement():
    """Test function with static data and debug output"""
    
    # Static outline data
    static_outline = {'Intro1': {'description': 'مقدمة بودكاستنا التقنيّة و الترحيب بالمتابعين الجدد والأصدقاء القدامى.', 'script': ["بسم الله ننبدأ، مرحبا بكم في بودكاستنا الفني 'تقنية مستدامة'.", 'شكر خاص لجميع الذين اختاروا الانضمام إلينا في رحلتنا نحو فهم أفضل للتكنولوجيا الخضراء.']}, 'Intro2': {'description': 'إدخال موضوع اليوم - الطاقة المتجددة وأهميتها.', 'script': ['اليوم سنناقش الطاقة المتجددة؛ مصدر طاقة لا ينضب ويقدم حلولاً بيئية.', 'سنوضح سبب كونها حاسمة لمستقبل أكثر استدامة ولماذا يجب علينا جميعا  الاهتمام بها.', 'في نهاية الحلقة ستكون لديك فكرة واضحة عن كيفية عمل الطاقة المتجددة وفوائدها.']}, 'Points': {'talking_points': {'النقطة الرئيسية الأولى': {'discussion': 'وهذا يقودنا إلى تعريف الطاقة المتجددة ومصادره المختلفة.', 'questions': ['كيف تعمل كل نوع من أنواع الطاقة المتجددة?', 'هل هناك أي تحديات تواجه استخدام الطاقة المتجددة?'], 'response_hint': 'التوضيح بأن كل نوع له خصائصه الخاصة وأن بعض التحديات قد تشمل تكلفة التنفيذ الأولي ولكن لها فوائد طويلة الأجل.'}, 'النقطة الرئيسية الثانية': {'discussion': 'فوائد الطاقة المتجددة مقارنة بالطاقة غير المتجددة.', 'questions': ['ما هي الفوائد البيئية لاستخدام الطاقة المتجددة?', 'كيف تؤثر الطاقة المتجددة على الاقتصاد المحلي?'], 'response_hint': 'الإشارة إلى الحد من انبعاثات الغازات الدفيئة، خلق فرص العمل الجديدة، والاستقلال الطاقوي كأمثلة للفوائد.'}, 'النقطة الرئيسية الثالثة': {'discussion': 'دور تكنولوجيا المعلومات في تعزيز الطاقة المتجددة.', 'questions': ['كيف تساعد الذكاء الاصطناعي والإنترنت الأشياء في تحسين إدارة الطاقة المتجددة?', 'ما هو دور البيانات الضخمة في تطوير الطاقة المتجددة?'], 'response_hint': 'توضيح كيف يمكن لتقنيات الذكاء الاصطناعي والإنترنت الأشياء تحسين فعالية الشبكات الكهربائية وإدارة الطلب.'}}}, 'Con': {'description': 'تلخيص واستنتاج شامل.', 'script': ['دعونا نلخص أهم نقاط الحوار.', 'لننهي بملاحظة تشجع الجمهور على النظر في التحول نحو الطاقة المتجددة.']}, 'raw_output': '{\n"Intro1": {\n"description": "مقدمة بودكاستنا التقنيّة و الترحيب بالمتابعين الجدد والأصدقاء القدامى.",\n"script": ["مررحبا بكم في بودكاستنا الفني \'تقنية مستدامة\'. نحن هنا لنغوص في عالم الطاقة البديلة وكيف يمكنها أن تغير حياتنا.", "شكر خاص لجميع الذين اختاروا الانضمام إلينا في رحلتنا نحو فهم أفضل للتكنولوجيا الخضراء."]\n},\n"Intro2": {\n"description": "إدخال موضوع اليوم - الطاقة المتجددة وأهميتها.",\n"script": ["اليوم سنناقش الطاقة المتجددة؛ مصدر طاقة لا ينضب ويقدم حلولاً بيئية.", ""سنوضح سبب كونها حاسمة لمستقبل أكثر استدامة ولماذا يجب علينا جميعا الاهتمام بها.", "في نهاية الحلقة ستكون لديك فكرة واضحة عن كيفية عمل الطاقة المتجددة وفوائدها."]\n},\n"Points": {\n"talking_points": {\n    "النقطة الرئيسية الأولى": {\n    "discussion": "تعريف الطاقة المتجددة ومصادره المختلفة.",\n    "questions": ["كيف تعمل كل نوع من أنواع الطاقة المتجددة?", "هل هناك أي تحديات تواجه استخدام الطاقة المتجددة?"],\n    "response_hint": "التوضيح بأن كل نوع له خصائصه الخاصة وأن بعض التحديات قد تشمل تكلفة التنفيذ الأولي ولكن لها فوائد طويلة الأجل."\n    },\n    "النقطة الرئيسية الثانية": {\n    "discussion": "فوائد الطاقة المتجددة مقارنة بالطاقة غير المتجددة.",\n    "questions": ["ما هي الفوائد البيئية لاستخدام الطاقة المتجددة?", "كيف تؤثر الطاقة المتجددة على الاقتصاد المحلي?"],\n    "response_hint": "الإشارة إلى الحد من انبعاثات الغازات الدفيئة، خلق فرص العمل الجديدة، والاستقلال الطاقوي كأمثلة للفوائد."\n    },\n    "النقطة الرئيسية الثالثة": {\n    "discussion": "دور تكنولوجيا المعلومات في تعزيز الطاقة المتجددة.",\n    "questions": ["كيف تساعد الذكاء الاصطناعي والإنترنت الأشياء في تحسين إدارة الطاقة المتجددة?", "ما هو دور البيانات الضخمة في تطوير الطاقة المتجددة?"],\n    "response_hint": "توضيح كيف يمكن لتقنيات الذكاء الاصطناعي والإنترنت الأشياء تحسين فعالية الشبكات الكهربائية وإدارة الطلب."\n    }\n  }\n},\n"Con": {\n"description": "تلخيص واستنتاج شامل.",\n"script": ["دعونا نلخص أهم نقاط الحوار.", "لننهي بملاحظة تشجع الجمهور على النظر في التحول نحو الطاقة المتجددة." ]\n}\n}', 'topic': 'الطاقة المتجددة', 'domain': 'تقنية'}
    
    # Static host persona
    static_host_persona = {
        "JobDescription": "مقدم برامج تقنية متخصص في الذكاء الاصطناعي والتكنولوجيا الحديثة",
        "SpeakingStyle": "أسلوب حواري تفاعلي مع طرح أسئلة عميقة ومثيرة للاهتمام"
    }
    
    # Static guest persona
    static_guest_persona = {
        "JobDescription": "خبير في التحول الرقمي ومدير تقني في شركة تكنولوجيا كبرى",
        "SpeakingStyle": "أسلوب علمي مبسط مع استخدام أمثلة عملية من الواقع"
    }
    
    print("=== STARTING PERSONA ENHANCEMENT TEST ===")
    print(f"Original outline sections: {list(static_outline.keys())}")
    print(f"Host: {static_host_persona['JobDescription']}")
    print(f"Guest: {static_guest_persona['JobDescription']}")
    print("=" * 50)
    
    try:
        # Initialize the client
        print("Initializing API client...")
        deployment = get_deployment()
        
        # Create persona enhancer with custom debug version
        enhancer = DebugPersonaEnhancer(deployment, "Fanar")
        
        # Run the enhancement
        print("\nRunning persona enhancement...")
        enhanced_outline = enhancer.enhance_outline_with_personas(
            static_outline,
            static_host_persona,
            static_guest_persona
        )
        
        print("\n=== FINAL ENHANCED OUTLINE ===")
        print(json.dumps(enhanced_outline, ensure_ascii=False, indent=2))
        
        # Check if enhancement was successful
        if enhanced_outline.get('persona_enhanced'):
            if enhanced_outline.get('fallback_used'):
                print("\n⚠️  RESULT: Fallback enhancement was used")
            else:
                print("\n✅ RESULT: Successfully enhanced with personas")
        else:
            print("\n❌ RESULT: Enhancement failed")
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


class DebugPersonaEnhancer(PersonaEnhancer):
    """Enhanced version with more detailed debugging"""
    
    def enhance_outline_with_personas(self, outline, host_persona, guest_persona):
        """Enhanced version with detailed debug output"""
        
        # Extract persona information
        host_job = host_persona['JobDescription']
        host_style = host_persona['SpeakingStyle']
        guest_job = guest_persona['JobDescription']
        guest_style = guest_persona['SpeakingStyle']

        # Create a simplified version of current outline for the prompt
        current_outline_json = {
            "Intro1": outline.get("Intro1", {}),
            "Intro2": outline.get("Intro2", {}),
            "Points": outline.get("Points", {}),
            "Con": outline.get("Con", {})
        }
        
        prompt = f"""Enhance this podcast outline with the personas provided.

HOST: {host_job} - {host_style}
GUEST: {guest_job} - {guest_style}

CURRENT OUTLINE:
{self._format_outline_simple(current_outline_json)}

Enhance it by:
1. Modify introductions to mention the personas
2. Adjust questions to match host expertise
3. Update response hints for guest background
4. Keep all content in Arabic

Return the EXACT same JSON structure:

{{
    "Intro1": {{
        "description": "وصف بالعربية",
        "script": ["نص بالعربية"]
    }},
    "Intro2": {{
        "description": "وصف بالعربية", 
        "script": ["نص بالعربية"]
    }},
    "Points": {{
        "talking_points": {{
            "عنوان النقطة": {{
                "discussion": "النقاش بالعربية",
                "questions": ["سؤال بالعربية؟"],
                "response_hint": "توجيه الإجابة بالعربية"
            }}
        }}
    }},
    "Con": {{
        "description": "وصف بالعربية",
        "script": ["نص بالعربية"]
    }}
}}"""

        print("\n=== SENDING REQUEST TO API ===")
        print(f"Prompt length: {len(prompt)} characters")
        print("Prompt preview:")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("=" * 30)

        try:
            response = self.deployment.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return only the requested JSON format. Do not add extra structure or wrapper objects."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.choices[0].message.content.strip()
            
            print("\n=== RAW API RESPONSE ===")
            print(f"Response length: {len(result)} characters")
            print("=" * 20)
            print("FULL RAW RESPONSE:")
            print(result)
            print("=" * 20)
            print("END OF RAW RESPONSE")
            
            return self._parse_enhanced_outline_debug(result, outline)
            
        except Exception as e:
            print(f"\n❌ API ERROR: {e}")
            import traceback
            traceback.print_exc()
            return self._get_persona_enhanced_fallback(outline, host_persona, guest_persona)
    
    def _parse_enhanced_outline_debug(self, result, original_outline):
        """Enhanced parsing with detailed debugging"""
        print("\n=== PARSING RAW RESPONSE ===")
        print(f"Raw result type: {type(result)}")
        print(f"Raw result length: {len(result)}")
        print(f"First 200 characters: {repr(result[:200])}")
        print(f"Last 200 characters: {repr(result[-200:])}")
        
        try:
            # Clean up response
            print("\nCleaning response...")
            result_cleaned = result.replace('```json', '').replace('```', '').strip()
            print(f"After removing markdown: length = {len(result_cleaned)}")
            
            # Check for common issues
            if result_cleaned.startswith('```'):
                print("⚠️  Warning: Response still contains markdown")
                result_cleaned = result_cleaned[3:].strip()
                
            if result_cleaned.endswith('```'):
                print("⚠️  Warning: Response ends with markdown")
                result_cleaned = result_cleaned[:-3].strip()
            
            print(f"Final cleaned result (first 100 chars): {repr(result_cleaned[:100])}")
            
            # Try to parse JSON
            print("\nAttempting JSON parsing...")
            enhanced_outline = json.loads(result_cleaned)
            print("✅ JSON parsing successful!")
            
            # Analyze structure
            print(f"Parsed object type: {type(enhanced_outline)}")
            print(f"Top-level keys: {list(enhanced_outline.keys())}")
            
            # Validate structure
            required_sections = ['Intro1', 'Intro2', 'Points', 'Con']
            missing_sections = [section for section in required_sections if section not in enhanced_outline]
            
            print(f"Required sections: {required_sections}")
            print(f"Missing sections: {missing_sections}")
            
            # Check each section structure
            for section in required_sections:
                if section in enhanced_outline:
                    print(f"✅ {section}: {type(enhanced_outline[section])}")
                    if section in ['Intro1', 'Intro2', 'Con']:
                        required_keys = ['description', 'script']
                        for key in required_keys:
                            if key in enhanced_outline[section]:
                                print(f"  ✅ {key}: {type(enhanced_outline[section][key])}")
                            else:
                                print(f"  ❌ Missing {key}")
                    elif section == 'Points':
                        if 'talking_points' in enhanced_outline[section]:
                            print(f"  ✅ talking_points: {len(enhanced_outline[section]['talking_points'])} points")
                        else:
                            print(f"  ❌ Missing talking_points")
                else:
                    print(f"❌ Missing {section}")
            
            if len(missing_sections) == 0:
                print("\n✅ VALIDATION SUCCESSFUL - All required sections found!")
                enhanced_outline['persona_enhanced'] = True
                enhanced_outline['raw_enhancement'] = result
                return enhanced_outline
            else:
                print(f"\n❌ VALIDATION FAILED - Missing sections: {missing_sections}")
                print("Falling back to simple enhancement...")
                return self._get_persona_enhanced_fallback(original_outline, None, None)
                
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON PARSING FAILED")
            print(f"Error: {e}")
            print(f"Error position: {e.pos if hasattr(e, 'pos') else 'unknown'}")
            
            # Show context around error
            if hasattr(e, 'pos') and e.pos:
                start = max(0, e.pos - 50)
                end = min(len(result_cleaned), e.pos + 50)
                print(f"Context around error:")
                print(f"'{result_cleaned[start:end]}'")
            
            print("Falling back to simple enhancement...")
            return self._get_persona_enhanced_fallback(original_outline, None, None)
            
        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR: {e}")
            import traceback
            traceback.print_exc()
            print("Falling back to simple enhancement...")
            return self._get_persona_enhanced_fallback(original_outline, None, None)


if __name__ == "__main__":
    test_persona_enhancement()
