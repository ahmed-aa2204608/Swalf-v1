import json


class PersonaEnhancer:
    def __init__(self, deployment, model="fanar"):
        self.deployment = deployment
        self.model = model
    
    def enhance_outline_with_personas(self, outline, host_persona, guest_persona):
        """Enhance generic outline with specific host and guest personas"""
        
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

        try:
            response = self.deployment.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return only the requested JSON format. Do not add extra structure or wrapper objects."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.choices[0].message.content.strip()
            return self._parse_enhanced_outline(result, outline)
            
        except Exception as e:
            print(f"Persona enhancement error: {e}")
            return self._get_persona_enhanced_fallback(outline, host_persona, guest_persona)
    
    def _format_outline_simple(self, outline):
        """Simple outline formatting for prompt"""
        return json.dumps(outline, ensure_ascii=False, indent=2)
    
    def _format_outline_for_prompt(self, outline):
        """Format outline for prompt (simplified version)"""
        formatted = ""
        
        # Add Intro sections
        if 'Intro1' in outline:
            formatted += f"Intro1: {outline['Intro1']['description']}\n"
            formatted += f"Scripts: {outline['Intro1']['script']}\n\n"
        
        if 'Intro2' in outline:
            formatted += f"Intro2: {outline['Intro2']['description']}\n"
            formatted += f"Scripts: {outline['Intro2']['script']}\n\n"
        
        # Add talking points
        if 'Points' in outline and 'talking_points' in outline['Points']:
            formatted += "Main Discussion Points:\n"
            for point_title, point_content in outline['Points']['talking_points'].items():
                formatted += f"- {point_title}: {point_content['discussion']}\n"
                formatted += f"  Questions: {point_content['questions']}\n"
                formatted += f"  Response hint: {point_content['response_hint']}\n\n"
        
        # Add conclusion
        if 'Con' in outline:
            formatted += f"Conclusion: {outline['Con']['description']}\n"
            formatted += f"Scripts: {outline['Con']['script']}\n"
        
        return formatted
    
    def _parse_enhanced_outline(self, result, original_outline):
        """Parse and validate enhanced outline"""
        print("=== DEBUGGING PERSONA ENHANCEMENT ===")
        print(f"Raw result length: {len(result)}")
        print(f"Raw result (first 200 chars): {result[:200]}...")
        print(f"Raw result (last 200 chars): ...{result[-200:]}")
        
        try:
            # Clean up response - remove markdown
            print("\nCleaning response...")
            result_cleaned = result.replace('```json', '').replace('```', '').strip()
            
            # NEW: Find the first '{' character - this is where JSON actually starts
            json_start = result_cleaned.find('{')
            if json_start == -1:
                raise ValueError("No JSON object found in response")
                
            # Extract only the JSON part
            json_part = result_cleaned[json_start:]
            
            # Find the last '}' to ensure we get complete JSON
            json_end = json_part.rfind('}')
            if json_end == -1:
                raise ValueError("No closing brace found in JSON")
                
            json_clean = json_part[:json_end + 1]
            
            print(f"Found JSON starting at position: {json_start}")
            print(f"JSON length: {len(json_clean)}")
            print(f"JSON preview: {json_clean[:200]}...")
            
            # Try to parse JSON
            print("\nAttempting JSON parsing...")
            enhanced_outline = json.loads(json_clean)
            print("✅ JSON parsing successful!")
            
            # Rest of validation code remains the same...
            print(f"Parsed object type: {type(enhanced_outline)}")
            print(f"Top-level keys: {list(enhanced_outline.keys())}")
            
            # Validate structure
            required_sections = ['Intro1', 'Intro2', 'Points', 'Con']
            missing_sections = [section for section in required_sections if section not in enhanced_outline]
            
            if len(missing_sections) == 0:
                print("\n✅ VALIDATION SUCCESSFUL - All required sections found!")
                enhanced_outline['persona_enhanced'] = True
                enhanced_outline['raw_enhancement'] = result
                return enhanced_outline
            else:
                print(f"\n❌ VALIDATION FAILED - Missing sections: {missing_sections}")
                return self._get_persona_enhanced_fallback(original_outline, None, None)
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print("Using fallback...")
            return self._get_persona_enhanced_fallback(original_outline, None, None)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("Using fallback...")
            return self._get_persona_enhanced_fallback(original_outline, None, None)
    
    def _get_persona_enhanced_fallback(self, original_outline, host_persona, guest_persona):
        """Simple persona enhancement fallback"""
        enhanced = original_outline.copy()
        
        if host_persona and guest_persona:
            # Simple modifications to show persona influence
            host_job = host_persona.get('job_description', 'مقدم برامج')
            guest_job = guest_persona.get('job_description', 'ضيف متخصص')
            
            # Modify Intro2 to mention personas
            if 'Intro2' in enhanced:
                enhanced['Intro2']['script'].append(f"معنا اليوم {guest_job}")
                enhanced['Intro2']['script'].append(f"وسيقدم الحلقة {host_job}")
            
            # Add persona context to first talking point
            if 'Points' in enhanced and 'talking_points' in enhanced['Points']:
                points = list(enhanced['Points']['talking_points'].keys())
                if points:
                    first_point = points[0]
                    enhanced['Points']['talking_points'][first_point]['response_hint'] += f" من منظور {guest_job}"
        
        enhanced['persona_enhanced'] = True
        enhanced['fallback_used'] = True
        return enhanced
    
    def print_enhanced_outline(self, enhanced_outline):
        """Pretty print the enhanced outline"""
        print("=== PERSONA-ENHANCED OUTLINE ===")
        print(json.dumps(enhanced_outline, ensure_ascii=False, indent=2))
        
        if enhanced_outline.get('persona_enhanced'):
            if enhanced_outline.get('fallback_used'):
                print("\n⚠️ Note: Fallback enhancement was used")
            else:
                print("\n✅ Successfully enhanced with personas")



def enhance_outline_with_personas(outline, host_persona, guest_persona, deployment=None):
    persona_enhancer = PersonaEnhancer(deployment, "Fanar-C-1-8.7B")
    enhanced_outline = persona_enhancer.enhance_outline_with_personas(
        outline,
        host_persona,
        guest_persona
    )
    return enhanced_outline

