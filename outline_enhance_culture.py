import json
import random


class CulturalEnhancer:
    def __init__(self, deployment, model="fanar"):
        self.deployment = deployment
        self.model = model
        
        # Cultural expressions templates
        self.cultural_templates = {
            'opening': ['بسم الله نبدأ', 'على بركة الله نستهل', 'بإذن الله نبدأ'],
            'transitions': ['وهذا يقودنا إلى', 'ومن هنا ننتقل إلى', 'وبهذا نصل إلى'],
            'gratitude': ['نشكركم على هذا التوضيح', 'جزاكم الله خيراً', 'بارك الله فيكم'],
            'respect': ['الأستاذ الفاضل', 'الدكتور المحترم', 'أستاذنا الكريم'],
            'closing': ['بارك الله في علمكم', 'نسأل الله التوفيق', 'والله أعلم']
        }
    
    def add_cultural_context(self, enhanced_outline, classification):
        """Add cultural elements using micro-LLM calls for each individual element"""
        
        sensitivity = classification.get('sensitivity', 'عادي')
        culturally_enhanced = enhanced_outline.copy()
        
        try:
            # 1. Enhance FIRST script in Intro1 only
            if 'Intro1' in culturally_enhanced and 'script' in culturally_enhanced['Intro1']:
                scripts = culturally_enhanced['Intro1']['script']
                if scripts:
                    # Find main welcome script
                    for i, script in enumerate(scripts):
                        if 'مرحب' in script and len(script) > 20:
                            enhanced_script = self._enhance_single_text(
                                script, 
                                "Add 'بسم الله نبدأ،' at the beginning"
                            )
                            scripts[i] = enhanced_script
                            print(f"✅ Enhanced Intro1 script")
                            break
            
            # 2. Enhance guest introduction in Intro2
            if 'Intro2' in culturally_enhanced and 'script' in culturally_enhanced['Intro2']:
                scripts = culturally_enhanced['Intro2']['script']
                for i, script in enumerate(scripts):
                    if 'معنا اليوم' in script:
                        enhanced_script = self._enhance_single_text(
                            script,
                            "Add 'الأستاذ الفاضل' after 'معنا اليوم'"
                        )
                        scripts[i] = enhanced_script
                        print(f"✅ Enhanced Intro2 guest introduction")
                        break
            
            # 3. Enhance EACH talking point discussion separately
            if ('Points' in culturally_enhanced and 
                'talking_points' in culturally_enhanced['Points']):
                
                talking_points = culturally_enhanced['Points']['talking_points']
                point_keys = list(talking_points.keys())
                
                # Only enhance FIRST point with transition
                if point_keys:
                    first_key = point_keys[0]
                    first_point = talking_points[first_key]
                    
                    if 'discussion' in first_point:
                        enhanced_discussion = self._enhance_single_text(
                            first_point['discussion'],
                            "Add 'وهذا يقودنا إلى' at the beginning"
                        )
                        first_point['discussion'] = enhanced_discussion
                        print(f"✅ Enhanced first discussion point")
            
            # 4. Enhance conclusion - create clean closing
            if 'Con' in culturally_enhanced and 'script' in culturally_enhanced['Con']:
                scripts = culturally_enhanced['Con']['script']
                
                # Find the main closing statement
                main_closing = None
                for script in scripts:
                    if ('خلاصة' in script or 'ختتم' in script) and len(script) > 30:
                        main_closing = script
                        break
                
                if main_closing:
                    # Enhance the main closing with gratitude
                    enhanced_closing = self._enhance_single_text(
                        main_closing,
                        "Add 'نشكركم،' at the beginning and 'بارك الله فيكم' at the end"
                    )
                    
                    # Create clean script array
                    new_scripts = [enhanced_closing]
                    if sensitivity == 'حساس':
                        new_scripts.append("والله أعلم.")
                    
                    culturally_enhanced['Con']['script'] = new_scripts
                    print(f"✅ Enhanced conclusion")
            
            culturally_enhanced['culturally_enhanced'] = True
            print("✅ All cultural enhancements completed successfully!")
            return culturally_enhanced
            
        except Exception as e:
            print(f"Cultural enhancement error: {e}")
            return self._add_cultural_fallback(enhanced_outline, sensitivity)
    
    def _enhance_single_text(self, original_text, instruction):
        """Enhance a single piece of text with simple instruction"""
        
        prompt = f"""{instruction}

Original: {original_text}

Return only the enhanced text."""
        
        try:
            response = self.deployment.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return only the enhanced text. No explanations, no quotes, no extra text."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            enhanced = response.choices[0].message.content.strip()
            
            # Clean up any quotes or extra formatting
            enhanced = enhanced.strip('"').strip("'").strip()
            
            return enhanced
            
        except Exception as e:
            print(f"❌ Text enhancement failed: {e}")
            # Fallback to simple manual enhancement
            if "بسم الله نبدأ" in instruction:
                return f"بسم الله نبدأ، {original_text}"
            elif "الأستاذ الفاضل" in instruction:
                return original_text.replace("معنا اليوم", "معنا اليوم الأستاذ الفاضل")
            elif "وهذا يقودنا إلى" in instruction:
                return f"وهذا يقودنا إلى {original_text}"
            elif "نشكركم" in instruction and "بارك الله فيكم" in instruction:
                return f"نشكركم، {original_text} بارك الله فيكم."
            else:
                return original_text
    
    def _enhance_intro1(self, intro1_section):
        """Integrate opening blessing into the first script naturally"""
        prompt = f"""Modify the first script line to include "بسم الله نبدأ" naturally at the beginning.

Current first script: "{intro1_section['script'][0] if intro1_section.get('script') else ''}"

Make it: "بسم الله نبدأ، [rest of the script]"

Return only the enhanced script text, not full JSON."""
        
        try:
            response = self.deployment.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return only the enhanced script text. No JSON, no explanations."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            enhanced_script = response.choices[0].message.content.strip().strip('"')
            
            # Apply the enhancement
            enhanced = intro1_section.copy()
            if 'script' in enhanced and enhanced['script']:
                enhanced['script'][0] = enhanced_script
            print("✅ Intro1 enhanced successfully")
            return enhanced
            
        except Exception as e:
            print(f"❌ Intro1 enhancement failed: {e}")
            # Simple fallback - integrate manually
            enhanced = intro1_section.copy()
            if 'script' in enhanced and enhanced['script']:
                current = enhanced['script'][0]
                enhanced['script'][0] = f"بسم الله نبدأ، {current}"
            return enhanced
    
    def _enhance_intro2(self, intro2_section):
        """Integrate respectful address naturally into guest introduction"""
        prompt = f"""Find the script line that introduces the guest and add "الأستاذ الفاضل" naturally.

Current scripts: {intro2_section.get('script', [])}

Modify the line that says "معنا اليوم" to include "الأستاذ الفاضل" naturally.

Return only the modified script line, not full JSON."""
        
        try:
            response = self.deployment.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return only the enhanced script text. No JSON, no explanations."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            enhanced_script = response.choices[0].message.content.strip().strip('"')
            
            # Apply the enhancement
            enhanced = intro2_section.copy()
            if 'script' in enhanced:
                for i, script in enumerate(enhanced['script']):
                    if 'معنا اليوم' in script:
                        enhanced['script'][i] = enhanced_script
                        break
            print("✅ Intro2 enhanced successfully")
            return enhanced
            
        except Exception as e:
            print(f"❌ Intro2 enhancement failed: {e}")
            # Simple fallback
            enhanced = intro2_section.copy()
            if 'script' in enhanced:
                for i, script in enumerate(enhanced['script']):
                    if 'معنا اليوم' in script and 'الأستاذ الفاضل' not in script:
                        enhanced['script'][i] = script.replace('معنا اليوم', 'معنا اليوم الأستاذ الفاضل')
                        break
            return enhanced
    
    def _enhance_points(self, points_section):
        """Integrate transition phrase naturally into first discussion"""
        if 'talking_points' not in points_section:
            return points_section
            
        points = list(points_section['talking_points'].keys())
        if not points:
            return points_section
            
        first_point = points[0]
        current_discussion = points_section['talking_points'][first_point]['discussion']
        
        prompt = f"""Add "وهذا يقودنا إلى" naturally at the beginning of this discussion.

Current discussion: "{current_discussion}"

Make it flow naturally: "وهذا يقودنا إلى [rest of discussion]"

Return only the enhanced discussion text, not full JSON."""
        
        try:
            response = self.deployment.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return only the enhanced discussion text. No JSON, no explanations."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            enhanced_discussion = response.choices[0].message.content.strip().strip('"')
            
            # Apply the enhancement
            enhanced = points_section.copy()
            enhanced['talking_points'][first_point]['discussion'] = enhanced_discussion
            print("✅ Points enhanced successfully")
            return enhanced
            
        except Exception as e:
            print(f"❌ Points enhancement failed: {e}")
            # Simple fallback
            enhanced = points_section.copy()
            enhanced['talking_points'][first_point]['discussion'] = f"وهذا يقودنا إلى {current_discussion}"
            return enhanced
    
    def _enhance_conclusion(self, con_section, sensitivity):
        """Integrate gratitude and blessing naturally into existing conclusion"""
        if not con_section.get('script'):
            return con_section
            
        # Enhance the last script with gratitude and blessing
        last_script = con_section['script'][-1]
        
        extra_blessing = " والله أعلم" if sensitivity == 'حساس' else ""
        
        prompt = f"""Add gratitude "نشكركم" and blessing "بارك الله فيكم" naturally to this closing.

Current closing: "{last_script}"

Integrate them naturally into the text, don't add as separate sentences.{extra_blessing}

Return only the enhanced closing text, not full JSON."""
        
        try:
            response = self.deployment.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return only the enhanced closing text. No JSON, no explanations."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            enhanced_closing = response.choices[0].message.content.strip().strip('"')
            
            # Apply the enhancement
            enhanced = con_section.copy()
            enhanced['script'][-1] = enhanced_closing
            print("✅ Conclusion enhanced successfully")
            return enhanced
            
        except Exception as e:
            print(f"❌ Conclusion enhancement failed: {e}")
            # Simple fallback
            enhanced = con_section.copy()
            enhanced['script'][-1] = f"نشكركم، {last_script} بارك الله فيكم{extra_blessing}."
            return enhanced
    
    def _parse_cultural_outline(self, result, original_outline):
        """Parse culturally enhanced outline"""
        print("=== DEBUGGING CULTURAL ENHANCEMENT ===")
        print(f"Raw result length: {len(result)}")
        print(f"Raw result (first 300 chars): {result[:300]}...")
        print(f"Raw result (last 200 chars): ...{result[-200:]}")
        
        try:
            # Clean response
            result_cleaned = result.replace('```json', '').replace('```', '').strip()
            print(f"After cleaning (first 200 chars): {result_cleaned[:200]}...")
            
            cultural_outline = json.loads(result_cleaned)
            print(f"JSON parsing successful!")
            print(f"Top-level keys found: {list(cultural_outline.keys())}")
            
            # Validate structure
            required_sections = ['Intro1', 'Intro2', 'Points', 'Con']
            missing_sections = [section for section in required_sections if section not in cultural_outline]
            
            print(f"Required sections: {required_sections}")
            print(f"Missing sections: {missing_sections}")
            
            if len(missing_sections) == 0:
                print("✅ All required sections found - CULTURAL SUCCESS!")
                cultural_outline['culturally_enhanced'] = True
                cultural_outline['raw_cultural'] = result
                return cultural_outline
            else:
                print(f"❌ Cultural validation failed - missing sections: {missing_sections}")
                print("Using cultural fallback...")
                return self._add_cultural_fallback(original_outline, 'عادي')
                
        except json.JSONDecodeError as e:
            print(f"❌ Cultural JSON parsing failed: {e}")
            print("Using cultural fallback...")
            return self._add_cultural_fallback(original_outline, 'عادي')
        except Exception as e:
            print(f"❌ Unexpected cultural error: {e}")
            print("Using cultural fallback...")
            return self._add_cultural_fallback(original_outline, 'عادي')
    
    def _add_cultural_fallback(self, outline, sensitivity):
        """Simple rule-based cultural enhancement fallback"""
        
        enhanced = outline.copy()
        
        # Add cultural opening to Intro1
        if 'Intro1' in enhanced and 'script' in enhanced['Intro1']:
            opening = random.choice(self.cultural_templates['opening'])
            enhanced['Intro1']['script'].insert(0, f"{opening}.")
        
        # Add respectful address to Intro2  
        if 'Intro2' in enhanced and 'script' in enhanced['Intro2']:
            respect = random.choice(self.cultural_templates['respect'])
            for i, script in enumerate(enhanced['Intro2']['script']):
                if 'معنا اليوم' in script:
                    enhanced['Intro2']['script'][i] = script.replace('معنا اليوم', f'معنا اليوم {respect}')
                    break
        
        # Add transition to first talking point
        if 'Points' in enhanced and 'talking_points' in enhanced['Points']:
            points = list(enhanced['Points']['talking_points'].keys())
            if points:
                first_point = points[0]
                transition = random.choice(self.cultural_templates['transitions'])
                current_discussion = enhanced['Points']['talking_points'][first_point]['discussion']
                enhanced['Points']['talking_points'][first_point]['discussion'] = f"{transition} {current_discussion}"
        
        # Add cultural closing to Con
        if 'Con' in enhanced and 'script' in enhanced['Con']:
            gratitude = random.choice(self.cultural_templates['gratitude'])
            closing = random.choice(self.cultural_templates['closing'])
            
            enhanced['Con']['script'].insert(0, f"{gratitude} على هذه المناقشة الثرية.")
            enhanced['Con']['script'].append(f"{closing}.")
            
            # Add extra religious expression for sensitive topics
            if sensitivity == 'حساس':
                enhanced['Con']['script'].append("والله أعلم.")
        
        enhanced['culturally_enhanced'] = True
        enhanced['fallback_cultural'] = True
        return enhanced
    
    def print_cultural_outline(self, cultural_outline):
        """Pretty print the culturally enhanced outline"""
        print("=== CULTURALLY ENHANCED OUTLINE ===")
        print(json.dumps(cultural_outline, ensure_ascii=False, indent=2))
        
        if cultural_outline.get('culturally_enhanced'):
            if cultural_outline.get('fallback_cultural'):
                print("\n⚠️ Note: Fallback cultural enhancement was used")
            else:
                print("\n✅ Successfully enhanced with cultural context")

# Usage example:
# cultural_enhancer = CulturalEnhancer(deployment, "fanar")
# final_outline = cultural_enhancer.add_cultural_context(enhanced_outline, classification)
# cultural_enhancer.print_cultural_outline(final_outline)

def enhance_outline_with_culture(outline, classification, deployment=None):
    cultural_enhancer = CulturalEnhancer(deployment, "Fanar-C-1-8.7B")
    final_outline = cultural_enhancer.add_cultural_context(outline, classification)
    cultural_enhancer.print_cultural_outline(final_outline)
    return final_outline