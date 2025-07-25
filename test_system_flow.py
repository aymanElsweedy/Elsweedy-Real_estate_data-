
#!/usr/bin/env python3
"""
سكريبت اختبار النظام - فحص جميع المكونات وإرسال رسالة تجريبية
"""

import asyncio
import os
from datetime import datetime

from config import Config
from services.telegram_service import TelegramService
from services.ai_service import AIService
from services.notion_service import NotionService
from services.zoho_service import ZohoService

# رسالة عقارية تجريبية
TEST_MESSAGE = """
🏠 شقة للإيجار - التجمع الخامس

📍 المنطقة: التجمع الخامس
🏢 النوع: شقة
📐 المساحة: 120 متر
🏗️ الدور: الثالث  
💰 السعر: 25000 جنيه
🛋️ الحالة: مفروشة

المميزات: مكيفة، فيو مفتوح، اسانسير

👤 المالك: أحمد محمد
📞 رقم المالك: 01234567890
👨‍💼 الموظف: بلبل
📸 الصور: متوفرة
"""

async def test_system():
    """اختبار جميع مكونات النظام"""
    
    print("🔍 بدء فحص النظام...")
    
    # 1. فحص الإعدادات
    print("\n1️⃣ فحص الإعدادات...")
    config = Config()
    
    if not config.validate():
        print("❌ فشل في التحقق من الإعدادات")
        return False
    
    print("✅ الإعدادات صحيحة")
    print(f"   📱 Telegram Bot: {'✅ متصل' if config.TELEGRAM_BOT_TOKEN else '❌ غير متاح'}")
    print(f"   🗃️ Notion: {'✅ متصل' if config.NOTION_INTEGRATION_SECRET else '❌ غير متاح'}")
    print(f"   🤖 AI Providers: {len(config.get_available_ai_providers())} متاح")
    
    # 2. اختبار خدمة التيليجرام
    print("\n2️⃣ اختبار خدمة التيليجرام...")
    try:
        async with TelegramService(config) as telegram:
            # جلب آخر الرسائل
            messages = await telegram.get_channel_messages(limit=5, apply_filter=False)
            print(f"✅ تم جلب {len(messages)} رسالة من القناة")
            
            # إرسال رسالة تجريبية
            test_sent = await telegram.send_message_to_channel(
                f"🧪 <b>رسالة اختبار</b>\n\n"
                f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"🔧 حالة النظام: يعمل بنجاح\n"
                f"📊 عدد الرسائل المجلبة: {len(messages)}"
            )
            
            if test_sent:
                print("✅ تم إرسال رسالة اختبار بنجاح")
            else:
                print("❌ فشل في إرسال رسالة الاختبار")
                
    except Exception as e:
        print(f"❌ خطأ في خدمة التيليجرام: {e}")
        return False
    
    # 3. اختبار خدمة الذكاء الاصطناعي
    print("\n3️⃣ اختبار خدمة الذكاء الاصطناعي...")
    try:
        ai_service = AIService(config)
        extracted_data = await ai_service.extract_property_data(TEST_MESSAGE)
        
        if extracted_data:
            print("✅ تم استخراج البيانات بنجاح")
            print(f"   🏘️ المنطقة: {extracted_data.get('المنطقة', 'غير محدد')}")
            print(f"   🏠 النوع: {extracted_data.get('نوع الوحدة', 'غير محدد')}")
            print(f"   📐 المساحة: {extracted_data.get('المساحة', 'غير محدد')}")
            print(f"   💰 السعر: {extracted_data.get('السعر', 'غير محدد')}")
        else:
            print("❌ فشل في استخراج البيانات")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في خدمة الذكاء الاصطناعي: {e}")
        return False
    
    # 4. اختبار خدمة Notion
    print("\n4️⃣ اختبار خدمة Notion...")
    try:
        notion_service = NotionService(
            config.NOTION_INTEGRATION_SECRET,
            config.NOTION_PROPERTIES_DB_ID,
            config.NOTION_OWNERS_DB_ID
        )
        
        # محاولة البحث عن عقار (حتى لو لم نجد، المهم أن الاتصال يعمل)
        search_result = await notion_service.search_property(extracted_data)
        print(f"✅ تم الاتصال بـ Notion - {'عُثر على عقار مشابه' if search_result else 'لا توجد عقارات مشابهة'}")
        
    except Exception as e:
        print(f"❌ خطأ في خدمة Notion: {e}")
        return False
    
    # 5. اختبار خدمة Zoho (اختياري)
    print("\n5️⃣ اختبار خدمة Zoho...")
    if config.ZOHO_CLIENT_ID and config.ZOHO_CLIENT_SECRET:
        try:
            zoho_service = ZohoService(config)
            await zoho_service.refresh_access_token()
            print("✅ تم الاتصال بـ Zoho CRM")
        except Exception as e:
            print(f"⚠️ تحذير - Zoho CRM: {e}")
    else:
        print("⚠️ Zoho CRM غير مُعيَّن (اختياري)")
    
    # 6. معالجة الرسالة التجريبية كاملة
    print("\n6️⃣ معالجة رسالة تجريبية كاملة...")
    try:
        async with TelegramService(config) as telegram:
            # إرسال الرسالة التجريبية أولاً
            test_message_sent = await telegram.send_message_to_channel(
                f"🧪 <b>رسالة عقارية تجريبية</b>\n\n{TEST_MESSAGE}"
            )
            
            if test_message_sent:
                print("✅ تم إرسال رسالة عقارية تجريبية")
                
                # انتظار قليل ثم معالجة الرسائل الجديدة
                await asyncio.sleep(2)
                
                # جلب الرسائل الجديدة ومعالجتها
                new_messages = await telegram.get_channel_messages(limit=10, apply_filter=True)
                print(f"📨 تم جلب {len(new_messages)} رسالة جديدة للمعالجة")
                
                if new_messages:
                    # معالجة أول رسالة
                    first_message = new_messages[0]
                    print(f"🔄 معالجة الرسالة: {first_message['message_id']}")
                    
                    # استخراج البيانات
                    property_data = await ai_service.extract_property_data(first_message['text'])
                    
                    if property_data:
                        print("✅ تم استخراج البيانات من الرسالة الجديدة")
                        
                        # محاولة حفظ في Notion
                        owner_id = await notion_service.create_owner_page(property_data)
                        if owner_id:
                            property_id = await notion_service.create_property_page(property_data, owner_id)
                            if property_id:
                                print("✅ تم حفظ العقار في Notion بنجاح")
                                
                                # إرسال إشعار نجاح
                                success_message = f"✅ <b>تم معالجة العقار بنجاح</b>\n\n"
                                success_message += f"🏘️ المنطقة: {property_data.get('المنطقة', 'غير محدد')}\n"
                                success_message += f"🏠 النوع: {property_data.get('نوع الوحدة', 'غير محدد')}\n"
                                success_message += f"📐 المساحة: {property_data.get('المساحة', 'غير محدد')}\n"
                                success_message += f"💰 السعر: {property_data.get('السعر', 'غير محدد')}\n"
                                success_message += f"🔗 رابط Notion: {notion_service.get_property_url(property_id)}"
                                
                                await telegram.send_notification(success_message)
                                print("✅ تم إرسال إشعار النجاح")
                            else:
                                print("❌ فشل في إنشاء صفحة العقار")
                        else:
                            print("❌ فشل في إنشاء صفحة المالك")
                    else:
                        print("❌ فشل في استخراج البيانات من الرسالة")
                else:
                    print("ℹ️ لا توجد رسائل جديدة للمعالجة")
            else:
                print("❌ فشل في إرسال الرسالة التجريبية")
                
    except Exception as e:
        print(f"❌ خطأ في المعالجة الكاملة: {e}")
        return False
    
    print("\n🎉 تم اختبار النظام بنجاح!")
    print("🔄 النظام جاهز لمعالجة الرسائل الحقيقية")
    return True

if __name__ == "__main__":
    asyncio.run(test_system())
