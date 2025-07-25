
"""
خدمات تجريبية للنظام - Demo Services
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import random
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DemoTelegramService:
    """خدمة تيليجرام تجريبية"""
    
    def __init__(self, config):
        self.config = config
        self.session = None
        self.demo_messages = [
            {
                "message_id": 1001,
                "text": """🏠 عقار للإيجار - التجمع الخامس

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
متاح""",
                "date": datetime.now(),
                "chat_id": "-1002711636474",
                "entities": [],
                "reply_markup": {},
                "raw_data": {}
            },
            {
                "message_id": 1002,
                "text": """🏡 فيلا للإيجار - الشروق

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
غير متاح""",
                "date": datetime.now(),
                "chat_id": "-1002711636474",
                "entities": [],
                "reply_markup": {},
                "raw_data": {}
            },
            {
                "message_id": 1003,
                "text": """🏢 شقة تمليك - جاردينيا هايتس

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
متاح""",
                "date": datetime.now(),
                "chat_id": "-1002711636474",
                "entities": [],
                "reply_markup": {},
                "raw_data": {}
            }
        ]
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_channel_messages(self, limit: int = 100, apply_filter: bool = True) -> List[Dict[str, Any]]:
        """محاكاة الحصول على رسائل القناة"""
        logger.info(f"📥 محاكاة جلب {len(self.demo_messages)} رسالة تجريبية من القناة")
        await asyncio.sleep(1)  # محاكاة وقت الشبكة
        return self.demo_messages
    
    async def send_message_to_channel(self, text: str, parse_mode: str = "HTML") -> bool:
        """محاكاة إرسال رسالة إلى القناة"""
        logger.info("✅ تم إرسال رسالة تجريبية إلى القناة")
        await asyncio.sleep(0.5)
        return True
    
    async def send_notification(self, text: str, parse_mode: str = "HTML") -> bool:
        """محاكاة إرسال إشعار"""
        logger.info("✅ تم إرسال إشعار تجريبي")
        await asyncio.sleep(0.5)
        return True
    
    async def delete_message(self, message_id: int) -> bool:
        """محاكاة حذف رسالة"""
        logger.info(f"✅ تم حذف الرسالة التجريبية {message_id}")
        await asyncio.sleep(0.3)
        return True
    
    async def edit_message(self, message_id: int, new_text: str, parse_mode: str = "HTML") -> bool:
        """محاكاة تعديل رسالة"""
        logger.info(f"✅ تم تعديل الرسالة التجريبية {message_id}")
        await asyncio.sleep(0.3)
        return True
    
    async def send_to_archive(self, text: str, original_message_id: int) -> bool:
        """محاكاة الأرشفة"""
        logger.info(f"✅ تم أرشفة الرسالة التجريبية {original_message_id}")
        await asyncio.sleep(0.3)
        return True
    
    def format_property_notification(self, property_data: Dict[str, Any], 
                                   classification: str, 
                                   similar_property_link: str = None) -> str:
        """تنسيق إشعار العقار"""
        return f"🏠 إشعار تجريبي: {classification} - {property_data.get('المنطقة', 'غير محدد')}"
    
    def format_success_message(self, property_data: Dict[str, Any]) -> str:
        """تنسيق رسالة نجاح"""
        return f"✅ عقار ناجح تجريبي: {property_data.get('المنطقة', 'غير محدد')}"
    
    def format_failed_message(self, property_data: Dict[str, Any]) -> str:
        """تنسيق رسالة فشل"""
        return f"❌ عقار فاشل تجريبي: {property_data.get('المنطقة', 'غير محدد')}"

class DemoAIService:
    """خدمة ذكاء اصطناعي تجريبية"""
    
    def __init__(self, config):
        self.config = config
    
    async def extract_property_data(self, raw_text: str) -> Dict[str, Any]:
        """محاكاة استخراج بيانات العقار"""
        logger.info("🤖 محاكاة استخراج البيانات بالذكاء الاصطناعي...")
        await asyncio.sleep(2)  # محاكاة وقت المعالجة
        
        # استخراج تجريبي بسيط
        extracted_data = {
            "المنطقة": "احياء تجمع",
            "كود الوحدة": f"DEMO-{random.randint(1000, 9999)}",
            "نوع الوحدة": "شقة",
            "حالة الوحدة": "مفروش",
            "المساحة": "120",
            "الدور": "الثالث",
            "السعر": "25000",
            "المميزات": "مكيفه، فيو مفتوح، اسانسير",
            "العنوان": "التجمع الخامس، القاهرة الجديدة",
            "اسم الموظف": "بلبل",
            "اسم المالك": "سارة أحمد",
            "رقم المالك": "01111111111",
            "اتاحة العقار": "متاح",
            "حالة الصور": "متوفر صور",
            "تفاصيل كاملة": raw_text,
            "البيان": f"[المنطقة: احياء تجمع] | [نوع الوحدة: شقة] | [المساحة: 120] | [السعر: 25000] | [المالك: سارة أحمد] | [الهاتف: 01111111111]"
        }
        
        # استخراج ديناميكي من النص
        if "فيلا" in raw_text:
            extracted_data["نوع الوحدة"] = "فيلا"
        if "اندلس" in raw_text:
            extracted_data["المنطقة"] = "اندلس"
        if "جاردينيا" in raw_text:
            extracted_data["المنطقة"] = "جاردينيا هايتس"
        
        # استخراج الأسعار
        import re
        price_match = re.search(r'(\d+)\s*جنيه', raw_text)
        if price_match:
            extracted_data["السعر"] = price_match.group(1)
        
        # استخراج أسماء الموظفين
        for employee in self.config.APPROVED_EMPLOYEES:
            if employee in raw_text:
                extracted_data["اسم الموظف"] = employee
                break
        
        logger.info("✅ تم استخراج البيانات التجريبية بنجاح")
        return extracted_data
    
    async def validate_property_data(self, property_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """محاكاة التحقق من صحة البيانات"""
        logger.info("🔍 محاكاة التحقق من صحة البيانات...")
        await asyncio.sleep(1)
        
        errors = []
        
        # تحقق تجريبي
        if not property_data.get("المنطقة"):
            errors.append("المنطقة مفقودة")
        if not property_data.get("السعر") or property_data.get("السعر") == "0":
            errors.append("السعر غير صحيح")
        if not property_data.get("رقم المالك"):
            errors.append("رقم المالك مفقود")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("✅ البيانات التجريبية صحيحة")
        else:
            logger.warning(f"⚠️ مشاكل في البيانات: {', '.join(errors)}")
        
        return is_valid, errors

class DemoNotionService:
    """خدمة Notion تجريبية"""
    
    def __init__(self, integration_secret: str, properties_db_id: str, owners_db_id: str):
        self.integration_secret = integration_secret
        self.properties_db_id = properties_db_id
        self.owners_db_id = owners_db_id
        self.demo_properties = []
        self.demo_owners = []
    
    async def search_property(self, property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """محاكاة البحث عن عقار"""
        logger.info("🔍 محاكاة البحث في قاعدة بيانات Notion...")
        await asyncio.sleep(1)
        
        # محاكاة عدم وجود عقار مكرر
        return None
    
    async def search_owner(self, owner_phone: str) -> Optional[Dict[str, Any]]:
        """محاكاة البحث عن مالك"""
        logger.info(f"🔍 محاكاة البحث عن المالك: {owner_phone}")
        await asyncio.sleep(0.5)
        
        # محاكاة وجود مالك أحياناً
        if len(self.demo_owners) > 0 and random.choice([True, False]):
            return self.demo_owners[0]
        return None
    
    async def create_property_page(self, property_data: Dict[str, Any], owner_id: str = None) -> Optional[str]:
        """محاكاة إنشاء صفحة عقار"""
        logger.info("📝 محاكاة إنشاء صفحة عقار في Notion...")
        await asyncio.sleep(1.5)
        
        page_id = f"demo-property-{random.randint(1000, 9999)}"
        self.demo_properties.append({"id": page_id, "data": property_data})
        
        logger.info(f"✅ تم إنشاء صفحة العقار التجريبية: {page_id}")
        return page_id
    
    async def create_owner_page(self, property_data: Dict[str, Any]) -> Optional[str]:
        """محاكاة إنشاء صفحة مالك"""
        logger.info("👤 محاكاة إنشاء صفحة مالك في Notion...")
        await asyncio.sleep(1)
        
        owner_id = f"demo-owner-{random.randint(1000, 9999)}"
        self.demo_owners.append({"id": owner_id, "phone": property_data.get("رقم المالك")})
        
        logger.info(f"✅ تم إنشاء صفحة المالك التجريبية: {owner_id}")
        return owner_id
    
    async def find_duplicate_properties(self, owner_phone: str, region: str, unit_type: str, 
                                      unit_condition: str, area: str, floor: str) -> List[Dict[str, Any]]:
        """محاكاة البحث عن عقارات مكررة"""
        logger.info("🔄 محاكاة البحث عن عقارات مكررة...")
        await asyncio.sleep(0.8)
        
        # محاكاة عدم وجود تكرار عادة
        return []
    
    async def find_owner_properties(self, owner_phone: str) -> List[Dict[str, Any]]:
        """محاكاة البحث عن عقارات المالك"""
        logger.info(f"🏠 محاكاة البحث عن عقارات المالك: {owner_phone}")
        await asyncio.sleep(0.5)
        
        # محاكاة وجود عقارات أخرى أحياناً
        if random.choice([True, False, False]):  # 33% احتمال
            return [{"id": "demo-existing-property", "owner_phone": owner_phone}]
        return []
    
    def get_property_url(self, page_id: str) -> str:
        """الحصول على رابط صفحة العقار"""
        clean_id = page_id.replace("-", "")
        return f"https://www.notion.so/{clean_id}"

class DemoZohoService:
    """خدمة Zoho تجريبية"""
    
    def __init__(self, client_id: str, client_secret: str, refresh_token: str, 
                 access_token: str, module_name: str = "Aqar"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.module_name = module_name
        self.demo_records = []
    
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def refresh_access_token(self) -> bool:
        """محاكاة تحديث access token"""
        logger.info("🔄 محاكاة تحديث Zoho access token...")
        await asyncio.sleep(0.5)
        logger.info("✅ تم تحديث التوكن التجريبي")
        return True
    
    async def create_record(self, property_data: Dict[str, Any]) -> Optional[str]:
        """محاكاة إنشاء سجل في Zoho"""
        logger.info("📊 محاكاة إنشاء سجل في Zoho CRM...")
        await asyncio.sleep(1.2)
        
        record_id = f"demo-zoho-{random.randint(10000, 99999)}"
        self.demo_records.append({"id": record_id, "data": property_data})
        
        logger.info(f"✅ تم إنشاء السجل التجريبي في Zoho: {record_id}")
        return record_id
    
    async def search_record(self, field_name: str, field_value: str) -> Optional[Dict[str, Any]]:
        """محاكاة البحث عن سجل"""
        logger.info(f"🔍 محاكاة البحث في Zoho: {field_name} = {field_value}")
        await asyncio.sleep(0.8)
        
        # محاكاة عدم وجود سجل مطابق عادة
        return None
    
    def get_lead_url(self, record_id: str) -> str:
        """الحصول على رابط السجل"""
        return f"https://crm.zoho.com/crm/org123/tab/Aqar/{record_id}"
