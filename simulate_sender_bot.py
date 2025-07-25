
#!/usr/bin/env python3
"""
محاكي بوت الإرسال - يحاكي عمل @RealEstate_Sender_bot
يستقبل رسائل من الزملاء ويحولها للقناة الرئيسية
"""

import asyncio
import aiohttp
from utils.logger import setup_logger

logger = setup_logger(__name__)

# إعدادات البوت المُرسِل
SENDER_BOT_TOKEN = "7613162592:AAFnqn3_1lPPClVUa1jckOXj44C2MGCVLHs"
MAIN_CHANNEL_ID = "-1002394758962"  # القناة الرئيسية للمعالجة

# رسائل تجريبية من الزملاء
EMPLOYEE_MESSAGES = [
    """
    من: أحمد (موظف المبيعات)
    
    🏠 عقار جديد للإيجار
    المنطقة: التجمع الخامس - احياء تجمع
    النوع: شقة سكنية مفروشة
    المساحة: 120 متر
    الدور: الثالث
    السعر: 25000 جنيه شهرياً
    
    المميزات: مكيفة، فيو مفتوح، اسانسير، حديقة
    
    المالك: سارة أحمد
    التليفون: 01111111111
    العنوان: شارع التسعين الشمالي
    
    تبع بلبل
    متاح للمعاينة
    متوفر صور
    """,
    """
    من: فاطمة (موظفة التسويق)
    
    🏡 فيلا دوبلكس للإيجار
    المنطقة: الشروق - اندلس
    النوع: فيلا دوبلكس فاضي
    المساحة: 250 متر
    الأدوار: أرضي + أول
    السعر: 45000 جنيه شهرياً
    
    المميزات: حديقة خاصة، تشطيب سوبر لوكس، مدخل خاص
    
    المالك: محمد حسن
    التليفون: 01222222222
    العنوان: المنطقة الثامنة
    
    تبع يوسف عماد
    غير متاح حالياً
    بدون صور
    """,
    """
    من: محمود (مدير المبيعات)
    
    🏢 شقة تمليك مميزة
    المنطقة: جاردينيا هايتس
    النوع: شقة للبيع
    المساحة: 180 متر
    الدور: الرابع
    السعر: 1500000 جنيه
    
    المميزات: مسجلة شهر عقاري، اسانسير، فيو جاردن، تقسيط
    
    المالك: أميرة خالد
    التليفون: 01333444555
    العنوان: كمبوند جاردينيا هايتس
    
    تبع محمود سامي
    متاح للمعاينة
    متوفر صور
    """
]

async def send_employee_message(session, message, employee_num):
    """إرسال رسالة موظف واحد للقناة الرئيسية"""
    
    url = f"https://api.telegram.org/bot{SENDER_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": MAIN_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                result = await response.json()
                if result.get("ok"):
                    logger.info(f"✅ تم تحويل رسالة الموظف {employee_num} للقناة الرئيسية")
                    return True
                else:
                    logger.error(f"❌ خطأ في تحويل رسالة الموظف {employee_num}: {result.get('description')}")
            else:
                logger.error(f"❌ خطأ HTTP {response.status} في رسالة الموظف {employee_num}")
                
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال رسالة الموظف {employee_num}: {e}")
    
    return False

async def simulate_sender_bot():
    """محاكاة عمل البوت المُرسِل"""
    
    logger.info("🤖 بدء محاكاة عمل البوت المُرسِل...")
    logger.info(f"📱 البوت: @RealEstate_Sender_bot")
    logger.info(f"📢 القناة الرئيسية: {MAIN_CHANNEL_ID}")
    logger.info("🔄 تحويل رسائل الزملاء للقناة...")
    logger.info("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        sent_count = 0
        
        for i, message in enumerate(EMPLOYEE_MESSAGES, 1):
            logger.info(f"📤 تحويل رسالة من موظف {i}/{len(EMPLOYEE_MESSAGES)}...")
            
            success = await send_employee_message(session, message, i)
            if success:
                sent_count += 1
            
            # توقف بين الرسائل
            await asyncio.sleep(3)
        
        logger.info("=" * 50)
        logger.info(f"✅ تم تحويل {sent_count}/{len(EMPLOYEE_MESSAGES)} رسالة للقناة الرئيسية")
        
        if sent_count > 0:
            logger.info("🎯 الرسائل الآن في القناة الرئيسية جاهزة للمعالجة")
            logger.info("🔄 يمكن تشغيل النظام الآن لمعالجة هذه الرسائل")

async def main():
    """الدالة الرئيسية"""
    print("🤖 محاكي البوت المُرسِل")
    print("📱 @RealEstate_Sender_bot")
    print("🔄 تحويل رسائل الزملاء للقناة الرئيسية")
    print("=" * 50)
    
    await simulate_sender_bot()
    
    print("\n✅ انتهت المحاكاة!")
    print("💡 الآن يمكن تشغيل النظام الرئيسي لمعالجة الرسائل")

if __name__ == "__main__":
    asyncio.run(main())
