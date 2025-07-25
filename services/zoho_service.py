
"""
خدمة Zoho CRM المحدثة - Zoho Service for Aqar Module
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
import aiohttp
from datetime import datetime, timedelta
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ZohoService:
    """خدمة التعامل مع Zoho CRM - موديول Aqar الجديد"""
    
    def __init__(self, client_id: str, client_secret: str, 
                 refresh_token: str, access_token: str, module_name: str = "Aqar"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.module_name = module_name  # موديول Aqar الجديد
        
        self.base_url = "https://www.zohoapis.com/crm/v2"
        self.token_url = "https://accounts.zoho.com/oauth/v2/token"
        self.session = None
        
        # خريطة الحقول المحدثة لموديول Aqar
        self.field_map = {
            "البيان": "Name",                    # حقل البيان المدمج الجديد
            "المنطقة": "Region",
            "كود الوحدة": "Unit_Code",
            "نوع الوحدة": "Unit_Type",
            "حالة الوحدة": "Unit_Condition",
            "المساحة": "Area",
            "الدور": "Floor",
            "السعر": "Price",
            "المميزات": "Features",
            "العنوان": "Address",
            "اسم الموظف": "Employee_Name",
            "اسم المالك": "Owner_Name",
            "رقم المالك": "Owner_Phone",
            "اتاحة العقار": "Availability",
            "حالة الصور": "Photos_Status",
            "تفاصيل كاملة": "Full_Details",
            "telegram_message_id": "Telegram_Message_ID",
            "notion_property_id": "Notion_Property_ID",
            "notion_owner_id": "Notion_Owner_ID",
            "status": "Status"
        }
        
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.refresh_access_token()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def refresh_access_token(self) -> bool:
        """تحديث access token"""
        
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
                    if "access_token" in result:
                        self.access_token = result["access_token"]
                        logger.info("✅ تم تحديث Zoho access token")
                        return True
                    else:
                        logger.error(f"❌ خطأ في تحديث التوكن: {result}")
                else:
                    logger.error(f"❌ خطأ HTTP في تحديث التوكن: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث التوكن: {e}")
            
        return False
    
    async def create_record(self, property_data: Dict[str, Any]) -> Optional[str]:
        """إنشاء سجل جديد في موديول Aqar"""
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # تحويل البيانات إلى تنسيق Zoho
            zoho_data = self._convert_to_zoho_format(property_data)
            
            url = f"{self.base_url}/{self.module_name}"
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "data": [zoho_data]
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 201:
                    result = await response.json()
                    if result.get("data") and len(result["data"]) > 0:
                        record_id = result["data"][0]["details"]["id"]
                        logger.info(f"✅ تم إنشاء سجل في Zoho Aqar: {record_id}")
                        return record_id
                    else:
                        logger.error(f"❌ خطأ في استجابة Zoho: {result}")
                elif response.status == 401:
                    # إعادة تحديث التوكن والمحاولة مرة أخرى
                    if await self.refresh_access_token():
                        return await self.create_record(property_data)
                else:
                    error_text = await response.text()
                    logger.error(f"❌ خطأ HTTP في إنشاء السجل: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء السجل: {e}")
            
        return None
    
    async def search_record(self, field_name: str, field_value: str) -> Optional[Dict[str, Any]]:
        """البحث عن سجل بواسطة حقل معين"""
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # تحويل اسم الحقل إلى تنسيق Zoho
            zoho_field = self.field_map.get(field_name, field_name)
            
            url = f"{self.base_url}/{self.module_name}/search"
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "criteria": f"{zoho_field}:equals:{field_value}"
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("data") and len(result["data"]) > 0:
                        record = result["data"][0]
                        logger.info(f"✅ تم العثور على السجل في Zoho: {record['id']}")
                        return record
                elif response.status == 204:
                    # لا توجد نتائج
                    logger.info(f"📝 لم يتم العثور على سجل بـ {field_name}: {field_value}")
                    return None
                elif response.status == 401:
                    # إعادة تحديث التوكن والمحاولة مرة أخرى
                    if await self.refresh_access_token():
                        return await self.search_record(field_name, field_value)
                else:
                    error_text = await response.text()
                    logger.error(f"❌ خطأ HTTP في البحث: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في البحث: {e}")
            
        return None
    
    async def update_record(self, record_id: str, property_data: Dict[str, Any]) -> bool:
        """تحديث سجل موجود"""
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # تحويل البيانات إلى تنسيق Zoho
            zoho_data = self._convert_to_zoho_format(property_data)
            zoho_data["id"] = record_id
            
            url = f"{self.base_url}/{self.module_name}"
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "data": [zoho_data]
            }
            
            async with self.session.put(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("data") and len(result["data"]) > 0:
                        logger.info(f"✅ تم تحديث السجل في Zoho: {record_id}")
                        return True
                    else:
                        logger.error(f"❌ خطأ في تحديث السجل: {result}")
                elif response.status == 401:
                    # إعادة تحديث التوكن والمحاولة مرة أخرى
                    if await self.refresh_access_token():
                        return await self.update_record(record_id, property_data)
                else:
                    error_text = await response.text()
                    logger.error(f"❌ خطأ HTTP في تحديث السجل: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث السجل: {e}")
            
        return False
    
    async def add_property_to_record(self, record_id: str, property_data: Dict[str, Any]) -> bool:
        """إضافة عقار إضافي لسجل موجود (للعقارات المتعددة)"""
        
        try:
            # البحث عن السجل الحالي
            existing_record = await self.get_record(record_id)
            if not existing_record:
                return False
            
            # دمج البيانات الجديدة مع الموجودة
            merged_data = self._merge_property_data(existing_record, property_data)
            
            # تحديث السجل
            return await self.update_record(record_id, merged_data)
            
        except Exception as e:
            logger.error(f"❌ خطأ في إضافة العقار للسجل: {e}")
            return False
    
    async def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """الحصول على سجل بواسطة ID"""
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.base_url}/{self.module_name}/{record_id}"
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("data") and len(result["data"]) > 0:
                        return result["data"][0]
                elif response.status == 401:
                    # إعادة تحديث التوكن والمحاولة مرة أخرى
                    if await self.refresh_access_token():
                        return await self.get_record(record_id)
                else:
                    error_text = await response.text()
                    logger.error(f"❌ خطأ HTTP في الحصول على السجل: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على السجل: {e}")
            
        return None
    
    def _convert_to_zoho_format(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """تحويل بيانات العقار إلى تنسيق Zoho"""
        
        zoho_record = {}
        
        for arabic_field, english_field in self.field_map.items():
            value = property_data.get(arabic_field)
            if value is not None:
                # تحويل القيم حسب نوع الحقل
                if english_field in ["Area", "Price"] and isinstance(value, str):
                    # تحويل النصوص الرقمية إلى أرقام
                    try:
                        zoho_record[english_field] = int(value) if value.isdigit() else value
                    except:
                        zoho_record[english_field] = value
                else:
                    zoho_record[english_field] = value
        
        # إضافة معلومات إضافية
        zoho_record["Created_Time"] = datetime.now().isoformat()
        zoho_record["Modified_Time"] = datetime.now().isoformat()
        
        # تحديد حالة متعددة القيم للـ Status
        status_values = []
        if property_data.get("status"):
            status_values.append(property_data["status"])
        
        # إضافة حالات إضافية بناءً على البيانات
        if property_data.get("notion_property_id"):
            status_values.append("Notion_Synced")
        if property_data.get("telegram_message_id"):
            status_values.append("Telegram_Processed")
        
        if status_values:
            zoho_record["Status"] = status_values
        
        return zoho_record
    
    def _merge_property_data(self, existing_record: Dict[str, Any], 
                           new_property_data: Dict[str, Any]) -> Dict[str, Any]:
        """دمج بيانات العقار الجديد مع السجل الموجود"""
        
        merged_data = existing_record.copy()
        
        # دمج الحقول النصية بفاصلة
        text_fields = ["Full_Details", "Features", "Address"]
        for field in text_fields:
            existing_value = existing_record.get(field, "")
            new_value = new_property_data.get(self._get_arabic_field(field), "")
            
            if new_value and new_value != existing_value:
                if existing_value:
                    merged_data[field] = f"{existing_value} | {new_value}"
                else:
                    merged_data[field] = new_value
        
        # تحديث التوقيت
        merged_data["Modified_Time"] = datetime.now().isoformat()
        
        # إضافة معلومات العقار الإضافي
        additional_unit_code = new_property_data.get("كود الوحدة", "")
        if additional_unit_code:
            existing_codes = merged_data.get("Unit_Code", "")
            if existing_codes and additional_unit_code not in existing_codes:
                merged_data["Unit_Code"] = f"{existing_codes}, {additional_unit_code}"
            elif not existing_codes:
                merged_data["Unit_Code"] = additional_unit_code
        
        return merged_data
    
    def _get_arabic_field(self, english_field: str) -> str:
        """الحصول على اسم الحقل العربي من الإنجليزي"""
        
        reverse_map = {v: k for k, v in self.field_map.items()}
        return reverse_map.get(english_field, english_field)
    
    async def get_daily_report_data(self, date: datetime) -> Dict[str, Any]:
        """الحصول على بيانات التقرير اليومي"""
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # تحديد نطاق التاريخ
            start_date = date.strftime("%Y-%m-%d")
            end_date = (date + timedelta(days=1)).strftime("%Y-%m-%d")
            
            url = f"{self.base_url}/{self.module_name}"
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "criteria": f"Created_Time:between:{start_date}T00:00:00+00:00,{end_date}T00:00:00+00:00"
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    records = result.get("data", [])
                    
                    # تحليل البيانات لإنشاء التقرير
                    report_data = {
                        "total_records": len(records),
                        "by_employee": {},
                        "by_region": {},
                        "by_status": {},
                        "records": records
                    }
                    
                    for record in records:
                        # حسب الموظف
                        employee = record.get("Employee_Name", "غير محدد")
                        report_data["by_employee"][employee] = report_data["by_employee"].get(employee, 0) + 1
                        
                        # حسب المنطقة
                        region = record.get("Region", "غير محدد")
                        report_data["by_region"][region] = report_data["by_region"].get(region, 0) + 1
                        
                        # حسب الحالة
                        status = record.get("Status", ["غير محدد"])
                        if isinstance(status, str):
                            status = [status]
                        for s in status:
                            report_data["by_status"][s] = report_data["by_status"].get(s, 0) + 1
                    
                    logger.info(f"✅ تم الحصول على بيانات التقرير: {len(records)} سجل")
                    return report_data
                    
                elif response.status == 401:
                    if await self.refresh_access_token():
                        return await self.get_daily_report_data(date)
                else:
                    error_text = await response.text()
                    logger.error(f"❌ خطأ في الحصول على بيانات التقرير: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء التقرير: {e}")
            
        return {}
