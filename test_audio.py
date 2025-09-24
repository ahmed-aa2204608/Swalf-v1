#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append('.')
from test2 import getTTS

async def test_full_script():
    """Test the complete podcast script we generated"""
    
    script = {
        'Intro1': '''المقدم: سلام عليكم يا جماعة، مبروك أنتم هنا مع برنامجنا الجديد <happy>
الضيف: شكرا حالك المقدم، سعيد إنني أنا ضيف <happy>
المقدم: زين زين بس قبل كل شيء، وش رايك إذا بدينا بشوية خفيفة عن البرنامج؟
الضيف: طبعا ماشي، وما أحسن من كدا بداية
المقدم: أهلا، كدا برنامج تعليمي وممتع ونحن اليوم حول الأطعمة التقليدية <excited>
الضيف: أنتي أؤيد الموضوع وحاسة لأن الأكل جزء مهم من ثقافتنا
المقدم: بالضبط، وأنا حلقة عن الكبسة السعودية الشهيرة''',
        
        'Intro2': '''المقدم: مرحبا بكم جميعا! اليوم حلقاتنا خاصة جدا! <happy>
الضيف: شكرا لك، أنا متحمسة وأني هنا <happy>
المقدم: بالتأكيد، دعنا نرحب بطالبتنا العزيزة <happy>
الضيف: معا كن من أروع الناس الذي عرفتهم <happy>
المقدم: أنتي قبل كل شيء، كيف تعرفت علينا؟
الضيف: كنت أبحث عن وصفات قديمة، صادفتها صدفة <surprised>
المقدم: واا! هذا رائع، طيب أخبرينا عنها أكثر
الضيف: حسنا، اسمها فاطمة، عمرها كان الستين بس قلبها صغير <happy>
المقدم: مرحبا بكم فاطمة، كن سعداء بأن تكوني معنا <happy>''',
        
        'Con': '''المقدم: وما سلام، وما أحلى وما تعلمناه عن أطعمتنا العربية <happy>
الضيف: معا كن طبع قصة وذكريات
المقدم: صحيح، وازل نحافظ عليها وننقلها للأجيال الجديدة
الضيف: بالا شك تعليمكم كن مستمتعين بها <happy>
المقدم: وأنت كن عندك وصفة تحبين مشاركتها معنا مرة أخرى؟
الضيف: وممم، ربما الكبسة السعودية الشهيرة <smiling>
المقدم: أؤؤييد أؤيد، هذي فكرة عظيمة
الضيف: كيكن تكون حلوة ومستقبلية وثيرة
المقدم: وطعام، سأحب ذلك، شكرا جزيلا للوجود معنا اليوم
الضيف: أني شكر من أيضا، كان كنت رائع
المقدم: وانني هنديين، دائما استمتع بتعلم الجديد عن تراثنا الغني
الضيف: آآن إلى اللقاء في الحلقة القادمة بإذن الله
المقدم: حتى نلتقي ثانية، حافظوا على حب الطعام والتجربة والاستكشاف'''
    }
    
    print("🎙️ Starting full podcast audio generation...")
    print(f"Script sections: {list(script.keys())}")
    
    try:
        result = await getTTS(script)
        print(f"✅ SUCCESS! Audio file created: {result}")
        
        if result and os.path.exists(result):
            file_size = os.path.getsize(result) / (1024 * 1024)  # MB
            print(f"📊 File size: {file_size:.2f} MB")
            print(f"📂 File location: {result}")
        else:
            print("❌ File not found or path is None")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_script())
