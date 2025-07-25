#!/usr/bin/env python3
"""
سكريبت تجريبي للعملية الكاملة:
1. استقبال رسالتين عقاريتين من التليجرام
2. معالجتهما بالذكاء الاصطناعي
3. تخزينهما في Notion وZoho
4. إرسال إشعارات للبوت
"""

import asyncio
import os
import json
from datetime import datetime
from typing import List

from models.property import PropertyData, PropertyStatus
from services.ai_service import AIService
from services.notion_service import NotionService
from services.zoho_service import ZohoService
from services.telegram_service import TelegramService
from processors.property_processor import PropertyProcessor
from utils.logger import setup_logger

logger = setup_logger(__name__)

# رسائل عقارية تجريبية (محاكاة رسائل التليجرام)
SAMPLE_MESSAGES = [
    {
        "message_id": 1001,
        "text": """
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
        """,
        "timestamp": datetime.now().isoformat()
    },
    {
        "message_id": 1002,
        "text": """
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
        """,
        "timestamp": datetime.now().isoformat()
    }
]

class FullWorkflowTester:
    """فئة لاختبار العملية الكاملة"""
    
    def __init__(self):
        self.ai_service = None
        self.notion_service = None
        self.zoho_service = None
        self.telegram_service = None
        self.property_processor = None
        
    async def setup_services(self):
        """إعداد الخدمات المطلوبة"""
        logger.info("🔧 إعداد الخدمات...")
        
        # خدمة الذكاء الاصطناعي
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.ai_service = AIService(anthropic_key)
            logger.info("✅ تم إعداد خدمة الذكاء الاصطناعي")
        else:
            logger.warning("⚠️ لم يتم العثور على ANTHROPIC_API_KEY")
        
        # خدمة Notion
        notion_secret = os.getenv("NOTION_INTEGRATION_SECRET")
        properties_db_id = os.getenv("NOTION_PROPERTIES_DB_ID", os.getenv("NOTION_DATABASE_ID"))
        owners_db_id = os.getenv("NOTION_OWNERS_DB_ID", os.getenv("NOTION_DATABASE_ID"))
        
        if notion_secret and properties_db_id:
            self.notion_service = NotionService(notion_secret, properties_db_id, owners_db_id or properties_db_id)
            logger.info("✅ تم إعداد خدمة Notion")
        else:
            logger.warning("⚠️ لم يتم العثور على إعدادات Notion")
        
        # خدمة Zoho
        zoho_client_id = os.getenv("ZOHO_CLIENT_ID")
        zoho_client_secret = os.getenv("ZOHO_CLIENT_SECRET")
        zoho_refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
        
        if all([zoho_client_id, zoho_client_secret, zoho_refresh_token]):
            self.zoho_service = ZohoService(zoho_client_id, zoho_client_secret, zoho_refresh_token)
            logger.info("✅ تم إعداد خدمة Zoho")
        else:
            logger.warning("⚠️ لم يتم العثور على إعدادات Zoho")
        
        # خدمة التليجرام
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
        
        if telegram_token:
            self.telegram_service = TelegramService(telegram_token, channel_id)
            logger.info("✅ تم إعداد خدمة التليجرام")
        else:
            logger.warning("⚠️ لم يتم العثور على TELEGRAM_BOT_TOKEN")
        
        # معالج العقارات
        if self.ai_service and self.notion_service:
            self.property_processor = PropertyProcessor(
                self.ai_service,
                self.notion_service,
                self.zoho_service,
                self.telegram_service
            )
            logger.info("✅ تم إعداد معالج العقارات")
    
    async def simulate_telegram_messages(self) -> List[dict]:
        """محاكاة استقبال رسائل من التليجرام"""
        logger.info("📱 محاكاة استقبال رسائل التليجرام...")
        
        received_messages = []
        for i, message in enumerate(SAMPLE_MESSAGES, 1):
            logger.info(f"📩 استقبال الرسالة {i}: معرف {message['message_id']}")
            received_messages.append(message)
            await asyncio.sleep(0.5)  # محاكاة وقت الاستقبال
        
        logger.info(f"✅ تم استقبال {len(received_messages)} رسالة")
        return received_messages
    
    async def process_message_with_ai(self, message_text: str) -> dict:
        """معالجة رسالة بالذكاء الاصطناعي"""
        if not self.ai_service:
            logger.warning("⚠️ خدمة الذكاء الاصطناعي غير متوفرة - سيتم استخدام بيانات افتراضية")
            return self.extract_fallback_data(message_text)
        
        try:
            logger.info("🤖 معالجة النص بالذكاء الاصطناعي...")
            extracted_data = await self.ai_service.extract_property_data(message_text)
            logger.info("✅ تم استخراج البيانات بنجاح")
            return extracted_data
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الذكاء الاصطناعي: {e}")
            return self.extract_fallback_data(message_text)
    
    def extract_fallback_data(self, message_text: str) -> dict:
        """استخراج بيانات افتراضية من النص"""
        # استخراج بسيط بدون AI
        data = {
            "المنطقة": "غير محدد",
            "نوع الوحدة": "شقة",
            "حالة الوحدة": "غير محدد",
            "المساحة": "0",
            "الدور": "غير محدد",
            "السعر": "0",
            "اسم المالك": "غير محدد",
            "رقم المالك": "غير محدد",
            "اتاحة العقار": "متاح",
            "حالة الصور": "غير محدد"
        }
        
        # بحث بسيط في النص
        if "التجمع الخامس" in message_text:
            data["المنطقة"] = "التجمع الخامس"
        elif "الشروق" in message_text:
            data["المنطقة"] = "الشروق"
        
        if "فيلا" in message_text:
            data["نوع الوحدة"] = "فيلا"
        
        # استخراج الرقم من النص
        import re
        price_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*جنيه', message_text)
        if price_match:
            data["السعر"] = price_match.group(1).replace(',', '')
        
        return data
    
    async def store_property_data(self, property_data: PropertyData) -> dict:
        """تخزين بيانات العقار في Notion وZoho"""
        results = {
            "notion_success": False,
            "zoho_success": False,
            "notion_urls": {},
            "zoho_urls": {}
        }
        
        # تخزين في Notion
        if self.notion_service:
            try:
                logger.info("💾 تخزين البيانات في Notion...")
                
                # إنشاء صفحة المالك
                owner_id = await self.notion_service.create_owner_page(property_data.to_dict())
                if owner_id:
                    property_data.notion_owner_id = owner_id
                    results["notion_urls"]["owner"] = self.notion_service.get_owner_url(owner_id)
                
                # إنشاء صفحة العقار
                property_id = await self.notion_service.create_property_page(
                    property_data.to_dict(), owner_id
                )
                if property_id:
                    property_data.notion_property_id = property_id
                    results["notion_urls"]["property"] = self.notion_service.get_property_url(property_id)
                    results["notion_success"] = True
                
                logger.info("✅ تم تخزين البيانات في Notion")
                
            except Exception as e:
                logger.error(f"❌ خطأ في تخزين Notion: {e}")
        
        # تخزين في Zoho
        if self.zoho_service:
            try:
                logger.info("💾 تخزين البيانات في Zoho...")
                
                async with self.zoho_service as zoho:
                    lead_id = await zoho.create_lead(property_data.to_dict())
                    if lead_id:
                        property_data.zoho_lead_id = lead_id
                        results["zoho_urls"]["lead"] = zoho.get_lead_url(lead_id)
                        results["zoho_success"] = True
                
                logger.info("✅ تم تخزين البيانات في Zoho")
                
            except Exception as e:
                logger.error(f"❌ خطأ في تخزين Zoho: {e}")
        
        return results
    
    async def send_notification(self, property_data: PropertyData, storage_results: dict):
        """إرسال إشعار للبوت"""
        if not self.telegram_service:
            logger.warning("⚠️ خدمة التليجرام غير متوفرة - سيتم طباعة الإشعار")
            self.print_notification(property_data, storage_results)
            return
        
        try:
            logger.info("📲 إرسال إشعار التليجرام...")
            
            # تحديد نوع الإشعار
            if storage_results["notion_success"] or storage_results["zoho_success"]:
                status = "تم تخزين العقار بنجاح"
                emoji = "✅"
            else:
                status = "فشل في تخزين العقار"
                emoji = "❌"
            
            # تكوين رسالة الإشعار
            notification_text = f"""{emoji} {status}

🏠 {property_data.unit_type} في {property_data.region}
👤 المالك: {property_data.owner_name}
📞 الهاتف: {property_data.owner_phone}
💰 السعر: {property_data.price} جنيه

📊 حالة التخزين:
Notion: {'✅' if storage_results['notion_success'] else '❌'}
Zoho: {'✅' if storage_results['zoho_success'] else '❌'}
"""
            
            # إضافة الروابط
            if storage_results["notion_urls"]:
                notification_text += "\n🔗 روابط Notion:\n"
                for url_type, url in storage_results["notion_urls"].items():
                    notification_text += f"   {url_type}: {url}\n"
            
            if storage_results["zoho_urls"]:
                notification_text += "\n🔗 روابط Zoho:\n"
                for url_type, url in storage_results["zoho_urls"].items():
                    notification_text += f"   {url_type}: {url}\n"
            
            # إرسال الإشعار
            await self.telegram_service.send_notification(notification_text)
            logger.info("✅ تم إرسال الإشعار")
            
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال الإشعار: {e}")
            self.print_notification(property_data, storage_results)
    
    def print_notification(self, property_data: PropertyData, storage_results: dict):
        """طباعة الإشعار في وحدة التحكم"""
        print("\n" + "="*50)
        print("📲 إشعار العقار:")
        print(f"🏠 {property_data.unit_type} في {property_data.region}")
        print(f"👤 المالك: {property_data.owner_name} ({property_data.owner_phone})")
        print(f"💰 السعر: {property_data.price} جنيه")
        print(f"📊 Notion: {'✅ نجح' if storage_results['notion_success'] else '❌ فشل'}")
        print(f"📊 Zoho: {'✅ نجح' if storage_results['zoho_success'] else '❌ فشل'}")
        
        if storage_results.get("notion_urls"):
            print("🔗 روابط Notion:")
            for url_type, url in storage_results["notion_urls"].items():
                print(f"   {url_type}: {url}")
        
        if storage_results.get("zoho_urls"):
            print("🔗 روابط Zoho:")
            for url_type, url in storage_results["zoho_urls"].items():
                print(f"   {url_type}: {url}")
        
        print("="*50)
    
    async def run_full_workflow(self):
        """تشغيل العملية الكاملة"""
        logger.info("🚀 بدء العملية الكاملة...")
        
        # إعداد الخدمات
        await self.setup_services()
        
        # محاكاة استقبال الرسائل
        messages = await self.simulate_telegram_messages()
        
        # معالجة كل رسالة
        for i, message in enumerate(messages, 1):
            logger.info(f"\n🔄 معالجة الرسالة {i}/{len(messages)}")
            
            # استخراج البيانات بالذكاء الاصطناعي
            extracted_data = await self.process_message_with_ai(message["text"])
            
            # إنشاء كائن العقار
            property_data = PropertyData.from_dict(extracted_data)
            property_data.status = PropertyStatus.NEW
            property_data.telegram_message_id = message["message_id"]
            property_data.created_at = datetime.now()
            
            logger.info(f"📋 تم إنشاء بيانات العقار: {property_data.region} - {property_data.unit_type}")
            
            # تخزين البيانات
            storage_results = await self.store_property_data(property_data)
            
            # إرسال الإشعار
            await self.send_notification(property_data, storage_results)
            
            # توقف قصير بين العقارات
            await asyncio.sleep(2)
        
        logger.info(f"🎉 تم إكمال معالجة {len(messages)} رسالة بنجاح!")

async def main():
    """الدالة الرئيسية"""
    print("🏠 اختبار العملية الكاملة لنظام إدارة العقارات")
    print("=" * 60)
    
    tester = FullWorkflowTester()
    await tester.run_full_workflow()
    
    print("\n" + "=" * 60)
    print("✅ تم إكمال الاختبار الكامل")

if __name__ == "__main__":
    asyncio.run(main())