"""
معالج العقارات - Property Processor
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from models.property import PropertyData, PropertyStatus
from services.telegram_service import TelegramService
from services.ai_service import AIService
from services.notion_service import NotionService
from services.zoho_service import ZohoService
from utils.database import DatabaseManager
from utils.logger import PropertyLogger, setup_logger
from config import Config

logger = setup_logger(__name__)

class PropertyProcessor:
    """معالج العقارات الرئيسي"""
    
    def __init__(self):
        self.config = Config()
        self.database = DatabaseManager(self.config.DATABASE_PATH)
        self.is_running = False
        
        # الخدمات
        self.telegram_service = None
        self.ai_service = None
        self.notion_service = None
        self.zoho_service = None
        
    async def start(self):
        """بدء المعالج"""
        try:
            # تهيئة قاعدة البيانات
            await self.database.initialize()
            
            # تهيئة الخدمات
            self.ai_service = AIService(self.config.ANTHROPIC_API_KEY)
            
            if self.config.NOTION_INTEGRATION_SECRET:
                self.notion_service = NotionService(
                    self.config.NOTION_INTEGRATION_SECRET,
                    self.config.NOTION_PROPERTIES_DB_ID,
                    self.config.NOTION_OWNERS_DB_ID
                )
            
            if self.config.ZOHO_CLIENT_ID:
                self.zoho_service = ZohoService(
                    self.config.ZOHO_CLIENT_ID,
                    self.config.ZOHO_CLIENT_SECRET,
                    self.config.ZOHO_REFRESH_TOKEN,
                    self.config.ZOHO_ACCESS_TOKEN
                )
            
            self.is_running = True
            logger.info("✅ تم بدء معالج العقارات")
            
        except Exception as e:
            logger.error(f"❌ خطأ في بدء المعالج: {e}")
            raise
    
    async def stop(self):
        """إيقاف المعالج"""
        self.is_running = False
        if self.database:
            await self.database.close()
        logger.info("✅ تم إيقاف معالج العقارات")
    
    async def process_all_pending(self):
        """معالجة جميع العقارات المعلقة"""
        while self.is_running:
            try:
                # الحصول على العقارات المعلقة
                pending_properties = await self.database.get_pending_properties()
                
                if pending_properties:
                    logger.info(f"🔄 معالجة {len(pending_properties)} عقار معلق")
                    
                    for property_data in pending_properties:
                        if not self.is_running:
                            break
                            
                        await self.process_property(property_data)
                        await asyncio.sleep(1)  # توقف قصير بين العقارات
                
                # جلب رسائل جديدة من Telegram إذا كان متوفر
                if self.config.TELEGRAM_BOT_TOKEN:
                    await self.fetch_new_messages()
                
                # انتظار قبل المحاولة التالية
                await asyncio.sleep(self.config.PROCESSING_INTERVAL)
                
            except Exception as e:
                logger.error(f"❌ خطأ في حلقة المعالجة: {e}")
                await asyncio.sleep(60)  # انتظار دقيقة في حالة الخطأ
    
    async def fetch_new_messages(self):
        """جلب رسائل جديدة من Telegram"""
        try:
            async with TelegramService(
                self.config.TELEGRAM_BOT_TOKEN,
                self.config.TELEGRAM_CHANNEL_ID
            ) as telegram:
                
                messages = await telegram.get_channel_messages()
                
                for message in messages:
                    # التحقق من عدم معالجة الرسالة مسبقاً
                    existing = await self.database.get_property_by_telegram_id(
                        message['message_id']
                    )
                    
                    if not existing and message['text'].strip():
                        # إنشاء عقار جديد من الرسالة
                        property_data = PropertyData()
                        property_data.telegram_message_id = message['message_id']
                        property_data.raw_text = message['text']
                        property_data.status = PropertyStatus.PENDING
                        
                        # حفظ في قاعدة البيانات
                        await self.database.save_property(property_data)
                        logger.info(f"📥 تم استلام رسالة جديدة: {message['message_id']}")
        
        except Exception as e:
            logger.error(f"❌ خطأ في جلب الرسائل: {e}")
    
    async def process_property(self, property_data: PropertyData) -> bool:
        """معالجة عقار واحد"""
        
        property_logger = PropertyLogger(
            str(property_data.telegram_message_id or "unknown")
        )
        
        try:
            property_logger.log_processing_start(property_data.to_dict())
            
            # زيادة عدد المحاولات
            property_data.processing_attempts += 1
            
            # الخطوة 1: استخراج البيانات بالذكاء الاصطناعي
            if not property_data.ai_extracted and property_data.raw_text:
                success = await self._extract_data_with_ai(property_data, property_logger)
                if not success:
                    return await self._mark_as_failed(property_data, property_logger)
            
            # الخطوة 2: التحقق من صحة البيانات
            is_valid, errors = property_data.is_valid()
            if not is_valid:
                property_logger.log_error("التحقق من البيانات", f"بيانات ناقصة: {', '.join(errors)}")
                return await self._mark_as_failed(property_data, property_logger)
            
            # الخطوة 3: تصنيف العقار
            classification = await self._classify_property(property_data, property_logger)
            
            # الخطوة 4: معالجة حسب التصنيف
            success = await self._process_by_classification(
                property_data, classification, property_logger
            )
            
            if success:
                property_logger.log_processing_complete(True, property_data.status.value)
                return True
            else:
                return await self._mark_as_failed(property_data, property_logger)
                
        except Exception as e:
            property_logger.log_error("معالجة العقار", str(e))
            return await self._mark_as_failed(property_data, property_logger)
    
    async def _extract_data_with_ai(self, property_data: PropertyData, 
                                  property_logger: PropertyLogger) -> bool:
        """استخراج البيانات بالذكاء الاصطناعي"""
        
        try:
            property_logger.log_processing_step("استخراج البيانات", "استخدام الذكاء الاصطناعي")
            
            extracted_data = await self.ai_service.extract_property_data(property_data.raw_text)
            
            if extracted_data:
                # تحديث بيانات العقار
                temp_property = PropertyData.from_dict(extracted_data)
                
                # نسخ البيانات المستخرجة
                property_data.region = temp_property.region
                property_data.unit_code = temp_property.unit_code
                property_data.unit_type = temp_property.unit_type
                property_data.unit_condition = temp_property.unit_condition
                property_data.area = temp_property.area
                property_data.floor = temp_property.floor
                property_data.price = temp_property.price
                property_data.features = temp_property.features
                property_data.address = temp_property.address
                property_data.employee_name = temp_property.employee_name
                property_data.owner_name = temp_property.owner_name
                property_data.owner_phone = temp_property.owner_phone
                property_data.availability = temp_property.availability
                property_data.photos_status = temp_property.photos_status
                property_data.full_details = temp_property.full_details
                
                # إنشاء البيان
                property_data.generate_statement()
                property_data.ai_extracted = True
                
                property_logger.log_success("استخراج البيانات", "تم بنجاح")
                return True
            else:
                property_logger.log_error("استخراج البيانات", "فشل في استخراج البيانات")
                return False
                
        except Exception as e:
            property_logger.log_error("استخراج البيانات", str(e))
            return False
    
    async def _classify_property(self, property_data: PropertyData, 
                               property_logger: PropertyLogger) -> str:
        """تصنيف العقار"""
        
        try:
            property_logger.log_processing_step("تصنيف العقار")
            
            # البحث عن عقارات مكررة
            duplicate_properties = await self.database.find_duplicate_properties(property_data)
            
            if duplicate_properties:
                # عقار مكرر
                property_logger.log_classification("عقار مكرر", "وجد عقار مطابق تماماً")
                return "عقار مكرر"
            
            # البحث عن عقارات للمالك نفسه
            owner_properties = await self.database.find_owner_properties(property_data.owner_phone)
            
            if owner_properties:
                # عقار متعدد
                property_logger.log_classification("عقار متعدد", "مالك لديه عقارات أخرى")
                return "عقار متعدد"
            
            # عقار جديد
            property_logger.log_classification("عقار جديد", "مالك ومواصفات جديدة")
            return "عقار جديد"
            
        except Exception as e:
            property_logger.log_error("تصنيف العقار", str(e))
            return "عقار جديد"  # افتراضي
    
    async def _process_by_classification(self, property_data: PropertyData, 
                                       classification: str, 
                                       property_logger: PropertyLogger) -> bool:
        """معالجة العقار حسب التصنيف"""
        
        try:
            if classification == "عقار جديد":
                return await self._process_new_property(property_data, property_logger)
            
            elif classification == "عقار متعدد":
                return await self._process_multiple_property(property_data, property_logger)
            
            elif classification == "عقار مكرر":
                return await self._process_duplicate_property(property_data, property_logger)
            
            else:
                property_logger.log_error("المعالجة", f"تصنيف غير معروف: {classification}")
                return False
                
        except Exception as e:
            property_logger.log_error("المعالجة حسب التصنيف", str(e))
            return False
    
    async def _process_new_property(self, property_data: PropertyData, 
                                  property_logger: PropertyLogger) -> bool:
        """معالجة عقار جديد"""
        
        try:
            # إنشاء صفحة مالك في Notion
            owner_id = None
            if self.notion_service:
                owner_id = await self.notion_service.create_owner_page(property_data.to_dict())
                property_data.notion_owner_id = owner_id
                property_logger.log_success("إنشاء صفحة المالك", f"Notion ID: {owner_id}")
            
            # إنشاء صفحة عقار في Notion
            if self.notion_service:
                property_id = await self.notion_service.create_property_page(
                    property_data.to_dict(), owner_id
                )
                property_data.notion_property_id = property_id
                property_logger.log_success("إنشاء صفحة العقار", f"Notion ID: {property_id}")
            
            # إرسال البيانات إلى Zoho
            if self.zoho_service:
                async with self.zoho_service as zoho:
                    lead_id = await zoho.create_lead(property_data.to_dict())
                    property_data.zoho_lead_id = lead_id
                    property_logger.log_success("إنشاء العميل", f"Zoho ID: {lead_id}")
            
            # تحديث الحالة
            property_data.status = PropertyStatus.SUCCESSFUL
            await self.database.update_property(
                property_data.telegram_message_id, property_data
            )
            
            # إرسال إشعار
            await self._send_notification(property_data, "عقار جديد", property_logger)
            
            return True
            
        except Exception as e:
            property_logger.log_error("معالجة العقار الجديد", str(e))
            return False
    
    async def _process_multiple_property(self, property_data: PropertyData, 
                                       property_logger: PropertyLogger) -> bool:
        """معالجة عقار متعدد"""
        
        try:
            # البحث عن المالك الموجود
            existing_owner = None
            if self.notion_service:
                existing_owner = await self.notion_service.search_owner(property_data.owner_phone)
            
            # إنشاء صفحة عقار جديدة مرتبطة بالمالك الموجود
            if self.notion_service and existing_owner:
                property_id = await self.notion_service.create_property_page(
                    property_data.to_dict(), existing_owner['id']
                )
                property_data.notion_property_id = property_id
                property_data.notion_owner_id = existing_owner['id']
                
                # تحديث عدد عقارات المالك
                await self.notion_service.update_owner_properties_count(existing_owner['id'])
                
                property_logger.log_success("ربط العقار بالمالك", f"Property: {property_id}")
            
            # إرسال البيانات إلى Zoho
            if self.zoho_service:
                async with self.zoho_service as zoho:
                    # البحث عن العميل الموجود
                    existing_lead = await zoho.search_lead(property_data.owner_phone)
                    
                    if existing_lead:
                        # تحديث البيانات الموجودة
                        await zoho.update_lead(existing_lead['id'], property_data.to_dict())
                        property_data.zoho_lead_id = existing_lead['id']
                        property_logger.log_success("تحديث العميل", f"Zoho ID: {existing_lead['id']}")
                    else:
                        # إنشاء عميل جديد
                        lead_id = await zoho.create_lead(property_data.to_dict())
                        property_data.zoho_lead_id = lead_id
                        property_logger.log_success("إنشاء العميل", f"Zoho ID: {lead_id}")
            
            # تحديث الحالة
            property_data.status = PropertyStatus.SUCCESSFUL
            await self.database.update_property(
                property_data.telegram_message_id, property_data
            )
            
            # إرسال إشعار
            await self._send_notification(property_data, "عقار متعدد", property_logger)
            
            return True
            
        except Exception as e:
            property_logger.log_error("معالجة العقار المتعدد", str(e))
            return False
    
    async def _process_duplicate_property(self, property_data: PropertyData, 
                                        property_logger: PropertyLogger) -> bool:
        """معالجة عقار مكرر"""
        
        try:
            # البحث عن العقار المطابق
            duplicate_properties = await self.database.find_duplicate_properties(property_data)
            similar_property = duplicate_properties[0] if duplicate_properties else None
            
            # تحديث الحالة
            property_data.status = PropertyStatus.DUPLICATE
            await self.database.update_property(
                property_data.telegram_message_id, property_data
            )
            
            # إرسال إشعار مع رابط العقار المشابه
            similar_link = ""
            if similar_property and similar_property.notion_property_id:
                similar_link = f"https://www.notion.so/{similar_property.notion_property_id.replace('-', '')}"
            
            await self._send_notification(
                property_data, "عقار مكرر", property_logger, similar_link
            )
            
            property_logger.log_success("معالجة العقار المكرر", "تم الإشعار بالتكرار")
            return True
            
        except Exception as e:
            property_logger.log_error("معالجة العقار المكرر", str(e))
            return False
    
    async def _mark_as_failed(self, property_data: PropertyData, 
                            property_logger: PropertyLogger) -> bool:
        """وسم العقار كفاشل"""
        
        try:
            property_data.status = PropertyStatus.FAILED
            property_data.update_timestamp()
            
            await self.database.update_property(
                property_data.telegram_message_id, property_data
            )
            
            # إرسال إشعار فشل
            await self._send_notification(property_data, "عقار فاشل", property_logger)
            
            property_logger.log_processing_complete(False, "عقار فاشل")
            return True
            
        except Exception as e:
            property_logger.log_error("وسم العقار كفاشل", str(e))
            return False
    
    async def _send_notification(self, property_data: PropertyData, 
                               classification: str, property_logger: PropertyLogger,
                               similar_link: str = "") -> bool:
        """إرسال إشعار"""
        
        try:
            if not self.config.TELEGRAM_BOT_TOKEN:
                return True  # لا يوجد بوت للإشعارات
            
            async with TelegramService(
                self.config.TELEGRAM_BOT_TOKEN,
                self.config.TELEGRAM_CHANNEL_ID
            ) as telegram:
                
                message = telegram.format_property_notification(
                    property_data.to_dict(), classification, similar_link
                )
                
                success = await telegram.send_message(message)
                
                if success:
                    property_logger.log_success("إرسال الإشعار", classification)
                else:
                    property_logger.log_error("إرسال الإشعار", "فشل في الإرسال")
                
                return success
                
        except Exception as e:
            property_logger.log_error("إرسال الإشعار", str(e))
            return False
