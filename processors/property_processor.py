
"""
معالج العقارات المحدث - Updated Property Processor
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
    """معالج العقارات الرئيسي مع التحديثات الجديدة"""
    
    def __init__(self):
        self.config = Config()
        self.database = DatabaseManager(self.config.DATABASE_PATH)
        self.is_running = False
        
        # الخدمات المحدثة
        self.telegram_service = None
        self.ai_service = None
        self.notion_service = None
        self.zoho_service = None
        
        # إحصائيات المعالجة
        self.processing_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "duplicate": 0,
            "multiple": 0,
            "ai_providers_used": {}
        }
        
    async def start(self):
        """بدء المعالج"""
        try:
            # تهيئة قاعدة البيانات
            await self.database.initialize()
            
            # تهيئة الخدمات المحدثة
            self.ai_service = AIService(self.config)
            
            self.telegram_service = TelegramService(self.config)
            
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
                    self.config.ZOHO_ACCESS_TOKEN,
                    self.config.ZOHO_MODULE_NAME  # موديول Aqar الجديد
                )
            
            self.is_running = True
            logger.info("✅ تم بدء معالج العقارات المحدث")
            
            # طباعة إحصائيات المزودين المتاحين
            available_providers = self.config.get_available_ai_providers()
            logger.info(f"🤖 مزودو الذكاء الاصطناعي المتاحون: {', '.join(available_providers)}")
            
        except Exception as e:
            logger.error(f"❌ خطأ في بدء المعالج: {e}")
            raise
    
    async def stop(self):
        """إيقاف المعالج"""
        self.is_running = False
        if self.database:
            await self.database.close()
        logger.info("✅ تم إيقاف معالج العقارات")
        
        # طباعة إحصائيات نهائية
        self._print_processing_stats()
    
    async def process_all_pending(self):
        """معالجة جميع العقارات المعلقة مع السير المحدث"""
        
        while self.is_running:
            try:
                logger.info("🔄 بدء دورة معالجة جديدة...")
                
                # جلب رسائل جديدة من Telegram
                await self.fetch_new_messages()
                
                # الحصول على العقارات المعلقة
                pending_properties = await self.database.get_pending_properties()
                
                if pending_properties:
                    logger.info(f"🔄 معالجة {len(pending_properties)} عقار معلق")
                    
                    batch_results = []
                    
                    for property_data in pending_properties:
                        if not self.is_running:
                            break
                            
                        result = await self.process_property(property_data)
                        batch_results.append(result)
                        
                        await asyncio.sleep(1)  # توقف قصير بين العقارات
                    
                    # إعادة معالجة العقارات الفاشلة في نفس الدفعة
                    await self._reprocess_failed_properties()
                    
                    logger.info(f"✅ انتهت دورة المعالجة - نجح: {sum(1 for r in batch_results if r)}")
                
                # انتظار قبل المحاولة التالية
                await asyncio.sleep(self.config.PROCESSING_INTERVAL)
                
            except Exception as e:
                logger.error(f"❌ خطأ في حلقة المعالجة: {e}")
                await asyncio.sleep(60)  # انتظار دقيقة في حالة الخطأ
    
    async def fetch_new_messages(self):
        """جلب رسائل جديدة من Telegram مع تطبيق الفلترة"""
        
        try:
            async with TelegramService(self.config) as telegram:
                
                # جلب الرسائل مع تطبيق فلتر الوسم
                messages = await telegram.get_channel_messages(limit=100, apply_filter=True)
                
                new_messages_count = 0
                
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
                        property_data.serial_number = await self._get_next_serial_number()
                        
                        # حفظ في قاعدة البيانات
                        await self.database.save_property(property_data)
                        new_messages_count += 1
                        
                        logger.info(f"📥 تم استلام رسالة جديدة: {message['message_id']}")
                
                if new_messages_count > 0:
                    logger.info(f"📥 تم استلام {new_messages_count} رسالة جديدة للمعالجة")
        
        except Exception as e:
            logger.error(f"❌ خطأ في جلب الرسائل: {e}")
    
    async def _get_next_serial_number(self) -> int:
        """الحصول على الرقم التسلسلي التالي"""
        
        try:
            # الحصول على آخر رقم تسلسلي من قاعدة البيانات
            last_serial = await self.database.get_last_serial_number()
            return (last_serial or 0) + 1
        except Exception:
            return 1
    
    async def process_property(self, property_data: PropertyData) -> bool:
        """معالجة عقار واحد وفقاً للسير المحدث"""
        
        property_logger = PropertyLogger(
            str(property_data.telegram_message_id or "unknown")
        )
        
        try:
            property_logger.log_processing_start(property_data.to_dict())
            self.processing_stats["total_processed"] += 1
            
            # زيادة عدد المحاولات
            property_data.processing_attempts += 1
            
            # الخطوة 1: استخراج البيانات بسلسلة الذكاء الاصطناعي المحدثة
            if not property_data.ai_extracted and property_data.raw_text:
                success = await self._extract_data_with_ai_chain(property_data, property_logger)
                if not success:
                    return await self._mark_as_failed(property_data, property_logger)
            
            # الخطوة 2: التحقق من صحة البيانات
            is_valid, errors = await self.ai_service.validate_property_data(property_data.to_dict())
            if not is_valid:
                property_logger.log_error("التحقق من البيانات", f"بيانات ناقصة: {', '.join(errors)}")
                return await self._mark_as_failed(property_data, property_logger)
            
            # الخطوة 3: البحث في Notion للمطابقة (بدلاً من قاعدة البيانات المحلية)
            classification = await self._classify_property_via_notion(property_data, property_logger)
            
            # الخطوة 4: معالجة حسب التصنيف الجديد
            success = await self._process_by_classification(
                property_data, classification, property_logger
            )
            
            if success:
                # إرسال إلى القناة الأرشيفية
                await self._send_to_archive(property_data, property_logger)
                
                property_logger.log_processing_complete(True, property_data.status.value)
                self.processing_stats["successful"] += 1
                return True
            else:
                return await self._mark_as_failed(property_data, property_logger)
                
        except Exception as e:
            property_logger.log_error("معالجة العقار", str(e))
            return await self._mark_as_failed(property_data, property_logger)
    
    async def _extract_data_with_ai_chain(self, property_data: PropertyData, 
                                        property_logger: PropertyLogger) -> bool:
        """استخراج البيانات بسلسلة الذكاء الاصطناعي الجديدة"""
        
        try:
            property_logger.log_processing_step("استخراج البيانات", "سلسلة الذكاء الاصطناعي")
            
            # تمرير الرقم التسلسلي للذكاء الاصطناعي
            enhanced_text = f"الرقم التسلسلي: {property_data.serial_number}\n\n{property_data.raw_text}"
            
            extracted_data = await self.ai_service.extract_property_data(enhanced_text)
            
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
                
                # إنشاء البيان المدمج الجديد
                property_data.statement = extracted_data.get("البيان", "")
                property_data.ai_extracted = True
                
                property_logger.log_success("استخراج البيانات", "تم بنجاح")
                return True
            else:
                property_logger.log_error("استخراج البيانات", "فشل في جميع مزودي الذكاء الاصطناعي")
                return False
                
        except Exception as e:
            property_logger.log_error("استخراج البيانات", str(e))
            return False
    
    async def _classify_property_via_notion(self, property_data: PropertyData, 
                                          property_logger: PropertyLogger) -> str:
        """تصنيف العقار عبر البحث المباشر في Notion"""
        
        try:
            property_logger.log_processing_step("تصنيف العقار", "البحث في Notion")
            
            if not self.notion_service:
                property_logger.log_classification("عقار جديد", "Notion غير متاح")
                return "عقار جديد"
            
            # البحث عن عقارات مكررة (تطابق جميع الشروط)
            duplicate_properties = await self.notion_service.find_duplicate_properties(
                property_data.owner_phone,
                property_data.region,
                property_data.unit_type,
                property_data.unit_condition,
                property_data.area,
                property_data.floor
            )
            
            if duplicate_properties:
                # عقار مكرر
                property_logger.log_classification("عقار مكرر", "وجد عقار مطابق تماماً في Notion")
                return "عقار مكرر"
            
            # البحث عن عقارات للمالك نفسه
            owner_properties = await self.notion_service.find_owner_properties(property_data.owner_phone)
            
            if owner_properties:
                # عقار متعدد
                property_logger.log_classification("عقار متعدد", "مالك لديه عقارات أخرى في Notion")
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
        """معالجة العقار حسب التصنيف الجديد"""
        
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
            
            # إرسال البيانات إلى Zoho موديول Aqar
            if self.zoho_service:
                async with self.zoho_service as zoho:
                    record_id = await zoho.create_record(property_data.to_dict())
                    property_data.zoho_record_id = record_id
                    property_logger.log_success("إنشاء السجل في Zoho", f"Aqar ID: {record_id}")
            
            # تحديث الحالة
            property_data.status = PropertyStatus.SUCCESSFUL
            await self.database.update_property(
                property_data.telegram_message_id, property_data
            )
            
            # إرسال إشعار نجاح
            await self._send_success_notification(property_data, "عقار جديد", property_logger)
            
            return True
            
        except Exception as e:
            property_logger.log_error("معالجة العقار الجديد", str(e))
            return False
    
    async def _process_multiple_property(self, property_data: PropertyData, 
                                       property_logger: PropertyLogger) -> bool:
        """معالجة عقار متعدد (بدون إنشاء مالك جديد)"""
        
        try:
            # البحث عن المالك الموجود في Notion
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
                
                property_logger.log_success("ربط العقار بالمالك الموجود", f"Property: {property_id}")
            
            # إرسال البيانات إلى Zoho مع تحديث السجل الموجود أو إنشاء جديد
            if self.zoho_service:
                async with self.zoho_service as zoho:
                    existing_record = await zoho.search_record("Owner_Phone", property_data.owner_phone)
                    
                    if existing_record:
                        # تحديث السجل الموجود بعقار إضافي
                        await zoho.add_property_to_record(existing_record['id'], property_data.to_dict())
                        property_data.zoho_record_id = existing_record['id']
                        property_logger.log_success("تحديث السجل في Zoho", f"Aqar ID: {existing_record['id']}")
                    else:
                        # إنشاء سجل جديد
                        record_id = await zoho.create_record(property_data.to_dict())
                        property_data.zoho_record_id = record_id
                        property_logger.log_success("إنشاء السجل في Zoho", f"Aqar ID: {record_id}")
            
            # تحديث الحالة
            property_data.status = PropertyStatus.SUCCESSFUL
            await self.database.update_property(
                property_data.telegram_message_id, property_data
            )
            
            # إرسال إشعار نجاح
            await self._send_success_notification(property_data, "عقار متعدد", property_logger)
            
            return True
            
        except Exception as e:
            property_logger.log_error("معالجة العقار المتعدد", str(e))
            return False
    
    async def _process_duplicate_property(self, property_data: PropertyData, 
                                        property_logger: PropertyLogger) -> bool:
        """معالجة عقار مكرر (بدون إنشاء مالك أو عقار جديد)"""
        
        try:
            # البحث عن العقار المطابق في Notion
            duplicate_properties = await self.notion_service.find_duplicate_properties(
                property_data.owner_phone,
                property_data.region,
                property_data.unit_type,
                property_data.unit_condition,
                property_data.area,
                property_data.floor
            ) if self.notion_service else []
            
            similar_property = duplicate_properties[0] if duplicate_properties else None
            
            # تحديث الحالة كمكرر
            property_data.status = PropertyStatus.DUPLICATE
            await self.database.update_property(
                property_data.telegram_message_id, property_data
            )
            
            # إرسال إشعار مكرر مع رابط العقار المشابه
            similar_link = ""
            if similar_property and similar_property.get('id'):
                similar_link = f"https://www.notion.so/{similar_property['id'].replace('-', '')}"
            
            await self._send_duplicate_notification(
                property_data, "عقار مكرر", property_logger, similar_link
            )
            
            property_logger.log_success("معالجة العقار المكرر", "تم الإشعار بالتكرار")
            self.processing_stats["duplicate"] += 1
            return True
            
        except Exception as e:
            property_logger.log_error("معالجة العقار المكرر", str(e))
            return False
    
    async def _mark_as_failed(self, property_data: PropertyData, 
                            property_logger: PropertyLogger) -> bool:
        """وسم العقار كفاشل مع الرسالة المنسقة"""
        
        try:
            property_data.status = PropertyStatus.FAILED
            property_data.update_timestamp()
            
            await self.database.update_property(
                property_data.telegram_message_id, property_data
            )
            
            # حذف الرسالة الأصلية وإرسال رسالة فاشل منسقة
            await self._replace_with_failed_message(property_data, property_logger)
            
            property_logger.log_processing_complete(False, "عقار فاشل")
            self.processing_stats["failed"] += 1
            return True
            
        except Exception as e:
            property_logger.log_error("وسم العقار كفاشل", str(e))
            return False
    
    async def _send_success_notification(self, property_data: PropertyData, 
                                       classification: str, 
                                       property_logger: PropertyLogger) -> bool:
        """إرسال إشعار نجاح وتحديث الرسالة الأصلية"""
        
        try:
            async with TelegramService(self.config) as telegram:
                
                # 1. حذف الرسالة الأصلية
                if property_data.telegram_message_id:
                    await telegram.delete_message(property_data.telegram_message_id)
                
                # 2. إرسال رسالة منسقة جديدة
                success_message = telegram.format_success_message(property_data.to_dict())
                await telegram.send_message_to_channel(success_message)
                
                # 3. إرسال إشعار بواسطة بوت الإشعارات
                notification = telegram.format_property_notification(
                    property_data.to_dict(), classification
                )
                await telegram.send_notification(notification)
                
                property_logger.log_success("إرسال إشعار النجاح", classification)
                return True
                
        except Exception as e:
            property_logger.log_error("إرسال إشعار النجاح", str(e))
            return False
    
    async def _send_duplicate_notification(self, property_data: PropertyData, 
                                         classification: str, 
                                         property_logger: PropertyLogger,
                                         similar_link: str = "") -> bool:
        """إرسال إشعار تكرار"""
        
        try:
            async with TelegramService(self.config) as telegram:
                
                # إرسال إشعار التكرار بواسطة بوت الإشعارات
                notification = telegram.format_property_notification(
                    property_data.to_dict(), classification, similar_link
                )
                await telegram.send_notification(notification)
                
                # وسم الرسالة الأصلية
                if property_data.telegram_message_id:
                    await telegram.add_message_tag(
                        property_data.telegram_message_id, 
                        self.config.DUPLICATE_TAG
                    )
                
                property_logger.log_success("إرسال إشعار التكرار", classification)
                return True
                
        except Exception as e:
            property_logger.log_error("إرسال إشعار التكرار", str(e))
            return False
    
    async def _replace_with_failed_message(self, property_data: PropertyData, 
                                         property_logger: PropertyLogger) -> bool:
        """استبدال الرسالة الأصلية برسالة فاشل منسقة"""
        
        try:
            async with TelegramService(self.config) as telegram:
                
                # حذف الرسالة الأصلية
                if property_data.telegram_message_id:
                    await telegram.delete_message(property_data.telegram_message_id)
                
                # إرسال رسالة فاشل منسقة
                failed_message = telegram.format_failed_message(property_data.to_dict())
                await telegram.send_message_to_channel(failed_message)
                
                property_logger.log_success("استبدال رسالة الفشل", "تم التنسيق")
                return True
                
        except Exception as e:
            property_logger.log_error("استبدال رسالة الفشل", str(e))
            return False
    
    async def _send_to_archive(self, property_data: PropertyData, 
                             property_logger: PropertyLogger) -> bool:
        """إرسال العقار إلى القناة الأرشيفية"""
        
        try:
            async with TelegramService(self.config) as telegram:
                
                # إرسال إلى الأرشيف مع معلومات JSON
                archive_data = {
                    "البيان": property_data.statement,
                    "المنطقة": property_data.region,
                    "كود الوحدة": property_data.unit_code,
                    "نوع الوحدة": property_data.unit_type,
                    "حالة الوحدة": property_data.unit_condition,
                    "المساحة": property_data.area,
                    "الدور": property_data.floor,
                    "السعر": property_data.price,
                    "اسم المالك": property_data.owner_name,
                    "رقم المالك": property_data.owner_phone,
                    "notion_id": property_data.notion_property_id,
                    "zoho_id": property_data.zoho_record_id
                }
                
                import json
                archive_text = f"📊 <b>بيانات مُعالجة</b>\n\n<code>{json.dumps(archive_data, ensure_ascii=False, indent=2)}</code>"
                
                success = await telegram.send_to_archive(
                    archive_text, 
                    property_data.telegram_message_id or 0
                )
                
                if success:
                    property_logger.log_success("الأرشفة", "تم الإرسال للأرشيف")
                
                return success
                
        except Exception as e:
            property_logger.log_error("الأرشفة", str(e))
            return False
    
    async def _reprocess_failed_properties(self):
        """إعادة معالجة العقارات الفاشلة في نفس الدفعة"""
        
        try:
            failed_properties = await self.database.get_failed_properties()
            
            if failed_properties:
                logger.info(f"🔄 إعادة معالجة {len(failed_properties)} عقار فاشل")
                
                for property_data in failed_properties:
                    if property_data.processing_attempts < self.config.MAX_RETRY_ATTEMPTS:
                        property_data.status = PropertyStatus.PENDING
                        await self.database.update_property(
                            property_data.telegram_message_id, property_data
                        )
                        
                        logger.info(f"🔄 إعادة جدولة العقار {property_data.telegram_message_id}")
                
        except Exception as e:
            logger.error(f"❌ خطأ في إعادة معالجة العقارات الفاشلة: {e}")
    
    def _print_processing_stats(self):
        """طباعة إحصائيات المعالجة"""
        
        logger.info("📊 إحصائيات المعالجة:")
        logger.info(f"   📈 إجمالي معالج: {self.processing_stats['total_processed']}")
        logger.info(f"   ✅ ناجح: {self.processing_stats['successful']}")
        logger.info(f"   ❌ فاشل: {self.processing_stats['failed']}")
        logger.info(f"   🔄 مكرر: {self.processing_stats['duplicate']}")
        logger.info(f"   📊 متعدد: {self.processing_stats['multiple']}")
        
        if self.processing_stats['ai_providers_used']:
            logger.info("🤖 مزودو الذكاء الاصطناعي المستخدمون:")
            for provider, count in self.processing_stats['ai_providers_used'].items():
                logger.info(f"   {provider}: {count}")
