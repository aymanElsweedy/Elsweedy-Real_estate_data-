
#!/usr/bin/env python3
"""
تطبيق تجريبي لنظام إدارة العقارات - Real Estate Demo App
"""

import asyncio
import sys
from datetime import datetime
from demo_config import DemoConfig
from demo_services import DemoTelegramService, DemoAIService, DemoNotionService, DemoZohoService
from models.property import PropertyData, PropertyStatus
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DemoRealEstateSystem:
    """النظام التجريبي لإدارة العقارات"""
    
    def __init__(self):
        self.config = DemoConfig()
        self.telegram_service = None
        self.ai_service = None
        self.notion_service = None
        self.zoho_service = None
        
        # إحصائيات التجريب
        self.demo_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "duplicate": 0,
            "multiple": 0
        }
    
    async def initialize_services(self):
        """تهيئة الخدمات التجريبية"""
        logger.info("🔧 تهيئة الخدمات التجريبية...")
        
        self.telegram_service = DemoTelegramService(self.config)
        self.ai_service = DemoAIService(self.config)
        self.notion_service = DemoNotionService(
            self.config.NOTION_INTEGRATION_SECRET,
            self.config.NOTION_PROPERTIES_DB_ID,
            self.config.NOTION_OWNERS_DB_ID
        )
        self.zoho_service = DemoZohoService(
            self.config.ZOHO_CLIENT_ID,
            self.config.ZOHO_CLIENT_SECRET,
            self.config.ZOHO_REFRESH_TOKEN,
            self.config.ZOHO_ACCESS_TOKEN,
            self.config.ZOHO_MODULE_NAME
        )
        
        logger.info("✅ تم تهيئة جميع الخدمات التجريبية")
    
    async def run_complete_demo(self):
        """تشغيل العرض التجريبي الكامل"""
        
        print("🏠 بدء العرض التجريبي لنظام إدارة العقارات")
        print("=" * 60)
        
        # تهيئة الخدمات
        await self.initialize_services()
        
        # عرض معلومات النظام
        self.display_system_info()
        
        print("\n🚀 بدء معالجة العقارات التجريبية...")
        print("=" * 60)
        
        # الخطوة 1: جلب الرسائل من Telegram
        messages = await self.fetch_demo_messages()
        
        # الخطوة 2: معالجة كل رسالة
        for i, message in enumerate(messages, 1):
            print(f"\n📋 معالجة العقار {i}/{len(messages)}")
            print("-" * 40)
            
            await self.process_single_property(message, i)
            
            # توقف قصير بين العقارات
            await asyncio.sleep(1)
        
        # عرض النتائج النهائية
        self.display_final_results()
    
    def display_system_info(self):
        """عرض معلومات النظام"""
        print("📋 معلومات النظام التجريبي:")
        print(f"   📱 قناة التيليجرام: {self.config.TELEGRAM_CHANNEL_ID}")
        print(f"   🗃️ قاعدة بيانات Notion: {self.config.NOTION_PROPERTIES_DB_ID}")
        print(f"   📊 موديول Zoho: {self.config.ZOHO_MODULE_NAME}")
        print(f"   🤖 مزودو AI المتاحون: {', '.join(self.config.get_available_ai_providers())}")
        print(f"   🏷️ وسم النجاح: {self.config.SUCCESS_TAG}")
        print(f"   📅 تاريخ العرض: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async def fetch_demo_messages(self):
        """جلب الرسائل التجريبية"""
        print("📥 جلب الرسائل من قناة التيليجرام...")
        
        async with self.telegram_service as telegram:
            messages = await telegram.get_channel_messages(apply_filter=True)
            print(f"✅ تم جلب {len(messages)} رسالة تجريبية")
            return messages
    
    async def process_single_property(self, message, property_number):
        """معالجة عقار واحد"""
        
        try:
            # إنشاء كائن العقار
            property_data = PropertyData()
            property_data.telegram_message_id = message["message_id"]
            property_data.raw_text = message["text"]
            property_data.status = PropertyStatus.PENDING
            property_data.serial_number = property_number
            
            print(f"🆔 معرف الرسالة: {message['message_id']}")
            print(f"📄 طول النص: {len(message['text'])} حرف")
            
            # الخطوة 1: استخراج البيانات بالذكاء الاصطناعي
            print("🤖 استخراج البيانات بالذكاء الاصطناعي...")
            extracted_data = await self.ai_service.extract_property_data(message["text"])
            
            if not extracted_data:
                print("❌ فشل في استخراج البيانات")
                self.demo_stats["failed"] += 1
                return
            
            # تحديث بيانات العقار
            temp_property = PropertyData.from_dict(extracted_data)
            self.copy_extracted_data(property_data, temp_property, extracted_data)
            
            print(f"   🏘️ المنطقة: {property_data.region}")
            print(f"   🏠 نوع الوحدة: {property_data.unit_type}")
            print(f"   📐 المساحة: {property_data.area} متر")
            print(f"   💰 السعر: {property_data.price} جنيه")
            print(f"   👤 المالك: {property_data.owner_name}")
            
            # الخطوة 2: التحقق من صحة البيانات
            print("🔍 التحقق من صحة البيانات...")
            is_valid, errors = await self.ai_service.validate_property_data(property_data.to_dict())
            
            if not is_valid:
                print(f"⚠️ بيانات ناقصة: {', '.join(errors)}")
                self.demo_stats["failed"] += 1
                return
            
            # الخطوة 3: تصنيف العقار
            print("🏷️ تصنيف العقار...")
            classification = await self.classify_property(property_data)
            print(f"   📊 التصنيف: {classification}")
            
            # الخطوة 4: معالجة حسب التصنيف
            success = await self.process_by_classification(property_data, classification)
            
            if success:
                print("✅ تم معالجة العقار بنجاح")
                self.demo_stats["successful"] += 1
                
                if classification == "عقار مكرر":
                    self.demo_stats["duplicate"] += 1
                elif classification == "عقار متعدد":
                    self.demo_stats["multiple"] += 1
            else:
                print("❌ فشل في معالجة العقار")
                self.demo_stats["failed"] += 1
            
            self.demo_stats["total_processed"] += 1
            
        except Exception as e:
            print(f"❌ خطأ في معالجة العقار: {e}")
            self.demo_stats["failed"] += 1
            self.demo_stats["total_processed"] += 1
    
    def copy_extracted_data(self, property_data, temp_property, extracted_data):
        """نسخ البيانات المستخرجة"""
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
        property_data.statement = extracted_data.get("البيان", "")
        property_data.ai_extracted = True
    
    async def classify_property(self, property_data):
        """تصنيف العقار"""
        
        # البحث عن عقارات مكررة
        duplicate_properties = await self.notion_service.find_duplicate_properties(
            property_data.owner_phone,
            property_data.region,
            property_data.unit_type,
            property_data.unit_condition,
            property_data.area,
            property_data.floor
        )
        
        if duplicate_properties:
            return "عقار مكرر"
        
        # البحث عن عقارات للمالك نفسه
        owner_properties = await self.notion_service.find_owner_properties(property_data.owner_phone)
        
        if owner_properties:
            return "عقار متعدد"
        
        return "عقار جديد"
    
    async def process_by_classification(self, property_data, classification):
        """معالجة حسب التصنيف"""
        
        try:
            if classification == "عقار جديد":
                return await self.process_new_property(property_data)
            elif classification == "عقار متعدد":
                return await self.process_multiple_property(property_data)
            elif classification == "عقار مكرر":
                return await self.process_duplicate_property(property_data)
            
            return False
            
        except Exception as e:
            print(f"❌ خطأ في المعالجة: {e}")
            return False
    
    async def process_new_property(self, property_data):
        """معالجة عقار جديد"""
        
        # إنشاء صفحة مالك في Notion
        print("👤 إنشاء صفحة المالك في Notion...")
        owner_id = await self.notion_service.create_owner_page(property_data.to_dict())
        property_data.notion_owner_id = owner_id
        
        # إنشاء صفحة عقار في Notion
        print("🏠 إنشاء صفحة العقار في Notion...")
        property_id = await self.notion_service.create_property_page(property_data.to_dict(), owner_id)
        property_data.notion_property_id = property_id
        
        # إرسال البيانات إلى Zoho
        print("📊 إنشاء السجل في Zoho CRM...")
        async with self.zoho_service as zoho:
            record_id = await zoho.create_record(property_data.to_dict())
            property_data.zoho_record_id = record_id
        
        # إرسال إشعار نجاح
        print("📲 إرسال إشعار النجاح...")
        await self.send_success_notification(property_data, "عقار جديد")
        
        return True
    
    async def process_multiple_property(self, property_data):
        """معالجة عقار متعدد"""
        
        # البحث عن المالك الموجود
        print("🔍 البحث عن المالك الموجود...")
        existing_owner = await self.notion_service.search_owner(property_data.owner_phone)
        
        # إنشاء صفحة عقار جديدة
        print("🏠 إنشاء صفحة العقار (مرتبطة بالمالك الموجود)...")
        property_id = await self.notion_service.create_property_page(
            property_data.to_dict(), existing_owner['id'] if existing_owner else None
        )
        property_data.notion_property_id = property_id
        
        # تحديث Zoho
        print("📊 تحديث السجل في Zoho CRM...")
        async with self.zoho_service as zoho:
            record_id = await zoho.create_record(property_data.to_dict())
            property_data.zoho_record_id = record_id
        
        # إرسال إشعار
        print("📲 إرسال إشعار العقار المتعدد...")
        await self.send_success_notification(property_data, "عقار متعدد")
        
        return True
    
    async def process_duplicate_property(self, property_data):
        """معالجة عقار مكرر"""
        
        print("🔄 معالجة العقار المكرر...")
        
        # إرسال إشعار تكرار
        print("📲 إرسال إشعار التكرار...")
        await self.send_duplicate_notification(property_data)
        
        return True
    
    async def send_success_notification(self, property_data, classification):
        """إرسال إشعار نجاح"""
        
        async with self.telegram_service as telegram:
            # حذف الرسالة الأصلية وإرسال رسالة منسقة
            await telegram.delete_message(property_data.telegram_message_id)
            
            success_message = telegram.format_success_message(property_data.to_dict())
            await telegram.send_message_to_channel(success_message)
            
            # إرسال إشعار
            notification = telegram.format_property_notification(
                property_data.to_dict(), classification
            )
            await telegram.send_notification(notification)
    
    async def send_duplicate_notification(self, property_data):
        """إرسال إشعار تكرار"""
        
        async with self.telegram_service as telegram:
            notification = telegram.format_property_notification(
                property_data.to_dict(), "عقار مكرر"
            )
            await telegram.send_notification(notification)
    
    def display_final_results(self):
        """عرض النتائج النهائية"""
        
        print("\n" + "=" * 60)
        print("📊 نتائج العرض التجريبي:")
        print("=" * 60)
        print(f"📈 إجمالي العقارات المعالجة: {self.demo_stats['total_processed']}")
        print(f"✅ عقارات ناجحة: {self.demo_stats['successful']}")
        print(f"❌ عقارات فاشلة: {self.demo_stats['failed']}")
        print(f"🔄 عقارات مكررة: {self.demo_stats['duplicate']}")
        print(f"📊 عقارات متعددة: {self.demo_stats['multiple']}")
        
        if self.demo_stats['total_processed'] > 0:
            success_rate = (self.demo_stats['successful'] / self.demo_stats['total_processed']) * 100
            print(f"📈 معدل النجاح: {success_rate:.1f}%")
        
        print("\n🎯 ميزات النظام المعروضة:")
        print("   🤖 استخراج البيانات بالذكاء الاصطناعي")
        print("   🔍 التحقق من صحة البيانات")
        print("   🏷️ تصنيف العقارات (جديد/مكرر/متعدد)")
        print("   📝 تخزين في Notion (المالكين والعقارات)")
        print("   📊 تكامل مع Zoho CRM")
        print("   📱 إشعارات Telegram")
        print("   🏷️ نظام الوسوم المتقدم")
        
        print("\n🌐 لتشغيل الواجهة الويب:")
        print("   python -m demo_web_interface")
        
        print("\n🎉 تم إكمال العرض التجريبي بنجاح!")
        print("=" * 60)

async def main():
    """الدالة الرئيسية للعرض التجريبي"""
    
    demo_system = DemoRealEstateSystem()
    
    try:
        await demo_system.run_complete_demo()
        
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف العرض التجريبي...")
    except Exception as e:
        logger.error(f"❌ خطأ في العرض التجريبي: {e}")

def print_welcome_banner():
    """طباعة بانر الترحيب"""
    
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                     العرض التجريبي                          ║
║               نظام إدارة العقارات المحدث v2.0                ║
║                Real Estate Demo System                       ║
╠══════════════════════════════════════════════════════════════╣
║  🎯 عرض شامل لجميع وظائف النظام                            ║
║  🤖 معالجة تجريبية بالذكاء الاصطناعي                       ║
║  📱 محاكاة تكامل مع Telegram وNotion وZoho                   ║
║  📊 إحصائيات ونتائج مفصلة                                 ║
║  🌐 واجهة ويب تفاعلية                                      ║
╚══════════════════════════════════════════════════════════════╝
    """
    
    print(banner)

if __name__ == "__main__":
    print_welcome_banner()
    
    # التحقق من Python version
    if sys.version_info < (3, 8):
        print("❌ يتطلب Python 3.8 أو أحدث")
        sys.exit(1)
    
    print("✅ بدء العرض التجريبي...")
    
    # تشغيل العرض التجريبي
    asyncio.run(main())
