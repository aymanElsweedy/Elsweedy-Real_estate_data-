
#!/usr/bin/env python3
"""
اختبار النظام المصلح - تجربة تدريجية للمكونات
"""

import asyncio
import os
from datetime import datetime
from config import Config
from services.telegram_service import TelegramService
from services.ai_service import AIService
from utils.logger import setup_logger

logger = setup_logger(__name__)

# رسالة اختبار بسيطة
SIMPLE_TEST_MESSAGE = """
🏠 شقة للإيجار

المنطقة: احياء تجمع
النوع: شقة
المساحة: 120 متر
الدور: الثاني
السعر: 25000 جنيه شهرياً
الحالة: مفروش

للتواصل: بلبل - 01234567890
المالك: احمد محمود - 01012345678
"""

async def test_fixed_system():
    """اختبار النظام المصلح تدريجياً"""
    
    print("🔧 اختبار النظام المصلح")
    print("=" * 50)
    
    # 1. فحص الإعدادات
    print("\n1️⃣ فحص الإعدادات...")
    config = Config()
    
    if not config.validate():
        print("❌ فشل في التحقق من الإعدادات")
        print("💡 تأكد من إضافة جميع المتغيرات في Secrets")
        return False
    
    print("✅ الإعدادات صحيحة")
    print(f"📱 Bot Token: {'✅' if config.TELEGRAM_BOT_TOKEN else '❌'}")
    print(f"📢 Channel ID: {'✅' if config.TELEGRAM_CHANNEL_ID else '❌'}")
    print(f"🤖 AI Providers: {len(config.get_available_ai_providers())}")
    
    # 2. اختبار الاتصال بالتليجرام
    print("\n2️⃣ اختبار خدمة التليجرام...")
    try:
        async with TelegramService(config) as telegram:
            # اختبار جلب الرسائل
            messages = await telegram.get_channel_messages(limit=5, apply_filter=False)
            print(f"✅ تم جلب {len(messages)} رسالة من القناة")
            
            # اختبار إرسال رسالة تجريبية بسيطة
            test_message = f"🧪 اختبار النظام\n\n⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}"
            success = await telegram.send_message_to_channel(test_message)
            
            if success:
                print("✅ تم إرسال رسالة الاختبار بنجاح")
            else:
                print("❌ فشل في إرسال رسالة الاختبار")
                return False
                
    except Exception as e:
        print(f"❌ خطأ في خدمة التليجرام: {e}")
        return False
    
    # 3. اختبار خدمة الذكاء الاصطناعي
    print("\n3️⃣ اختبار خدمة الذكاء الاصطناعي...")
    try:
        ai_service = AIService(config)
        
        print(f"🤖 مزودو AI المتاحون: {', '.join(config.get_available_ai_providers())}")
        
        # اختبار استخراج البيانات
        print("🔄 بدء استخراج البيانات...")
        extracted_data = await ai_service.extract_property_data(SIMPLE_TEST_MESSAGE)
        
        if extracted_data:
            print("✅ تم استخراج البيانات بنجاح")
            print(f"   🏘️ المنطقة: {extracted_data.get('المنطقة', 'غير محدد')}")
            print(f"   🏠 النوع: {extracted_data.get('نوع الوحدة', 'غير محدد')}")
            print(f"   📐 المساحة: {extracted_data.get('المساحة', 'غير محدد')}")
            print(f"   💰 السعر: {extracted_data.get('السعر', 'غير محدد')}")
            
            # التحقق من صحة البيانات
            is_valid, errors = await ai_service.validate_property_data(extracted_data)
            if is_valid:
                print("✅ البيانات صحيحة ومكتملة")
            else:
                print(f"⚠️ مشاكل في البيانات: {', '.join(errors[:3])}")
                
        else:
            print("❌ فشل في استخراج البيانات")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في خدمة الذكاء الاصطناعي: {e}")
        return False
    
    # 4. النتيجة النهائية
    print("\n" + "=" * 50)
    print("🎉 تم اختبار النظام بنجاح!")
    print("✅ جميع المكونات الأساسية تعمل")
    print("🚀 النظام جاهز لمعالجة الرسائل الفعلية")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_fixed_system())
