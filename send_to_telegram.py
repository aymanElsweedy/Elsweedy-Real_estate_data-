
#!/usr/bin/env python3
"""
إرسال عقارات تجريبية إلى قناة التليجرام لاختبار النظام المحدث
"""

import asyncio
import os
from config import Config
from services.telegram_service import TelegramService
from utils.logger import setup_logger

logger = setup_logger(__name__)

# الرسائل العقارية المحدثة وفقاً للدليل الجديد
PROPERTY_MESSAGES = [
    """
🏠 عقار للإيجار - التجمع الخامس

المنطقة: احياء تجمع
النوع: شقة سكنية
المساحة: 120 متر مربع
الدور: الثالث
السعر: 25000 جنيه شهرياً
الحالة: مفروش

المميزات:
- مكيفه
- فيو مفتوح  
- اسانسير
- حديقه

للتواصل: أحمد محمد - 01234567890
المالك: سارة أحمد - 01111111111
متوفر صور للوحدة

العنوان: شارع التسعين الشمالي، التجمع الخامس، القاهرة الجديدة
تبع بلبل
متاح
    """,
    """
🏡 فيلا دوبلكس للإيجار - الشروق

المنطقة: اندلس
النوع: فيلا دوبلكس  
المساحة: 250 متر مربع
الأدوار: دور أرضي + أول
السعر: 45000 جنيه شهرياً
الحالة: فاضي

المميزات:
- حديقه خاصة
- تشطيب سوبر لوكس
- مدخل خاص

للتواصل: فاطمة علي - 01987654321
المالك: محمد حسن - 01222222222
بدون صور حالياً

العنوان: المنطقة الثامنة، اندلس
تبع يوسف عماد
غير متاح
    """,
    """
🏢 شقة تمليك - جاردينيا هايتس

المنطقة: جاردينيا هايتس
النوع: شقة
المساحة: 180 متر
الدور: دور رابع
السعر: 1500000 جنيه
الحالة: تمليك

المميزات:
- مسجله شهر عقاري
- اسانسير
- فيو جاردن
- تقسيط

للتواصل: محمود سامي - 01555666777
المالك: أميرة خالد - 01333444555
بصور متاحة

العنوان: كمبوند جاردينيا هايتس، الحي الخامس
تبع محمود سامي
متاح
    """
]

async def send_properties_to_channel():
    """إرسال العقارات التجريبية إلى قناة التليجرام"""
    
    config = Config()
    
    # استخدام بوت الإرسال الجديد
    sender_bot_token = config.TELEGRAM_BOT_sender_TOKEN
    if not sender_bot_token:
        logger.error("❌ لم يتم العثور على TELEGRAM_BOT_sender_TOKEN")
        return False
    
    # استخدام القناة الرئيسية للمعالجة كوجهة للإرسال
    target_channel = config.TELEGRAM_CHANNEL_ID
    if not target_channel:
        logger.error("❌ لم يتم العثور على TELEGRAM_CHANNEL_ID")
        return False
    
    try:
        # إنشاء خدمة تليجرام مخصصة للإرسال
        sender_config = Config()
        sender_config.TELEGRAM_BOT_TOKEN = sender_bot_token
        sender_config.TELEGRAM_CHANNEL_ID = target_channel
        
        async with TelegramService(sender_config) as telegram_service:
            logger.info(f"📤 بدء إرسال العقارات التجريبية إلى القناة {target_channel}...")
            
            sent_messages = []
            for i, message in enumerate(PROPERTY_MESSAGES, 1):
                logger.info(f"📤 إرسال العقار {i}/{len(PROPERTY_MESSAGES)} إلى القناة...")
                
                # إرسال الرسالة إلى القناة الرئيسية للمعالجة
                success = await telegram_service.send_message_to_channel(message)
                
                if success:
                    logger.info(f"✅ تم إرسال العقار {i} بنجاح إلى القناة الرئيسية")
                    sent_messages.append(message)
                else:
                    logger.error(f"❌ فشل في إرسال العقار {i}")
                
                # توقف قصير بين الرسائل
                await asyncio.sleep(3)
        
        logger.info(f"✅ تم إرسال {len(sent_messages)} عقار إلى القناة")
        
        # انتظار لمعالجة الرسائل
        logger.info("⏳ انتظار معالجة الرسائل...")
        await asyncio.sleep(10)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال العقارات: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    print("🏠 إرسال العقارات التجريبية إلى قناة التليجرام")
    print("=" * 50)
    
    success = await send_properties_to_channel()
    
    if success:
        print("\n✅ تم إرسال العقارات بنجاح!")
        print("الآن يمكن تشغيل النظام لمعالجة هذه الرسائل:")
        print("   python test_full_system.py  # للاختبار")
        print("   python main.py             # للتشغيل الكامل")
    else:
        print("\n❌ فشل في إرسال العقارات")

if __name__ == "__main__":
    asyncio.run(main())
