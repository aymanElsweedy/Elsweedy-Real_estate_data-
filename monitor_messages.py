
#!/usr/bin/env python3
"""
مراقب الرسائل المباشر - Real-time Message Monitor
"""

import asyncio
from datetime import datetime
from config import Config
from services.telegram_service import TelegramService

async def monitor_messages():
    """مراقبة الرسائل الواردة في الوقت الفعلي"""
    
    print("📡 بدء مراقبة رسائل التيليجرام...")
    print("🔄 سيتم فحص الرسائل كل 10 ثوانٍ")
    print("⏸️ اضغط Ctrl+C للإيقاف")
    print("=" * 50)
    
    config = Config()
    last_message_id = 0
    
    try:
        while True:
            async with TelegramService(config) as telegram:
                # جلب آخر الرسائل
                messages = await telegram.get_channel_messages(limit=20, apply_filter=False)
                
                if messages:
                    # ترتيب الرسائل حسب التاريخ
                    messages.sort(key=lambda x: x['message_id'])
                    
                    # عرض الرسائل الجديدة فقط
                    new_messages = [msg for msg in messages if msg['message_id'] > last_message_id]
                    
                    if new_messages:
                        print(f"\n📨 {len(new_messages)} رسالة جديدة:")
                        
                        for msg in new_messages:
                            print(f"\n🆔 رقم الرسالة: {msg['message_id']}")
                            print(f"⏰ التاريخ: {msg['date'].strftime('%Y-%m-%d %H:%M:%S')}")
                            print(f"📝 النص: {msg['text'][:100]}...")
                            
                            # فحص إذا كانت الرسالة تحتوي على وسم
                            if config.SUCCESS_TAG in msg['text']:
                                print("   ✅ رسالة موسومة - تم تخطيها")
                            elif config.FAILED_TAG in msg['text']:
                                print("   ❌ رسالة فاشلة - تم تخطيها")
                            elif config.DUPLICATE_TAG in msg['text']:
                                print("   🔄 رسالة مكررة - تم تخطيها")
                            else:
                                print("   🆕 رسالة جديدة - قابلة للمعالجة")
                            
                            last_message_id = max(last_message_id, msg['message_id'])
                    else:
                        print(f"🔄 {datetime.now().strftime('%H:%M:%S')} - لا توجد رسائل جديدة (آخر معالجة: {last_message_id})")
                else:
                    print(f"⚠️ {datetime.now().strftime('%H:%M:%S')} - لم يتم جلب أي رسائل")
                
                # انتظار 10 ثوانٍ
                await asyncio.sleep(10)
                
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف المراقبة")
    except Exception as e:
        print(f"\n❌ خطأ في المراقبة: {e}")

if __name__ == "__main__":
    asyncio.run(monitor_messages())
