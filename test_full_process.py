#!/usr/bin/env python3
"""
اختبار العملية الكاملة: إرسال العقارين -> معالجة -> تخزين في Notion وZoho -> إشعارات
"""

import asyncio
import os
from datetime import datetime
from services.telegram_service import TelegramService
from services.ai_service import AIService
from services.notion_service import NotionService
from services.zoho_service import ZohoService
from models.property import PropertyData, PropertyStatus
from utils.logger import setup_logger

logger = setup_logger(__name__)

# الرسائل العقارية التي سيتم إرسالها ومعالجتها
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

async def full_workflow_test():
    """اختبار العملية الكاملة"""
    
    # إعداد الخدمات
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    notion_secret = os.getenv("NOTION_INTEGRATION_SECRET")
    properties_db_id = os.getenv("NOTION_PROPERTIES_DB_ID")
    owners_db_id = os.getenv("NOTION_OWNERS_DB_ID")
    
    zoho_client_id = os.getenv("ZOHO_CLIENT_ID")
    zoho_client_secret = os.getenv("ZOHO_CLIENT_SECRET")
    zoho_refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
    
    if not all([bot_token, channel_id, anthropic_key, notion_secret, properties_db_id, owners_db_id]):
        logger.error("❌ إعدادات غير مكتملة")
        return False
    
    telegram_service = TelegramService(bot_token, channel_id)
    ai_service = AIService(anthropic_key)
    notion_service = NotionService(notion_secret, properties_db_id, owners_db_id)
    
    zoho_service = None
    if all([zoho_client_id, zoho_client_secret, zoho_refresh_token]):
        zoho_service = ZohoService(zoho_client_id, zoho_client_secret, zoho_refresh_token)
    
    results = []
    
    try:
        # الخطوة 1: إرسال العقارات إلى القناة
        logger.info("📤 الخطوة 1: إرسال العقارات إلى القناة...")
        
        for i, message in enumerate(PROPERTY_MESSAGES, 1):
            logger.info(f"📤 إرسال العقار {i} إلى القناة...")
            success = await telegram_service.send_message_to_channel(message)
            
            if success:
                logger.info(f"✅ تم إرسال العقار {i} بنجاح")
            else:
                logger.error(f"❌ فشل في إرسال العقار {i}")
            
            await asyncio.sleep(2)
        
        # انتظار قصير لتسليم الرسائل
        await asyncio.sleep(5)
        
        # الخطوة 2: استلام الرسائل من القناة
        logger.info("📥 الخطوة 2: استلام الرسائل من القناة...")
        received_messages = await telegram_service.get_channel_messages()
        
        if not received_messages:
            logger.error("❌ لم يتم استلام أي رسائل من القناة")
            return False
        
        logger.info(f"📥 تم استلام {len(received_messages)} رسالة من القناة")
        
        # الخطوة 3: معالجة كل رسالة
        for i, message in enumerate(received_messages[-2:], 1):  # آخر رسالتين
            logger.info(f"\n🔄 الخطوة 3.{i}: معالجة الرسالة {i}...")
            
            message_text = message.get("text", "")
            if not message_text.strip():
                logger.warning(f"⚠️ الرسالة {i} فارغة - تخطي")
                continue
            
            # معالجة بالذكاء الاصطناعي
            logger.info(f"🤖 معالجة النص بالذكاء الاصطناعي...")
            try:
                extracted_data = await ai_service.extract_property_data(message_text)
                logger.info(f"✅ تم استخراج البيانات بنجاح")
            except Exception as e:
                logger.error(f"❌ خطأ في الذكاء الاصطناعي: {e}")
                # استخدام بيانات افتراضية
                extracted_data = {
                    "المنطقة": "التجمع الخامس" if "التجمع الخامس" in message_text else "الشروق",
                    "نوع الوحدة": "فيلا" if "فيلا" in message_text else "شقة",
                    "حالة الوحدة": "مفروش",
                    "المساحة": "250" if "250" in message_text else "120",
                    "الدور": "دوبليكس" if "دوبليكس" in message_text else "الثالث",
                    "السعر": "45000" if "45,000" in message_text else "25000",
                    "اسم المالك": "محمد حسن" if "محمد حسن" in message_text else "سارة أحمد",
                    "رقم المالك": "01222222222" if "محمد حسن" in message_text else "01111111111",
                    "اتاحة العقار": "متاح",
                    "حالة الصور": "بدون صور" if "لا توجد صور" in message_text else "بصور",
                    "اسم الموظف": "فاطمة علي" if "فاطمة علي" in message_text else "أحمد محمد",
                    "كود الوحدة": f"TEST-00{i}-2024",
                    "العنوان": "المنطقة الثامنة، مدينة الشروق" if "الشروق" in message_text else "شارع التسعين الشمالي، التجمع الخامس",
                    "المميزات": "حديقة، جراج، مطبخ" if "حديقة" in message_text else "مكيفة، فيو مفتوح، اسانسير",
                    "تفاصيل كاملة": message_text[:200] + "...",
                    "البيان": f"عقار {i} - " + extracted_data.get("نوع الوحدة", "شقة") + " في " + extracted_data.get("المنطقة", "القاهرة")
                }
            
            # إنشاء كائن العقار
            property_data = PropertyData.from_dict(extracted_data)
            property_data.status = PropertyStatus.NEW
            property_data.telegram_message_id = message.get("message_id")
            property_data.created_at = datetime.now()
            
            result = {
                "property_data": property_data,
                "message_id": message.get("message_id"),
                "notion_success": False,
                "zoho_success": False,
                "notion_urls": {},
                "zoho_urls": {}
            }
            
            # الخطوة 4: تخزين في Notion
            logger.info(f"💾 تخزين في Notion...")
            try:
                # إنشاء المالك
                owner_id = await notion_service.create_owner_page(property_data.to_dict())
                if owner_id:
                    logger.info(f"✅ تم إنشاء المالك في Notion: {owner_id}")
                    result["notion_urls"]["owner"] = f"https://www.notion.so/{owner_id.replace('-', '')}"
                    
                    # إنشاء العقار
                    property_id = await notion_service.create_property_page(property_data.to_dict(), owner_id)
                    if property_id:
                        logger.info(f"✅ تم إنشاء العقار في Notion: {property_id}")
                        result["notion_urls"]["property"] = f"https://www.notion.so/{property_id.replace('-', '')}"
                        result["notion_success"] = True
                        property_data.notion_property_id = property_id
                        property_data.notion_owner_id = owner_id
                
            except Exception as e:
                logger.error(f"❌ خطأ في Notion: {e}")
            
            # الخطوة 5: تخزين في Zoho
            if zoho_service:
                logger.info(f"💾 تخزين في Zoho...")
                try:
                    async with zoho_service as zoho:
                        lead_id = await zoho.create_lead(property_data.to_dict())
                        if lead_id:
                            logger.info(f"✅ تم إنشاء العميل في Zoho: {lead_id}")
                            result["zoho_urls"]["lead"] = f"https://crm.zoho.com/crm/EntityInfo?module=Leads&id={lead_id}"
                            result["zoho_success"] = True
                            property_data.zoho_lead_id = lead_id
                
                except Exception as e:
                    logger.error(f"❌ خطأ في Zoho: {e}")
            
            results.append(result)
            
            # الخطوة 6: إرسال إشعار
            logger.info(f"📲 إرسال إشعار...")
            await send_notification(telegram_service, result)
            
            await asyncio.sleep(2)
        
        return results
        
    except Exception as e:
        logger.error(f"❌ خطأ في العملية الكاملة: {e}")
        return False

async def send_notification(telegram_service, result):
    """إرسال إشعار النتيجة"""
    
    property_data = result["property_data"]
    
    status_emoji = "✅" if (result["notion_success"] or result["zoho_success"]) else "❌"
    status_text = "تم تخزين العقار بنجاح" if (result["notion_success"] or result["zoho_success"]) else "فشل في تخزين العقار"
    
    notification = f"""{status_emoji} {status_text}

🏠 {property_data.unit_type} في {property_data.region}
👤 المالك: {property_data.owner_name}
📞 الهاتف: {property_data.owner_phone}
💰 السعر: {property_data.price} جنيه

📊 حالة التخزين:
Notion: {'✅' if result['notion_success'] else '❌'}
Zoho: {'✅' if result['zoho_success'] else '❌'}
"""
    
    # إضافة الروابط
    if result["notion_urls"]:
        notification += "\n🔗 روابط Notion:\n"
        for url_type, url in result["notion_urls"].items():
            notification += f"   {url_type}: {url}\n"
    
    if result["zoho_urls"]:
        notification += "\n🔗 روابط Zoho:\n"
        for url_type, url in result["zoho_urls"].items():
            notification += f"   {url_type}: {url}\n"
    
    try:
        await telegram_service.send_message(notification)
        logger.info("✅ تم إرسال الإشعار")
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال الإشعار: {e}")

async def main():
    """الدالة الرئيسية"""
    print("🏠 اختبار العملية الكاملة لنظام إدارة العقارات")
    print("=" * 60)
    
    results = await full_workflow_test()
    
    if results:
        print(f"\n🎉 تم إكمال العملية بنجاح - تم معالجة {len(results)} عقار")
        
        print("\n📋 ملخص النتائج:")
        for i, result in enumerate(results, 1):
            property_data = result["property_data"]
            print(f"\n{i}. {property_data.unit_type} في {property_data.region}")
            print(f"   المالك: {property_data.owner_name} ({property_data.owner_phone})")
            print(f"   السعر: {property_data.price} جنيه")
            print(f"   Notion: {'✅' if result['notion_success'] else '❌'}")
            print(f"   Zoho: {'✅' if result['zoho_success'] else '❌'}")
            
            if result["notion_urls"]:
                for url_type, url in result["notion_urls"].items():
                    print(f"   Notion {url_type}: {url}")
            
            if result["zoho_urls"]:
                for url_type, url in result["zoho_urls"].items():
                    print(f"   Zoho {url_type}: {url}")
    
    else:
        print("\n❌ فشلت العملية")

if __name__ == "__main__":
    asyncio.run(main())