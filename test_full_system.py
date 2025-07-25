
#!/usr/bin/env python3
"""
اختبار شامل للنظام المحدث مع الدليل الجديد
سيقوم بمعالجة جميع الرسائل الموجودة على القناة
"""

import asyncio
import os
import json
from datetime import datetime
from config import Config
from services.telegram_service import TelegramService
from services.ai_service import AIService
from services.notion_service import NotionService
from services.zoho_service import ZohoService
from utils.logger import setup_logger

logger = setup_logger(__name__)

async def test_full_system():
    """اختبار النظام الكامل مع معالجة جميع الرسائل"""
    
    print("🏠 بدء اختبار نظام إدارة العقارات المحدث")
    print("=" * 60)
    
    # إعداد التكوين
    config = Config()
    
    # التحقق من المتطلبات
    if not config.validate():
        print("❌ فشل في التحقق من الإعدادات")
        return False
    
    try:
        # إعداد الخدمات
        async with TelegramService(config) as telegram_service:
            ai_service = AIService(config)
            
            # طباعة معلومات النظام
            print(f"📱 قناة التيليجرام: {config.TELEGRAM_CHANNEL_ID}")
            print(f"🤖 مزودو AI المتاحون: {', '.join(config.get_available_ai_providers())}")
            print(f"🏷️ وسم النجاح: {config.SUCCESS_TAG}")
            print(f"❌ وسم الفشل: {config.FAILED_TAG}")
            print("=" * 60)
            
            # الحصول على جميع رسائل القناة
            print("📥 الحصول على رسائل القناة...")
            messages = await telegram_service.get_channel_messages(limit=50, apply_filter=True)
            
            if not messages:
                print("⚠️ لم يتم العثور على رسائل للمعالجة")
                print("💡 تأكد من وجود رسائل في القناة أو قم بإرسال رسائل تجريبية")
                return False
            
            print(f"✅ تم العثور على {len(messages)} رسالة للمعالجة")
            print("=" * 60)
            
            # معالجة كل رسالة
            processed_count = 0
            successful_count = 0
            failed_count = 0
            
            for i, message in enumerate(messages, 1):
                print(f"\n📝 معالجة الرسالة {i}/{len(messages)}")
                print(f"🆔 معرف الرسالة: {message.get('message_id')}")
                print(f"📅 تاريخ الرسالة: {message.get('date')}")
                
                # النص الخام
                raw_text = message.get('text', '').strip()
                if not raw_text:
                    print("⚠️ رسالة فارغة، تخطي...")
                    continue
                
                print(f"📄 طول النص: {len(raw_text)} حرف")
                
                # استخراج البيانات بالذكاء الاصطناعي
                print("🤖 بدء استخراج البيانات...")
                
                try:
                    property_data = await ai_service.extract_property_data(raw_text)
                    
                    if property_data:
                        print("✅ تم استخراج البيانات بنجاح!")
                        
                        # طباعة البيانات المستخرجة
                        print("\n📋 البيانات المستخرجة:")
                        print(f"   🏘️ المنطقة: {property_data.get('المنطقة', 'غير محدد')}")
                        print(f"   🏠 نوع الوحدة: {property_data.get('نوع الوحدة', 'غير محدد')}")
                        print(f"   🔑 حالة الوحدة: {property_data.get('حالة الوحدة', 'غير محدد')}")
                        print(f"   📐 المساحة: {property_data.get('المساحة', 'غير محدد')} متر")
                        print(f"   💰 السعر: {property_data.get('السعر', 'غير محدد')} جنيه")
                        print(f"   🆔 كود الوحدة: {property_data.get('كود الوحدة', 'غير محدد')}")
                        
                        # طباعة البيان المدمج
                        statement = property_data.get('البيان', '')
                        if statement:
                            print(f"\n📝 البيان المدمج:")
                            for line in statement.split('\n'):
                                if line.strip():
                                    print(f"   {line}")
                        
                        # التحقق من صحة البيانات
                        is_valid, errors = await ai_service.validate_property_data(property_data)
                        
                        if is_valid:
                            print("✅ البيانات صحيحة ومكتملة")
                            successful_count += 1
                            
                            # إضافة وسم النجاح (محاكاة)
                            print("🏷️ سيتم إضافة وسم النجاح للرسالة")
                            
                        else:
                            print("⚠️ مشاكل في البيانات:")
                            for error in errors:
                                print(f"   - {error}")
                            failed_count += 1
                            
                            # إضافة وسم الفشل (محاكاة)
                            print("❌ سيتم إضافة وسم الفشل للرسالة")
                    
                    else:
                        print("❌ فشل في استخراج البيانات")
                        failed_count += 1
                        
                except Exception as e:
                    print(f"❌ خطأ في معالجة الرسالة: {e}")
                    failed_count += 1
                
                processed_count += 1
                
                # توقف قصير بين الرسائل
                await asyncio.sleep(2)
            
            # طباعة الإحصائيات النهائية
            print("\n" + "=" * 60)
            print("📊 إحصائيات المعالجة:")
            print(f"   📝 إجمالي الرسائل المعالجة: {processed_count}")
            print(f"   ✅ رسائل ناجحة: {successful_count}")
            print(f"   ❌ رسائل فاشلة: {failed_count}")
            print(f"   📈 معدل النجاح: {(successful_count/processed_count)*100:.1f}%" if processed_count > 0 else "0%")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار النظام: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    success = await test_full_system()
    
    if success:
        print("\n🎉 تم اختبار النظام بنجاح!")
        print("💡 يمكنك الآن تشغيل النظام الكامل باستخدام:")
        print("   python main.py")
    else:
        print("\n❌ فشل في اختبار النظام")
        print("💡 تحقق من الإعدادات والاتصال بالخدمات")

if __name__ == "__main__":
    asyncio.run(main())
