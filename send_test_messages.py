
#!/usr/bin/env python3
"""
إرسال رسائل تجريبية باستخدام بوت الإرسال الجديد
"""

import asyncio
import aiohttp
from utils.logger import setup_logger

logger = setup_logger(__name__)

# بيانات البوت
SENDER_BOT_TOKEN = "7613162592:AAFnqn3_1lPPClVUa1jckOXj44C2MGCVLHs"
# قناة الأرشيف الوحيدة (هي القناة الرئيسية للمعالجة والأرشفة)
MAIN_PROCESSING_CHANNEL_ID = "-1002711636474"  # Real_estate Archive Channel

# الرسائل التجريبية
TEST_MESSAGES = [
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

async def send_test_message(session, text, message_num):
    """إرسال رسالة واحدة"""
    
    url = f"https://api.telegram.org/bot{SENDER_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": MAIN_PROCESSING_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                result = await response.json()
                if result.get("ok"):
                    logger.info(f"✅ تم إرسال الرسالة {message_num} بنجاح")
                    return True
                else:
                    logger.error(f"❌ خطأ في إرسال الرسالة {message_num}: {result.get('description')}")
            else:
                logger.error(f"❌ خطأ HTTP {response.status} في إرسال الرسالة {message_num}")
                
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال الرسالة {message_num}: {e}")
    
    return False

async def send_all_test_messages():
    """إرسال جميع الرسائل التجريبية"""
    
    logger.info("🚀 بدء إرسال الرسائل التجريبية...")
    logger.info(f"📱 البوت: {SENDER_BOT_TOKEN[:20]}...")
    logger.info(f"📢 القناة الرئيسية: {MAIN_PROCESSING_CHANNEL_ID}")
    logger.info("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        sent_count = 0
        
        for i, message in enumerate(TEST_MESSAGES, 1):
            logger.info(f"📤 إرسال الرسالة {i}/{len(TEST_MESSAGES)}...")
            
            success = await send_test_message(session, message, i)
            if success:
                sent_count += 1
            
            # توقف قصير بين الرسائل
            await asyncio.sleep(2)
        
        logger.info("=" * 50)
        logger.info(f"✅ تم إرسال {sent_count}/{len(TEST_MESSAGES)} رسالة بنجاح")
        
        if sent_count > 0:
            logger.info("🎉 يمكنك الآن فحص القناة الرئيسية لرؤية الرسائل")
            logger.info("🔄 النظام سيعالج هذه الرسائل ويأرشفها تلقائياً")

async def main():
    """الدالة الرئيسية"""
    print("📤 إرسال رسائل تجريبية إلى القناة الرئيسية للمعالجة")
    print("=" * 50)
    
    await send_all_test_messages()
    
    print("\nتم الانتهاء! 🎊")

if __name__ == "__main__":
    asyncio.run(main())
