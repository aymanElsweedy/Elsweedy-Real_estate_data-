"""
خدمة Zoho CRM - Zoho CRM Service
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ZohoService:
    """خدمة التعامل مع Zoho CRM"""
    
    def __init__(self, client_id: str, client_secret: str, refresh_token: str, access_token: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.base_url = "https://www.zohoapis.com/crm/v2"
        self.token_url = "https://accounts.zoho.com/oauth/v2/token"
        self.session = None
        
        # خريطة حقول Zoho CRM
        self.field_map = {
            "البيان": "Name",
            "اتاحة العقار": "field12",
            "اسم الموظف": "field13",
            "نوع الوحدة": "field14", 
            "حالة الصور": "field11",
            "الدور": "field10",
            "المساحة": "field9",
            "حالة الوحدة": "field8",
            "المنطقة": "field7",
            "كود الوحدة": "field6",
            "اسم المالك": "field5",
            "رقم المالك": "field4",
            "العنوان": "field3",
            "المميزات": "field2",
            "تفاصيل كاملة": "field1",
            "السعر": "field"
        }
    
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def refresh_access_token(self) -> bool:
        """تجديد رمز الوصول"""
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            data = {
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token"
            }
            
            async with self.session.post(self.token_url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.access_token = result.get("access_token")
                    logger.info("✅ تم تجديد رمز الوصول لـ Zoho")
                    return True
                else:
                    logger.error(f"❌ خطأ في تجديد رمز الوصول: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في تجديد رمز الوصول: {e}")
            
        return False
    
    async def create_lead(self, property_data: Dict[str, Any]) -> Optional[str]:
        """إنشاء عميل محتمل جديد في Zoho"""
        
        try:
            if not self.access_token:
                if not await self.refresh_access_token():
                    return None
                    
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # تحويل البيانات إلى تنسيق Zoho
            zoho_data = self._convert_to_zoho_format(property_data)
            
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "data": [zoho_data],
                "trigger": ["approval", "workflow", "blueprint"]
            }
            
            url = f"{self.base_url}/Leads"
            
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 201:
                    result = await response.json()
                    if result.get("data") and len(result["data"]) > 0:
                        lead_id = result["data"][0]["details"]["id"]
                        logger.info(f"✅ تم إنشاء العميل في Zoho: {lead_id}")
                        return lead_id
                    else:
                        logger.error("❌ لم يتم إرجاع معرف العميل من Zoho")
                        
                elif response.status == 401:
                    # انتهت صلاحية الرمز، نحاول التجديد
                    if await self.refresh_access_token():
                        return await self.create_lead(property_data)
                    else:
                        logger.error("❌ فشل في تجديد رمز الوصول")
                        
                else:
                    error_text = await response.text()
                    logger.error(f"❌ خطأ في إنشاء العميل: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء العميل في Zoho: {e}")
            
        return None
    
    def _convert_to_zoho_format(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """تحويل بيانات العقار إلى تنسيق Zoho"""
        
        zoho_data = {}
        
        for arabic_field, zoho_field in self.field_map.items():
            value = property_data.get(arabic_field, "")
            if value:
                # معالجة خاصة للحقول الرقمية
                if arabic_field in ["المساحة", "السعر"]:
                    try:
                        zoho_data[zoho_field] = float(value) if value.replace('.', '').isdigit() else 0
                    except:
                        zoho_data[zoho_field] = 0
                else:
                    zoho_data[zoho_field] = str(value)
        
        # إضافة الحقول المطلوبة في Zoho
        owner_name = property_data.get("اسم المالك", "مالك جديد")
        
        # تقسيم الاسم إلى أول وأخير
        name_parts = owner_name.split()
        if len(name_parts) >= 2:
            zoho_data["First_Name"] = name_parts[0]
            zoho_data["Last_Name"] = " ".join(name_parts[1:])
        else:
            zoho_data["First_Name"] = owner_name
            zoho_data["Last_Name"] = "عميل"  # اسم أخير افتراضي
        
        # إضافة معلومات الاتصال
        if "رقم المالك" in property_data:
            zoho_data["Phone"] = str(property_data["رقم المالك"])
        
        # إضافة حقول إضافية مطلوبة لـ Zoho
        zoho_data["Lead_Source"] = "Telegram Bot"
        zoho_data["Lead_Status"] = "Not Contacted"
        zoho_data["Company"] = "عقار"
        
        # إضافة تاريخ الإنشاء
        zoho_data["Created_Time"] = datetime.now().isoformat()
        
        return zoho_data
    
    async def search_lead(self, owner_phone: str) -> Optional[Dict[str, Any]]:
        """البحث عن عميل موجود"""
        
        try:
            if not self.access_token:
                if not await self.refresh_access_token():
                    return None
                    
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # البحث برقم الهاتف
            search_criteria = f"(field4:equals:{owner_phone})"
            url = f"{self.base_url}/Leads/search?criteria={search_criteria}"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("data") and len(result["data"]) > 0:
                        logger.info("✅ تم العثور على عميل موجود في Zoho")
                        return result["data"][0]
                        
                elif response.status == 204:
                    # لا توجد نتائج
                    logger.info("ℹ️ لم يتم العثور على عميل في Zoho")
                    return None
                    
                elif response.status == 401:
                    if await self.refresh_access_token():
                        return await self.search_lead(owner_phone)
                    else:
                        logger.error("❌ فشل في تجديد رمز الوصول")
                        
                else:
                    error_text = await response.text()
                    logger.error(f"❌ خطأ في البحث: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في البحث في Zoho: {e}")
            
        return None
    
    async def update_lead(self, lead_id: str, property_data: Dict[str, Any]) -> bool:
        """تحديث بيانات عميل موجود"""
        
        try:
            if not self.access_token:
                if not await self.refresh_access_token():
                    return False
                    
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            zoho_data = self._convert_to_zoho_format(property_data)
            
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "data": [zoho_data]
            }
            
            url = f"{self.base_url}/Leads/{lead_id}"
            
            async with self.session.put(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    logger.info(f"✅ تم تحديث العميل في Zoho: {lead_id}")
                    return True
                elif response.status == 401:
                    if await self.refresh_access_token():
                        return await self.update_lead(lead_id, property_data)
                    else:
                        logger.error("❌ فشل في تجديد رمز الوصول")
                else:
                    error_text = await response.text()
                    logger.error(f"❌ خطأ في تحديث العميل: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث العميل في Zoho: {e}")
            
        return False
    
    def get_lead_url(self, lead_id: str) -> str:
        """الحصول على رابط العميل في Zoho"""
        return f"https://crm.zoho.com/crm/EntityInfo?module=Leads&id={lead_id}"
