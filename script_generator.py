import json


class ScriptGenerator:
    def __init__(self, deployment, model="fanar"):
        self.deployment = deployment
        self.model = model
        self.context_history = []
        
        # Real podcast examples for few-shot learning
        self.examples = {
            'intro1': """المقدم: أهلا بكم معنا، اليوم رح نتكلم عن موضوع يعني مذهل شوي، الحوسبة الكمومية
المقدم: ورح نحاول نفهم أساسياتها سوا وكيف تختلف عن الكمبيوترات اللي نستخدمها والإمكانيات الرهيبة اللي ممكن تفتحها
المقدم: يقولون إنها ممكن تحل مسائل، أحتاج حواسيبنا الخارقة اليوم ملايين السنين، كيف ممكن هذا؟
المقدم: القصة بتبدأ من فكرة بصراحة كأنها خيال علمي""",
            
            'intro2': """الضيف: بدل ما نعتمد على الفيزياء العادية، الحواسيب دي بتدخل لعالم ميكانيكا الكم الغريب
الضيف: وبتستخدم دواهر زي التراكب وتشابك عشان تحسب
الضيف: طريقة تفكير مختلفة تماما عن معالجة المعلومات
المقدم: طيب، خلينا نبدأ بالفرق الجوهري""",
            
            'point': """المقدم: كمبيوتراتنا تستخدم البت، يا صفري يا واحد، بسيطة
المقدم: بس الحوسبة الكمومية بتستخدم الكيوبت
المقدم: ايش اللي يخلي الكيوبت ده مختلف لها الدرجة؟
الضيف: هنا بقى القوة والغرابة كلها
الضيف: الكيوبت مش بس صفر أو واحد
الضيف: بفضل التراكب الكمومي هو يقدر يكون صفر وواحد في نفس الوقت أو أي نسبة منهم""",
            
            'conclusion': """المقدم: إذن الخلاصة هي إننا نستخدم أغرب جوانب الفيزياء عشان نبتكر طريقة حساب جديدة كلياً
المقدم: طريقة ممكن تغير قواعد اللعبة في مجالات كثيرة
الضيف: تماماً كده
المقدم: الانتقال من البت للكيوبت مش مجرد سرعة زيادة
المقدم: لا دي قفزة نوعية في قدرات المعالجة"""
        }
    
    def generate_full_script(self, enhanced_outline, personas, classification):
        """Generate complete podcast script section by section with context flow"""
        
        host_name = "المقدم"
        guest_name = "الضيف"
        
        scripts = {}
        self.context_history = []
        
        try:
            # 1. Generate Intro1 script
            if 'Intro1' in enhanced_outline:
                scripts['Intro1'] = self._generate_intro1_script(
                    enhanced_outline['Intro1'], host_name
                )
                self.context_history.append(f"Intro1: {scripts['Intro1'][:100]}...")
                print("✅ Intro1 script generated")
            
            # 2. Generate Intro2 script
            if 'Intro2' in enhanced_outline:
                scripts['Intro2'] = self._generate_intro2_script(
                    enhanced_outline['Intro2'], host_name, guest_name
                )
                self.context_history.append(f"Intro2: {scripts['Intro2'][:100]}...")
                print("✅ Intro2 script generated")
            
            # 3. Generate Points scripts
            if 'Points' in enhanced_outline and 'talking_points' in enhanced_outline['Points']:
                scripts['Points'] = self._generate_points_scripts(
                    enhanced_outline['Points']['talking_points'], host_name, guest_name
                )
                print("✅ Points scripts generated")
            
            # 4. Generate Conclusion script
            if 'Con' in enhanced_outline:
                scripts['Con'] = self._generate_conclusion_script(
                    enhanced_outline['Con'], host_name, guest_name, classification
                )
                print("✅ Conclusion script generated")
            
            print("✅ All scripts generated successfully!")
            return scripts
            
        except Exception as e:
            print(f"Script generation error: {e}")
            return self._get_fallback_scripts(enhanced_outline, host_name, guest_name)
    
    def _generate_intro1_script(self, intro1_section, host_name):
        """Generate brief opening script"""
        
        content = intro1_section.get('description', '') + " " + " ".join(intro1_section.get('script', []))
        
        prompt = f"""Generate a natural podcast opening (6-8 very short turns).

Topic: {content}

Style example (don't copy, use as reference only):
{self.examples['intro1']}

Requirements:
- Use ONLY these speaker names: المقدم and الضيف
- Format each line as: المقدم: [dialogue] or الضيف: [dialogue]
- Start with casual welcome, not formal
- Include natural hesitations: اممم، يعني، شوي
- Include emotional tags: <happy>, <sad>, <surprised>, <scared>, <anger> if needed
- Use Gulf dialect: شلون، وش رايك، زين، ماشي
- Include thinking moments: [pause: 1s]
- Avoid English words - use only Arabic
- Include some incomplete thoughts ending with ... [pause: 1s]
- Make it sound spontaneous, not scripted
- Each turn: MAX 1 sentence, MAX 20 words

Generate ONLY dialogue lines (no headers, no formatting):"""
        
        return self._call_fanar_for_script(prompt, "opening script")
    
    def _generate_intro2_script(self, intro2_section, host_name, guest_name):
        """Generate topic introduction with guest"""
        
        content = intro2_section.get('description', '') + " " + " ".join(intro2_section.get('script', []))
        previous_context = self.context_history[-1] if self.context_history else ""
        
        prompt = f"""Generate topic introduction and guest welcome (8-10 short turns).

Topic: {content}
Previous context: {previous_context}

Style example (don't copy, use as reference only):
{self.examples['intro2']}

Requirements:
- Use ONLY these speaker names: المقدم and الضيف
- Format each line as: المقدم: [dialogue] or الضيف: [dialogue]
- Casual guest introduction, not formal
- Include spontaneous reactions and natural flow
- Add hesitations: اممم، يعني، بصراحة
- Use Gulf dialect: شلون، طيب، زين
- Include emotional tags: <happy>, <sad>, <surprised>, <scared>, <anger> if needed
- Add natural pauses: [pause: 1s]
- Avoid English words - use only Arabic
- Include some incomplete thoughts ending with ... [pause: 1s]
- Make conversation feel unscripted
- Each turn: MAX 1 sentence, MAX 20 words

Generate ONLY dialogue lines (no headers, no formatting):"""
        
        return self._call_fanar_for_script(prompt, "intro2 script")
    
    def _generate_points_scripts(self, talking_points, host_name, guest_name):
        """Generate scripts for each talking point"""
        
        point_scripts = {}
        
        for i, (point_title, point_content) in enumerate(talking_points.items()):
            script = self._generate_single_point_script(
                point_title, point_content, host_name, guest_name, i
            )
            point_scripts[point_title] = script
            self.context_history.append(f"Point {i+1}: {script[:100]}...")
            print(f"✅ Generated script for point {i+1}")
        
        return point_scripts
    
    def _generate_single_point_script(self, point_title, point_content, host_name, guest_name, point_index):
        """Generate script for one talking point"""
        
        discussion = point_content.get('discussion', '')
        questions = point_content.get('questions', [])[:2]
        previous_context = self.context_history[-1] if self.context_history else ""
        
        prompt = f"""Generate dialogue for discussion point {point_index + 1} (20-25 short turns).

Point: {point_title}
Content: {discussion}
Questions: {questions}
Previous context: {previous_context}

Style example (don't copy, use as reference only):
{self.examples['point']}

Requirements:
- Use ONLY these speaker names: المقدم and الضيف
- Format each line as: المقدم: [dialogue] or الضيف: [dialogue]
- Create natural conversation, not interview-style Q&A
- Include spontaneous reactions: والله، صحيح؟، <surprised>
- Add natural hesitations: اممم، يعني، شوف، [pause: 2s]
- Use Gulf dialect: ايش، شلون، وش رايك، بس، زين
- Include thinking moments: [pause: 1s]
- Include emotional tags: <happy>, <sad>, <surprised>, <scared>, <anger> if needed
- Make responses build on each other naturally
- Include incomplete thoughts and natural interruptions
- Avoid English words - use only Arabic
- Include some incomplete thoughts ending with ... [pause: 1s]
- Each turn: MAX 1 sentence, MAX 20 words

Generate ONLY dialogue lines (no headers, no formatting):"""
        
        return self._call_fanar_for_script(prompt, f"point {point_index + 1} script")
    
    def _generate_conclusion_script(self, con_section, host_name, guest_name, classification):
        """Generate conclusion script"""
        
        content = con_section.get('description', '') + " " + " ".join(con_section.get('script', []))
        full_context = " | ".join(self.context_history[-2:])
        sensitivity = classification.get('sensitivity', 'عادي')
        
        extra_note = 'Add "والله أعلم" at the end' if sensitivity == 'حساس' else ''
        
        prompt = f"""Generate natural podcast conclusion (8-10 short turns).

Content: {content}
Previous discussion: {full_context}

Style example (don't copy, use as reference only):
{self.examples['conclusion']}

Requirements:
- Use ONLY these speaker names: المقدم and الضيف
- Format each line as: المقدم: [dialogue] or الضيف: [dialogue]
- Natural, casual conclusion - not formal summary
- Include spontaneous reactions and appreciation
- Add natural fillers: يعني، والله، بصراحة
- Use Gulf dialect: زين، ماشي، يعطيك العافية
- Include emotional tags: <happy>, <sad>, <surprised>, <scared>, <anger> if needed
- Add natural pauses for reflection: [pause: 1s]
- Avoid English words - use only Arabic
- Include some incomplete thoughts ending with ... [pause: 1s]
- Make it feel like natural conversation ending
- Each turn: MAX 1 sentence, MAX 20 words
{extra_note}

Generate ONLY dialogue lines (no headers, no formatting):"""
        
        return self._call_fanar_for_script(prompt, "conclusion script")
    
    def _call_fanar_for_script(self, prompt, script_type):
        """Call Fanar to generate script"""
        
        system_message = """You are an expert Arabic podcast dialogue writer.
Generate ONLY speaker dialogue lines. No headers, no stars, no formatting, no section titles.
Each line must start with either: المقدم: or الضيف:

Create natural, spontaneous Arabic conversations with these characteristics:
- Mix MSA with Gulf dialect (use: شلون، وش رايك، زين، ماشي، والله يهديك)
- Include natural fillers: يعني، اممم، اههه، بصراحة، شوي، طيب، خلاص
- Add thinking moments: [pause: 1s], [pause: 2s]
- Include emotional tags: <happy>, <sad>, <surprised>, <scared>, <anger> if needed
- Use incomplete thoughts and natural interruptions
- Each turn: MAX 1 sentence, MAX 20 words
- Make it sound unpolished and spontaneous, not scripted
- Avoid English words - use only Arabic
- Include some incomplete thoughts ending with ... [pause: 1s]"""
        
        try:
            response = self.deployment.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
            )
            
            script = response.choices[0].message.content.strip()
            
            # Clean up formatting issues - remove stars, headers, extra formatting
            lines = script.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                # Skip empty lines, stars, headers, or lines without speaker names
                if (line and 
                    not line.startswith('*') and 
                    not line.startswith('#') and 
                    not line.startswith('-') and
                    ('المقدم:' in line or 'الضيف:' in line)):
                    # Ensure line starts with speaker name
                    if 'المقدم:' in line and not line.startswith('المقدم:'):
                        line = 'المقدم:' + line.split('المقدم:')[1]
                    elif 'الضيف:' in line and not line.startswith('الضيف:'):
                        line = 'الضيف:' + line.split('الضيف:')[1]
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
            
        except Exception as e:
            print(f"❌ {script_type} generation failed: {e}")
            return f"المقدم: [فشل في توليد {script_type}]"
    
    def _get_fallback_scripts(self, enhanced_outline, host_name, guest_name):
        """Simple fallback scripts"""
        
        return {
            'Intro1': """المقدم: أهلاً بكم معنا في بودكاست جديد
المقدم: موضوعنا اليوم مثير ومهم""",
            'Intro2': """المقدم: معنا اليوم ضيف متخصص
الضيف: أهلاً، شكراً للاستضافة
المقدم: أهلاً وسهلاً""",
            'Points': {"نقطة": """المقدم: ايش رايك في هالموضوع؟
الضيف: والله موضوع مهم
المقدم: زين، شكراً"""},
            'Con': """المقدم: شكراً على هالمعلومات الحلوة
الضيف: الله يعافيك
المقدم: بارك الله فيكم"""
        }
    
    def print_scripts(self, scripts):
        """Pretty print all generated scripts with time estimation"""
        
        print("\n" + "="*50)
        print("GENERATED PODCAST SCRIPTS")
        print("="*50)
        
        total_turns = 0
        
        for section, script in scripts.items():
            print(f"\n--- {section} ---")
            if isinstance(script, dict):  # Points section
                for point_title, point_script in script.items():
                    print(f"\n** {point_title} **")
                    print(point_script)
                    total_turns += len([line for line in point_script.split('\n') 
                                      if line.strip().startswith(('المقدم:', 'الضيف:'))])
            else:
                print(script)
                total_turns += len([line for line in script.split('\n') 
                                  if line.strip().startswith(('المقدم:', 'الضيف:'))])
        
        estimated_minutes = (total_turns * 3.5) / 60
        
        print(f"\n--- STATS ---")
        print(f"Total turns: {total_turns}")
        print(f"Estimated TTS time: ~{estimated_minutes:.1f} minutes")
        print("="*50)

def script_generator(enhanced_outline, personas, classification, deployment=None):
    script_generator = ScriptGenerator(deployment, "Fanar-C-1-8.7B")
    scripts = script_generator.generate_full_script(enhanced_outline, personas, classification)
    script_generator.print_scripts(scripts)
    return scripts
