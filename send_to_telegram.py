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

# الرسائل العقارية التي سيتم إرسالها
PROPERTY_MESSAGES = [
    """
🏠 عقار للإيجار - التجمع الخامس

📍 المنطقة: التجمع الخامس، القاهرة الجديدة
🏢 النوع: شقة سكنية
📐 المساحة: 120 متر مربع
🏗️ الدور: الثالث
💰 السعر: 25,000 جنيه شهرياً
🛋️ الحالة: مفروشة بالكامل

المميزات:
✅ مكيفة
✅ فيو مفتوح
✅ اسانسير
✅ موقف سيارة

📞 للتواصل: أحمد محمد - 01234567890
👤 المالك: سارة أحمد - 01111111111
📸 متوفر صور للوحدة

كود الوحدة: TEST-001-2024
العنوان: شارع التسعين الشمالي، التجمع الخامس، القاهرة الجديدة
    """,
    """
🏡 فيلا مميزة للإيجار - الشروق

📍 المنطقة: المنطقة الثامنة، مدينة الشروق
🏢 النوع: فيلا دوبليكس
📐 المساحة: 250 متر مربع
🏗️ الأدوار: دور أرضي + أول
💰 السعر: 45,000 جنيه شهرياً
🛋️ الحالة: غير مفروشة

المميزات:
🌳 حديقة خاصة
🚗 جراج للسيارات
🍳 مطبخ جاهز
🚿 3 حمامات
🏠 غرف واسعة

📞 للتواصل: فاطمة علي - 01987654321
👤 المالك: محمد حسن - 01222222222
📸 لا توجد صور حالياً

كود الوحدة: TEST-002-2024
العنوان: المنطقة الثامنة، مدينة الشروق
    """
]

async def send_properties_to_channel():
    """إرسال العقارات التجريبية إلى قناة التليجرام"""
    
    config = Config()
    
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("❌ لم يتم العثور على TELEGRAM_BOT_TOKEN")
        return False
    
    if not config.TELEGRAM_CHANNEL_ID:
        logger.error("❌ لم يتم العثور على TELEGRAM_CHANNEL_ID")
        return False
    
    try:
        async with TelegramService(config) as telegram_service:
        
        logger.info("📤 بدء إرسال العقارات التجريبية إلى القناة...")
            
            sent_messages = []
            for i, message in enumerate(PROPERTY_MESSAGES, 1):
                logger.info(f"📤 إرسال العقار {i} إلى القناة...")
                
                # إرسال الرسالة إلى القناة
                success = await telegram_service.send_message_to_channel(message)
                
                if success:
                    logger.info(f"✅ تم إرسال العقار {i} بنجاح")
                    sent_messages.append(message)
                else:
                    logger.error(f"❌ فشل في إرسال العقار {i}")
                
                # توقف قصير بين الرسائل
                await asyncio.sleep(3)
        
        logger.info(f"✅ تم إرسال {len(sent_messages)} عقار إلى القناة")
        
        # انتظار لمعالجة الرسائل
        logger.info("⏳ انتظار معالجة الرسائل...")
        await asyncio.sleep(10)
        
        # فحص الرسائل المستلمة
        logger.info("🔍 فحص الرسائل المستلمة من القناة...")
        received_messages = await telegram_service.get_channel_messages()
        
        if received_messages:
            logger.info(f"📥 تم استلام {len(received_messages)} رسالة من القناة")
            for i, msg in enumerate(received_messages[-2:], 1):  # آخر رسالتين
                logger.info(f"📩 الرسالة {i}: معرف {msg.get('message_id', 'غير معروف')}")
        else:
            logger.warning("⚠️ لم يتم استلام أي رسائل من القناة")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال العقارات: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    print("🏠 إرسال العقارين إلى قناة التليجرام")
    print("=" * 50)
    
    success = await send_properties_to_channel()
    
    if success:
        print("\n✅ تم إرسال العقارات بنجاح!")
        print("الآن يمكن للنظام فحص هذه الرسائل ومعالجتها تلقائياً")
    else:
        print("\n❌ فشل في إرسال العقارات")

if __name__ == "__main__":
    asyncio.run(main())