
#!/usr/bin/env python3
"""
اختبار شامل للنظام: إرسال رسائل جديدة ومعالجة جميع الرسائل الموجودة في القناة
"""

import asyncio
import os
from datetime import datetime
from config import Config
from services.telegram_service import TelegramService
from services.ai_service import AIService
from utils.logger import setup_logger

logger = setup_logger(__name__)

# رسائل عقارية جديدة للإرسال والاختبار
NEW_PROPERTY_MESSAGES = [
    """
🏠 شقة للإيجار - التجمع الخامس

المنطقة: احياء تجمع
النوع: شقة سكنية
المساحة: 150 متر مربع
الدور: الثاني
السعر: 28000 جنيه شهرياً
الحالة: مفروش

المميزات:
- تشطيب سوبر لوكس
- حديقه
- اسانسير
- فيو مفتوح

للتواصل: بلبل - 01234567890
المالك: احمد محمود - 01012345678
متوفر صور للوحدة

العنوان: التجمع الخامس، القاهرة الجديدة
متاح للمعاينة
    """,
    """
🏡 شقة مفروشة - اندلس

المنطقة: اندلس
النوع: شقة
المساحة: 130 متر
الدور: دور تالت
السعر: 20000 جنيه شهرياً
الحالة: مفروش

المميزات:
- مكيفه
- فيو مفتوح
- اسانسير
- انترنت
- اجهزه كهربائيه

للتواصل: يوسف عماد - 01987654321
المالك: هدي المفتي - 01000011109
بدون صور حالياً

العنوان: اندلس، القاهرة الجديدة
غير متاحه حالياً
    """,
    """
🏢 شقة تمليك - جاردينيا

المنطقة: جاردينيا
النوع: شقة
المساحة: 200 متر
الدور: دور خامس
السعر: 2500000 جنيه
الحالة: تمليك

المميزات:
- تشطيب سوبر لوكس
- اسانسير
- فيو جاردن
- مسجله شهر عقاري

للتواصل: محمود سامي - 01555666777
المالك: أميرة خالد - 01333444555
متوفر صور

العنوان: كمبوند جاردينيا، الحي الخامس
متاح للمعاينة
    """
]

async def send_new_messages_to_channel():
    """إرسال رسائل عقارية جديدة إلى القناة"""
    
    config = Config()
    
    print("📤 إرسال رسائل عقارية جديدة إلى القناة...")
    
    try:
        async with TelegramService(config) as telegram_service:
            sent_count = 0
            
            for i, message in enumerate(NEW_PROPERTY_MESSAGES, 1):
                print(f"📤 إرسال الرسالة {i}/{len(NEW_PROPERTY_MESSAGES)}")
                
                success = await telegram_service.send_message_to_channel(message)
                
                if success:
                    print(f"✅ تم إرسال الرسالة {i} بنجاح")
                    sent_count += 1
                else:
                    print(f"❌ فشل إرسال الرسالة {i}")
                
                # توقف قصير بين الرسائل
                await asyncio.sleep(3)
            
            print(f"✅ تم إرسال {sent_count}/{len(NEW_PROPERTY_MESSAGES)} رسالة جديدة")
            
            # انتظار لمعالجة الرسائل
            print("⏳ انتظار 10 ثوانِ قبل بدء المعالجة...")
            await asyncio.sleep(10)
            
            return sent_count > 0
            
    except Exception as e:
        print(f"❌ خطأ في إرسال الرسائل: {e}")
        return False

async def process_all_channel_messages():
    """معالجة جميع رسائل القناة"""
    
    config = Config()
    
    print("🔄 بدء معالجة جميع رسائل القناة...")
    
    try:
        async with TelegramService(config) as telegram_service:
            ai_service = AIService(config)
            
            # الحصول على جميع الرسائل
            print("📥 جلب رسائل القناة...")
            messages = await telegram_service.get_channel_messages(limit=100, apply_filter=True)
            
            if not messages:
                print("⚠️ لم يتم العثور على رسائل للمعالجة")
                return False
            
            print(f"📊 تم العثور على {len(messages)} رسالة للمعالجة")
            
            # معالجة كل رسالة
            processed_count = 0
            successful_count = 0
            failed_count = 0
            
            for i, message in enumerate(messages, 1):
                print(f"\n📝 معالجة الرسالة {i}/{len(messages)}")
                print(f"🆔 معرف الرسالة: {message.get('message_id')}")
                
                raw_text = message.get('text', '').strip()
                if not raw_text:
                    print("⚠️ رسالة فارغة، تخطي...")
                    continue
                
                print(f"📄 طول النص: {len(raw_text)} حرف")
                
                try:
                    # استخراج البيانات
                    print("🤖 استخراج البيانات بالذكاء الاصطناعي...")
                    property_data = await ai_service.extract_property_data(raw_text)
                    
                    if property_data:
                        print("✅ تم استخراج البيانات بنجاح!")
                        
                        # عرض البيانات المهمة
                        print(f"   🏘️ المنطقة: {property_data.get('المنطقة', 'غير محدد')}")
                        print(f"   🏠 نوع الوحدة: {property_data.get('نوع الوحدة', 'غير محدد')}")
                        print(f"   📐 المساحة: {property_data.get('المساحة', 'غير محدد')} متر")
                        print(f"   💰 السعر: {property_data.get('السعر', 'غير محدد')} جنيه")
                        print(f"   👤 المالك: {property_data.get('اسم المالك', 'غير محدد')}")
                        
                        # عرض البيان المدمج
                        statement = property_data.get('البيان', '')
                        if statement:
                            print(f"📝 البيان المدمج:")
                            statement_lines = statement.split('\n')[:3]  # أول 3 أسطر فقط
                            for line in statement_lines:
                                if line.strip():
                                    print(f"   {line}")
                            if len(statement.split('\n')) > 3:
                                print("   ...")
                        
                        # التحقق من صحة البيانات
                        is_valid, validation_errors = await ai_service.validate_property_data(property_data)
                        
                        if is_valid:
                            print("✅ البيانات صحيحة ومكتملة")
                            successful_count += 1
                            
                            # محاكاة إضافة وسم النجاح
                            print("🏷️ سيتم إضافة وسم النجاح")
                            
                        else:
                            print(f"⚠️ مشاكل في البيانات ({len(validation_errors)} مشكلة)")
                            for error in validation_errors[:2]:  # أول مشكلتين فقط
                                print(f"   - {error}")
                            if len(validation_errors) > 2:
                                print("   ...")
                            failed_count += 1
                            print("❌ سيتم إضافة وسم الفشل")
                    
                    else:
                        print("❌ فشل في استخراج البيانات")
                        failed_count += 1
                        
                except Exception as e:
                    print(f"❌ خطأ في معالجة الرسالة: {e}")
                    failed_count += 1
                
                processed_count += 1
                
                # توقف قصير بين الرسائل
                await asyncio.sleep(1)
            
            # الإحصائيات النهائية
            print("\n" + "=" * 60)
            print("📊 نتائج المعالجة:")
            print(f"   📝 إجمالي الرسائل: {processed_count}")
            print(f"   ✅ رسائل ناجحة: {successful_count}")
            print(f"   ❌ رسائل فاشلة: {failed_count}")
            
            if processed_count > 0:
                success_rate = (successful_count / processed_count) * 100
                print(f"   📈 معدل النجاح: {success_rate:.1f}%")
            
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في معالجة الرسائل: {e}")
        return False

async def main():
    """الدالة الرئيسية للاختبار الشامل"""
    
    print("🏠 اختبار شامل لنظام إدارة العقارات")
    print("=" * 60)
    
    # التحقق من الإعدادات
    config = Config()
    if not config.validate():
        print("❌ فشل في التحقق من الإعدادات")
        print("💡 تأكد من إضافة جميع متغيرات البيئة المطلوبة")
        return
    
    print("✅ تم التحقق من الإعدادات بنجاح")
    print(f"📱 قناة التليجرام: {config.TELEGRAM_CHANNEL_ID}")
    print(f"🤖 مزودو AI متاحون: {', '.join(config.get_available_ai_providers())}")
    print("=" * 60)
    
    try:
        # الخطوة 1: إرسال رسائل جديدة
        print("\n🚀 الخطوة 1: إرسال رسائل عقارية جديدة")
        send_success = await send_new_messages_to_channel()
        
        if send_success:
            print("✅ تم إرسال الرسائل الجديدة بنجاح")
        else:
            print("⚠️ فشل في إرسال الرسائل الجديدة (سيتم المتابعة)")
        
        # الخطوة 2: معالجة جميع الرسائل
        print("\n🚀 الخطوة 2: معالجة جميع رسائل القناة")
        process_success = await process_all_channel_messages()
        
        if process_success:
            print("\n🎉 تم الاختبار الشامل بنجاح!")
            print("💡 يمكنك الآن تشغيل النظام الكامل:")
            print("   python main.py")
        else:
            print("\n⚠️ حدثت مشاكل في المعالجة")
            print("💡 تحقق من الإعدادات والاتصال بالخدمات")
            
    except Exception as e:
        print(f"\n❌ خطأ في الاختبار الشامل: {e}")

if __name__ == "__main__":
    asyncio.run(main())
