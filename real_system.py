
#!/usr/bin/env python3
"""
النظام الحقيقي لإدارة العقارات - Real Estate System
"""

import asyncio
import sys
from datetime import datetime
from real_config import RealConfig
from services.telegram_service import TelegramService
from services.ai_service import AIService
from services.notion_service import NotionService
from services.zoho_service import ZohoService
from models.property import PropertyData, PropertyStatus
from utils.logger import setup_logger
from utils.database import DatabaseManager

logger = setup_logger(__name__)

class RealEstateRealSystem:
    """النظام الحقيقي لمعالجة العقارات"""
    
    def __init__(self):
        self.config = RealConfig()
        self.database = None
        self.is_running = False
        
        # الخدمات
        self.telegram_service = None
        self.ai_service = None
        self.notion_service = None
        self.zoho_service = None
        
        # إحصائيات
        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "duplicate": 0,
            "multiple": 0,
            "session_start": datetime.now()
        }
    
    async def initialize(self):
        """تهيئة النظام"""
        
        logger.info("🔧 تهيئة النظام الحقيقي...")
        
        # التحقق من الإعدادات
        if not self.config.validate():
            raise Exception("إعدادات غير صحيحة")
        
        # تهيئة قاعدة البيانات
        self.database = DatabaseManager(self.config.DATABASE_PATH)
        await self.database.initialize()
        
        # تهيئة الخدمات
        self.ai_service = AIService(self.config)
        self.telegram_service = TelegramService(self.config)
        
        # تهيئة Notion إذا كان متاحاً
        if (self.config.NOTION_INTEGRATION_SECRET and 
            self.config.NOTION_PROPERTIES_DB_ID and 
            self.config.NOTION_OWNERS_DB_ID):
            self.notion_service = NotionService(
                self.config.NOTION_INTEGRATION_SECRET,
                self.config.NOTION_PROPERTIES_DB_ID,
                self.config.NOTION_OWNERS_DB_ID
            )
            logger.info("✅ تم تهيئة خدمة Notion")
        else:
            logger.warning("⚠️ Notion غير مُعد - سيتم تخطيه")
        
        # تهيئة Zoho إذا كان متاحاً
        if (self.config.ZOHO_CLIENT_ID and 
            self.config.ZOHO_CLIENT_SECRET and 
            self.config.ZOHO_REFRESH_TOKEN):
            self.zoho_service = ZohoService(
                self.config.ZOHO_CLIENT_ID,
                self.config.ZOHO_CLIENT_SECRET,
                self.config.ZOHO_REFRESH_TOKEN,
                self.config.ZOHO_ACCESS_TOKEN,
                self.config.ZOHO_MODULE_NAME
            )
            logger.info("✅ تم تهيئة خدمة Zoho CRM")
        else:
            logger.warning("⚠️ Zoho CRM غير مُعد - سيتم تخطيه")
        
        logger.info("✅ تم تهيئة النظام الحقيقي بنجاح")
    
    async def start_monitoring(self):
        """بدء مراقبة القناة ومعالجة الرسائل"""
        
        self.is_running = True
        logger.info("🚀 بدء مراقبة القناة الحقيقية...")
        logger.info(f"📱 القناة: {self.config.TELEGRAM_CHANNEL_ID}")
        logger.info(f"🤖 مزودو AI متاحون: {', '.join(self.config.get_available_ai_providers())}")
        
        while self.is_running:
            try:
                # جلب الرسائل الجديدة
                new_messages = await self._fetch_new_messages()
                
                if new_messages:
                    logger.info(f"📥 تم العثور على {len(new_messages)} رسالة جديدة")
                    
                    # معالجة كل رسالة
                    for message in new_messages:
                        if not self.is_running:
                            break
                        
                        await self._process_single_message(message)
                        await asyncio.sleep(2)  # توقف بين الرسائل
                
                # معالجة العقارات المعلقة
                await self._process_pending_properties()
                
                # انتظار قبل الدورة التالية
                logger.info(f"⏳ انتظار {self.config.PROCESSING_INTERVAL} ثانية...")
                await asyncio.sleep(self.config.PROCESSING_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("🛑 تم طلب إيقاف النظام...")
                break
            except Exception as e:
                logger.error(f"❌ خطأ في حلقة المراقبة: {e}")
                await asyncio.sleep(60)  # انتظار دقيقة في حالة الخطأ
        
        await self._cleanup()
    
    async def _fetch_new_messages(self):
        """جلب الرسائل الجديدة من القناة"""
        
        try:
            async with self.telegram_service as telegram:
                # جلب الرسائل مع تطبيق الفلترة
                messages = await telegram.get_channel_messages(limit=50, apply_filter=True)
                
                new_messages = []
                for message in messages:
                    # التحقق من عدم معالجة الرسالة مسبقاً
                    existing = await self.database.get_property_by_telegram_id(
                        message['message_id']
                    )
                    
                    if not existing and message['text'].strip():
                        new_messages.append(message)
                
                return new_messages
                
        except Exception as e:
            logger.error(f"❌ خطأ في جلب الرسائل: {e}")
            return []
    
    async def _process_single_message(self, message):
        """معالجة رسالة واحدة"""
        
        try:
            logger.info(f"📝 معالجة الرسالة {message['message_id']}")
            
            # إنشاء عقار جديد
            property_data = PropertyData()
            property_data.telegram_message_id = message['message_id']
            property_data.raw_text = message['text']
            property_data.status = PropertyStatus.PENDING
            property_data.serial_number = await self._get_next_serial()
            
            # حفظ في قاعدة البيانات
            await self.database.save_property(property_data)
            
            logger.info(f"✅ تم استلام الرسالة {message['message_id']}")
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الرسالة {message['message_id']}: {e}")
    
    async def _process_pending_properties(self):
        """معالجة العقارات المعلقة"""
        
        try:
            pending = await self.database.get_pending_properties()
            
            if pending:
                logger.info(f"🔄 معالجة {len(pending)} عقار معلق")
                
                for property_data in pending:
                    if not self.is_running:
                        break
                    
                    success = await self._process_property_complete(property_data)
                    
                    if success:
                        self.stats["successful"] += 1
                    else:
                        self.stats["failed"] += 1
                    
                    self.stats["total_processed"] += 1
                    
                    # طباعة إحصائيات
                    if self.stats["total_processed"] % 5 == 0:
                        self._print_stats()
                    
                    await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة العقارات المعلقة: {e}")
    
    async def _process_property_complete(self, property_data):
        """المعالجة الكاملة للعقار"""
        
        try:
            logger.info(f"🏠 بدء معالجة العقار {property_data.telegram_message_id}")
            
            # الخطوة 1: استخراج البيانات بالذكاء الاصطناعي
            if not property_data.ai_extracted:
                extracted = await self.ai_service.extract_property_data(property_data.raw_text)
                
                if not extracted:
                    logger.error(f"❌ فشل استخراج البيانات للعقار {property_data.telegram_message_id}")
                    return await self._mark_as_failed(property_data)
                
                # تحديث البيانات
                self._update_property_data(property_data, extracted)
                property_data.ai_extracted = True
            
            # الخطوة 2: التحقق من صحة البيانات
            is_valid, errors = await self.ai_service.validate_property_data(property_data.to_dict())
            if not is_valid:
                logger.error(f"❌ بيانات غير صحيحة: {', '.join(errors)}")
                return await self._mark_as_failed(property_data)
            
            # الخطوة 3: تصنيف العقار
            classification = await self._classify_property(property_data)
            logger.info(f"🏷️ تصنيف العقار: {classification}")
            
            # الخطوة 4: معالجة حسب التصنيف
            success = await self._process_by_classification(property_data, classification)
            
            if success:
                # إرسال إشعار نجاح
                await self._send_success_notification(property_data, classification)
                
                property_data.status = PropertyStatus.SUCCESSFUL
                await self.database.update_property(property_data.telegram_message_id, property_data)
                
                logger.info(f"✅ تم معالجة العقار {property_data.telegram_message_id} بنجاح")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة العقار {property_data.telegram_message_id}: {e}")
            return await self._mark_as_failed(property_data)
    
    def _update_property_data(self, property_data, extracted):
        """تحديث بيانات العقار من البيانات المستخرجة"""
        
        temp_property = PropertyData.from_dict(extracted)
        
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
        property_data.statement = extracted.get("البيان", "")
    
    async def _classify_property(self, property_data):
        """تصنيف العقار"""
        
        if self.notion_service:
            # البحث في Notion
            duplicates = await self.notion_service.search_property(property_data.to_dict())
            if duplicates:
                return "عقار مكرر"
            
            owner_properties = await self.notion_service.search_owner(property_data.owner_phone)
            if owner_properties:
                return "عقار متعدد"
        
        return "عقار جديد"
    
    async def _process_by_classification(self, property_data, classification):
        """معالجة حسب التصنيف"""
        
        try:
            if classification == "عقار جديد":
                return await self._process_new_property(property_data)
            elif classification == "عقار متعدد":
                return await self._process_multiple_property(property_data)
            elif classification == "عقار مكرر":
                return await self._process_duplicate_property(property_data)
            
            return False
            
        except Exception as e:
            logger.error(f"❌ خطأ في المعالجة حسب التصنيف: {e}")
            return False
    
    async def _process_new_property(self, property_data):
        """معالجة عقار جديد"""
        
        try:
            # إنشاء في Notion
            if self.notion_service:
                owner_id = await self.notion_service.create_owner_page(property_data.to_dict())
                property_data.notion_owner_id = owner_id
                
                property_id = await self.notion_service.create_property_page(
                    property_data.to_dict(), owner_id
                )
                property_data.notion_property_id = property_id
                
                logger.info(f"✅ تم إنشاء صفحات Notion: Owner={owner_id}, Property={property_id}")
            
            # إنشاء في Zoho
            if self.zoho_service:
                async with self.zoho_service as zoho:
                    record_id = await zoho.create_record(property_data.to_dict())
                    property_data.zoho_record_id = record_id
                    logger.info(f"✅ تم إنشاء سجل Zoho: {record_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة العقار الجديد: {e}")
            return False
    
    async def _process_multiple_property(self, property_data):
        """معالجة عقار متعدد"""
        
        try:
            # البحث عن المالك الموجود
            existing_owner = None
            if self.notion_service:
                existing_owner = await self.notion_service.search_owner(property_data.owner_phone)
                
                if existing_owner:
                    property_id = await self.notion_service.create_property_page(
                        property_data.to_dict(), existing_owner['id']
                    )
                    property_data.notion_property_id = property_id
                    property_data.notion_owner_id = existing_owner['id']
                    
                    await self.notion_service.update_owner_properties_count(existing_owner['id'])
                    logger.info(f"✅ تم ربط العقار بالمالك الموجود: {property_id}")
            
            # تحديث في Zoho
            if self.zoho_service:
                async with self.zoho_service as zoho:
                    existing_record = await zoho.search_record("Owner_Phone", property_data.owner_phone)
                    
                    if existing_record:
                        await zoho.add_property_to_record(existing_record['id'], property_data.to_dict())
                        property_data.zoho_record_id = existing_record['id']
                    else:
                        record_id = await zoho.create_record(property_data.to_dict())
                        property_data.zoho_record_id = record_id
                    
                    logger.info(f"✅ تم تحديث سجل Zoho للعقار المتعدد")
            
            self.stats["multiple"] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة العقار المتعدد: {e}")
            return False
    
    async def _process_duplicate_property(self, property_data):
        """معالجة عقار مكرر"""
        
        try:
            # إرسال إشعار فقط
            await self._send_duplicate_notification(property_data)
            
            property_data.status = PropertyStatus.DUPLICATE
            await self.database.update_property(property_data.telegram_message_id, property_data)
            
            self.stats["duplicate"] += 1
            logger.info(f"✅ تم معالجة العقار المكرر: {property_data.telegram_message_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة العقار المكرر: {e}")
            return False
    
    async def _send_success_notification(self, property_data, classification):
        """إرسال إشعار النجاح"""
        
        try:
            async with TelegramService(self.config) as telegram:
                # حذف الرسالة الأصلية
                if property_data.telegram_message_id:
                    await telegram.delete_message(property_data.telegram_message_id)
                
                # إرسال رسالة منسقة
                success_message = telegram.format_success_message(property_data.to_dict())
                await telegram.send_message_to_channel(success_message)
                
                # إرسال إشعار
                notification = telegram.format_property_notification(
                    property_data.to_dict(), classification
                )
                await telegram.send_notification(notification)
                
                logger.info(f"✅ تم إرسال إشعار النجاح للعقار {property_data.telegram_message_id}")
                
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال إشعار النجاح: {e}")
    
    async def _send_duplicate_notification(self, property_data):
        """إرسال إشعار التكرار"""
        
        try:
            async with TelegramService(self.config) as telegram:
                # وسم الرسالة كمكررة
                if property_data.telegram_message_id:
                    await telegram.add_message_tag(
                        property_data.telegram_message_id, 
                        self.config.DUPLICATE_TAG
                    )
                
                # إرسال إشعار التكرار
                notification = telegram.format_property_notification(
                    property_data.to_dict(), "عقار مكرر"
                )
                await telegram.send_notification(notification)
                
                logger.info(f"✅ تم إرسال إشعار التكرار للعقار {property_data.telegram_message_id}")
                
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال إشعار التكرار: {e}")
    
    async def _mark_as_failed(self, property_data):
        """وسم العقار كفاشل"""
        
        try:
            property_data.status = PropertyStatus.FAILED
            property_data.processing_attempts += 1
            
            await self.database.update_property(property_data.telegram_message_id, property_data)
            
            # إرسال رسالة فاشل منسقة
            async with TelegramService(self.config) as telegram:
                if property_data.telegram_message_id:
                    await telegram.delete_message(property_data.telegram_message_id)
                
                failed_message = telegram.format_failed_message(property_data.to_dict())
                await telegram.send_message_to_channel(failed_message)
            
            logger.info(f"❌ تم وسم العقار {property_data.telegram_message_id} كفاشل")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في وسم العقار كفاشل: {e}")
            return False
    
    async def _get_next_serial(self):
        """الحصول على الرقم التسلسلي التالي"""
        
        try:
            last_serial = await self.database.get_last_serial_number()
            return (last_serial or 0) + 1
        except Exception:
            return 1
    
    def _print_stats(self):
        """طباعة الإحصائيات"""
        
        runtime = datetime.now() - self.stats["session_start"]
        
        logger.info("📊 إحصائيات الجلسة:")
        logger.info(f"   ⏱️ مدة التشغيل: {runtime}")
        logger.info(f"   📈 إجمالي معالج: {self.stats['total_processed']}")
        logger.info(f"   ✅ ناجح: {self.stats['successful']}")
        logger.info(f"   ❌ فاشل: {self.stats['failed']}")
        logger.info(f"   🔄 مكرر: {self.stats['duplicate']}")
        logger.info(f"   📊 متعدد: {self.stats['multiple']}")
        
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['successful'] / self.stats['total_processed']) * 100
            logger.info(f"   📈 معدل النجاح: {success_rate:.1f}%")
    
    async def _cleanup(self):
        """تنظيف الموارد"""
        
        self.is_running = False
        if self.database:
            await self.database.close()
        
        self._print_stats()
        logger.info("✅ تم إيقاف النظام الحقيقي")

async def main():
    """الدالة الرئيسية"""
    
    print("🏠 النظام الحقيقي لإدارة العقارات")
    print("=" * 60)
    
    system = RealEstateRealSystem()
    
    try:
        await system.initialize()
        await system.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n🛑 تم طلب إيقاف النظام...")
    except Exception as e:
        logger.error(f"❌ خطأ في النظام: {e}")
    finally:
        await system._cleanup()

if __name__ == "__main__":
    asyncio.run(main())
