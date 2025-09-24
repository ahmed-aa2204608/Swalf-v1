import asyncio
import edge_tts
import re
from pydub import AudioSegment
import io
import os
from typing import Dict, List, Tuple

class PodcastTTSGenerator:
    def __init__(self, host_voice="ar-SA-HamedNeural", guest_voice="ar-SA-ZariyahNeural"):
        """
        Initialize the TTS generator with two distinct voices.
        
        Available Arabic voices in Edge TTS:
        - ar-SA-HamedNeural (Male)
        - ar-SA-ZariyahNeural (Female)
        - ar-EG-SalmaNeural (Female)
        - ar-EG-ShakirNeural (Male)
        """
        self.host_voice = host_voice
        self.guest_voice = guest_voice
        self.audio_segments = []
        
    def parse_script_line(self, line: str) -> Tuple[str, str, str]:
        """
        Parse a single line to extract speaker, emotion, and text.
        Returns: (speaker, emotion, text)
        """
        # Match patterns like "المقدم:" or "الضيف:"
        speaker_pattern = r'^(المقدم|الضيف):\s*'
        
        # Extract speaker
        speaker_match = re.match(speaker_pattern, line)
        if not speaker_match:
            return None, None, line
        
        speaker = speaker_match.group(1)
        text = line[speaker_match.end():]
        
        # Extract emotion tags like <happy>, <excited>, etc.
        emotion_pattern = r'<(\w+)>'
        emotion_match = re.match(emotion_pattern, text)
        emotion = None
        
        if emotion_match:
            emotion = emotion_match.group(1)
            text = text[emotion_match.end():].strip()
        
        return speaker, emotion, text
    
    def create_ssml(self, text: str, emotion: str = None, speaker: str = None) -> str:
        """
        Create SSML markup for the text with appropriate emotion and prosody.
        """
        ssml = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-SA">'
        
        # Add prosody based on emotion
        if emotion:
            if emotion == "happy":
                ssml += '<prosody rate="1.1" pitch="+5%">'
            elif emotion == "excited":
                ssml += '<prosody rate="1.2" pitch="+10%" volume="+5dB">'
            elif emotion == "eager":
                ssml += '<prosody rate="1.15" pitch="+7%">'
            elif emotion == "interested":
                ssml += '<prosody rate="1.05" pitch="+3%">'
            elif emotion == "determined":
                ssml += '<prosody rate="0.95" pitch="-2%" volume="+3dB">'
            elif emotion == "agreeing":
                ssml += '<prosody rate="1.0" pitch="+2%">'
            else:
                ssml += '<prosody rate="1.0">'
        else:
            ssml += '<prosody rate="1.0">'
        
        # Clean the text and add it
        clean_text = text.strip()
        ssml += clean_text
        
        # Close prosody tag if emotion was added
        if emotion or True:  # Always close prosody
            ssml += '</prosody>'
        
        ssml += '</speak>'
        return ssml
    
    async def generate_audio_segment(self, text: str, voice: str, emotion: str = None) -> bytes:
        """
        Generate audio for a single text segment using Edge TTS.
        """
        # Create SSML
        ssml = self.create_ssml(text, emotion)
        
        # Use Edge TTS to generate audio
        communicate = edge_tts.Communicate(text, voice)
        
        # Generate audio data
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        return audio_data
    
    def process_script_section(self, section_text: str) -> List[Dict]:
        """
        Process a section of the script and return a list of dialogue entries.
        """
        dialogues = []
        lines = section_text.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            speaker, emotion, text = self.parse_script_line(line)
            if speaker:
                dialogues.append({
                    'speaker': speaker,
                    'emotion': emotion,
                    'text': text,
                    'voice': self.host_voice if speaker == "المقدم" else self.guest_voice
                })
        
        return dialogues
    
    async def process_full_script(self, script: Dict) -> str:
        """
        Process the entire podcast script and generate the final audio file.
        """
        all_dialogues = []
        
        # Process intro sections
        if 'Intro1' in script:
            all_dialogues.extend(self.process_script_section(script['Intro1']))
        elif 'Intro2' in script:
            all_dialogues.extend(self.process_script_section(script['Intro2']))
        
        # Add a short pause between sections
        all_dialogues.append({'pause': 1000})  # 1 second pause
        
        # Process main points
        if 'Points' in script:
            for point_title, point_content in script['Points'].items():
                # Optional: Add section title announcement
                # all_dialogues.append({
                #     'speaker': 'المقدم',
                #     'text': f"والآن، {point_title}",
                #     'voice': self.host_voice,
                #     'emotion': None
                # })
                all_dialogues.extend(self.process_script_section(point_content))
                all_dialogues.append({'pause': 800})  # 0.8 second pause between points
        
        # Process conclusion
        if 'Con' in script:
            all_dialogues.extend(self.process_script_section(script['Con']))
        
        # Generate audio for each dialogue
        audio_segments = []
        
        for i, dialogue in enumerate(all_dialogues):
            print(f"Processing segment {i+1}/{len(all_dialogues)}")
            
            if 'pause' in dialogue:
                # Add silence
                silence = AudioSegment.silent(duration=dialogue['pause'])
                audio_segments.append(silence)
            else:
                # Generate speech
                audio_data = await self.generate_audio_segment(
                    dialogue['text'],
                    dialogue['voice'],
                    dialogue.get('emotion')
                )
                
                # Convert to AudioSegment
                audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
                
                # Add a small pause after each dialogue (200ms)
                audio = audio + AudioSegment.silent(duration=200)
                audio_segments.append(audio)
        
        # Combine all audio segments
        print("Combining audio segments...")
        final_audio = sum(audio_segments)
        
        # Export to file
        import uuid
        import datetime
        
        # Create audio directory if it doesn't exist
        audio_dir = os.path.join(os.getcwd(), "audio_output")
        os.makedirs(audio_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"podcast_{timestamp}_{str(uuid.uuid4())[:8]}.mp3"
        output_path = os.path.join(audio_dir, output_filename)
        
        final_audio.export(output_path, format="mp3", bitrate="192k")
        print(f"Audio saved to {output_path}")
        
        return os.path.abspath(output_path)

async def getTTS(script=None):
    """
    Main function to generate TTS audio from a podcast script
    If no script is provided, uses a default example script
    """
    
    # Use provided script or default example
    if script is None:
        script = {
        'Intro1': 'المقدم: سلام عليكم جميعاً، مبروك أنتم هنا مع بودكاست "الطاقة للمستقبل"\nالضيف: <happy>أهلاً، شكراً على الدعوة، سعيد بأنني هنا\nالمقدم: أمم، أول شي، وش رأيك نبدا بشرح بسيط لسبب أهمية الطاقة المتجددة؟\nالضيف: طيب، بالطبع، هي مستدامة ولا تضر البيئة زي الوقود الأحفوري\nالمقدم: صحيح، وهذا مهم جداً للجيل الجديد\nالضيف: يعني، تخيل عالم بدون انقطاع كهرباء أو تلوث هواء\nالمقدم: <excited>والله يهديك، كلام جميل، دعنا ندخل أكثر في الموضوع',
        'Intro2': 'المقدم: مرحباً بكم مجدداً في بودكاست "الطاقة للمستقبل". اليوم, بشوفنا ضيف مميز.\nالضيف: <happy>مرحبا! سعيد بأن أكون هنا.\nالمقدم: طيب, قبل كل شيء, كيف حالك اليوم?\nالضيف: زين, والحمدلله.\nالمقدم: ممتاز, فخورون بمشاركتك خبرتك.\nالضيف: شكراً لك, أمم.. الطاقة المتجددة موضوع مهم جداً.\nالمقدم: بالتأكيد, دعنا نتعمق فيه.\nالضيف: يعني, هي مصدر مستدام للأجيال القادمة.\nالمقدم: صحيح, هذا نقطة البداية.',
        'Points': {
            'فهم الأساسيات': 'المقدم: طيب, قبل نبدأ بالتفاصيل, وش رايك نعرف أولا إيش هي الطاقة المتجددة?\nالضيف: <eager>بالطبع! هي الطاقة من مصادر طبيعية تتعاود وتتجدد باستمرار\nالمقدم: مثلاً الشمس والرياح... صح؟\nالضيف: تمام, هذي أمثلة مباشرة\nالمقدم: لكن ليش مهمة جداً الآن?\nالضيف: لأن العالم يتجه نحو خفض الانبعاثات الغازية\nالضيف: وإحنا بحاجة لتقليل الاعتماد على الوقود الأحفوري\nالمقدم: والله هذا نقطة هامة فعلا\nالمقدم: فكيف يمكن أن توضح لنا الفرق بينها وبين غير المتجددة?\nالضيف: حسنا, غير المتجددة مثل الفحم والنفط\nالضيف: وهي محدودة وغير قابلة للتجديد بسرعة كافية\nالضيف: بينما المتجددة مستمرة ومتوفرة دائماً تقريباً',
            'التطبيقات الحالية': 'المقدم: طيب, الضيف, وش رايك بشركات مثل "Masdar" بدولة الإمارات?\nالضيف: <excited>والله, رائعين! هم بيطورون تقنيات جديدة باستمرار\nالمقدم: صحيح, لكن كيف تطبق هذي التقنيات على أرض الواقع?\nالضيف: مثلاً, محطات الطاقة الشمسية الكبيرة في الصحراء\nالمقدم: وايه الفائدة من كذا بالنسبة للناس العاديين?\nالضيف: خفض تكلفة الكهرباء وتوفير فرص عمل جديدة\nالمقدم: أمم, بس ما فيه تحديات مع الرياح والأتربة وغيره?\nالضيف: بالتأكيد, لكنهم يعملون على حلول ذكية لهذه الأمور\nالضيف: زي استخدام أنظمة تنظيف خاصة للمحطات الهوائية\nالمقدم: هذا فعلاً رائع, وش رايك بأبحاث الخلايا الكهروضوئية الجديدة?\nالضيف: <interested>أحبها! لأنها بتحسن كفاءة تحويل ضوء الشمس لكهرباء\nالمقدم: صراحة, مستقبل الطاقة المتجددة يبدو مشرقاً\nالضيف: <agreeing>بالضبط, بشرط دعم الحكومات والمجتمعات له\nالمقدم: وأفكار الناس أيضاً مهمة, يعني ممكن كل شخص يساهم بطريقته الخاصة\nالضيف: تمام, حتى لو كان بزراعة أشجار أو تركيب ألواح شمسيّة صغيرة',
            'النظرة المستقبلية': 'المقدم: طيب, الضيف, وش رأيك بالاتجاهات المستقبيلة للطاقة الشمسية مثلاً?\nالضيف: اممم, أعتقد أنها ستكون أكثر انتشاراً بكثير\nالضيف: لكن أيضاً, الهيدروجين الأخضر له مستقبل كبير\nالمقدم: صحيح, سمعت عنه كثير مؤخراً\nالمقدم: وش نصيحتك لأولئك الراغبين في التعلم عنها أكثر?\nالضيف: اطلع على الأبحاث العلمية الحديثة أولاً\nالضيف: ثم انضم لمجتمعات المهتمين عبر الإنترنت\nالضيف: هناك الكثير من الدورات المجانية الآن\nالمقدم: هذا رائع, شكراً لك على هذه الأفكار\nالضيف: لا شيء, سعيد أن أساعد\nالضيف: فقط تذكر, المستقبل متعلق بالتغيير الجذري\nالمقدم: <interested>بالفعل, كيف نستعد لهذا التحول الكبير?\nالضيف: التعليم والتوعية هما المفتاح الأساسي\nالضيف: يجب علينا جميعاً فهم أهميته\nالمقدم: موافق, وهذا ما نحاول فعله اليوم\nالضيف: exactly, مهم جداً نشر الوعي حول الموضوع'
        },
        'Con': 'المقدم: طيب, قبل ما نخليكم, وش رسالتك الأخيرة للمستمعين?\nالضيف: <determined>أه, لازم يعرفوا أن كل خطوة صغيرة مهمة\nالمقدم: صحيح, حتى لو كانت تغيير مصباح واحد فقط\nالضيف: exactly, ويشجعون حكومتهم على الاستثمار أكثر\nالمقدم: ويعرفون حقهم في عالم طاقة نظيفة\nالضيف: <happy>يعني, هذا هو الحلم, صح؟\nالمقدم: بالتأكيد, حلم قابل للتحقيق إذا عملنا مع بعض\nالضيف: والله, شكراً لك على هذه الفرصة الرائعة\nالمقدم: ألف شكر لضيفتنا اليوم, تعطيها العافية\nالضيف: تشرفت بالمشاركة, إلى اللقاء!'
    }
    
    # Initialize the TTS generator
    # You can customize the voices here
    generator = PodcastTTSGenerator(
        host_voice="ar-SA-HamedNeural",  # Male voice for host
        guest_voice="ar-SA-ZariyahNeural"  # Female voice for guest
    )
    
    # Process the script and generate audio
    output_file = await generator.process_full_script(script)
    print(f"Podcast audio generation complete! File saved as: {output_file}")
    
    return output_file

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(getTTS(script=None))