
#!/usr/bin/env python3
"""
نظام إدارة العقارات المحدث - Real Estate Management System v2.0
نظام شامل لمعالجة وإدارة بيانات العقارات مع سلسلة AI محدثة والتكامل مع Telegram وNotion وZoho CRM
"""

import asyncio
import sys
import os
from datetime import datetime
from utils.logger import setup_logger
from config import Config
from processors.property_processor import PropertyProcessor
from web_interface import app

logger = setup_logger(__name__)

class RealEstateSystem:
    """النظام الرئيسي لإدارة العقارات المحدث"""
    
    def __init__(self):
        self.config = Config()
        self.processor = PropertyProcessor()
        self.is_running = False
        
    async def start(self):
        """بدء تشغيل النظام المحدث"""
        logger.info("🏠 بدء تشغيل نظام إدارة العقارات المحدث v2.0...")
        
        try:
            # التحقق من المتطلبات
            if not self.config.validate():
                logger.error("❌ فشل في التحقق من الإعدادات")
                return False
            
            # طباعة معلومات التكوين
            self._print_system_info()
            
            # بدء المعالج
            self.is_running = True
            await self.processor.start()
            
            logger.info("✅ تم تشغيل النظام بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل النظام: {e}")
            return False
    
    async def stop(self):
        """إيقاف النظام"""
        logger.info("🛑 إيقاف النظام...")
        self.is_running = False
        if self.processor:
            await self.processor.stop()
        logger.info("✅ تم إيقاف النظام")

    async def process_all_channel_messages(self):
        """معالجة جميع رسائل القناة بشكل مستمر"""
        if self.is_running:
            await self.processor.process_all_pending()
    
    def _print_system_info(self):
        """طباعة معلومات النظام"""
        
        logger.info("📋 معلومات النظام:")
        logger.info(f"   📱 قناة التيليجرام: {self.config.TELEGRAM_CHANNEL_ID}")
        logger.info(f"   📁 قناة الأرشيف: {self.config.TELEGRAM_ARCHIVE_CHANNEL_ID or 'غير مُعيَّنة'}")
        logger.info(f"   🗃️ موديول Zoho: {self.config.ZOHO_MODULE_NAME}")
        logger.info(f"   🤖 مزودو AI المتاحون: {', '.join(self.config.get_available_ai_providers())}")
        logger.info(f"   🏷️ وسم النجاح: {self.config.SUCCESS_TAG}")
        logger.info(f"   📅 فلتر التاريخ: {'مُفعَّل' if self.config.APPLY_DATE_FILTER else 'مُعطَّل'}")
        
        if self.config.APPLY_DATE_FILTER and self.config.LAST_SUCCESS_DATE:
            logger.info(f"   📅 آخر تاريخ نجاح: {self.config.LAST_SUCCESS_DATE}")

async def main():
    """الدالة الرئيسية المحدثة"""
    system = RealEstateSystem()
    
    try:
        # بدء النظام
        if await system.start():
            print("🏠 نظام إدارة العقارات المحدث v2.0 يعمل...")
            print("📊 المميزات الجديدة:")
            print("   🤖 سلسلة AI محدثة: Gemini → OpenAI → Copilot → Mistral → Groq")
            print("   🏷️ نظام وسم متقدم مع فلترة ذكية")
            print("   📝 حقل البيان المدمج (9 حقول)")
            print("   🤖 بوت إشعارات منفصل")
            print("   🗃️ موديول Zoho Aqar الجديد")
            print("   🔍 مطابقة مباشرة من Notion")
            print("🌐 الواجهة متاحة على: http://0.0.0.0:5000")
            print("⏸️  اضغط Ctrl+C للتوقف")
            print("=" * 60)
            
            # تشغيل الواجهة والمعالجة
            await asyncio.gather(
                run_web_interface(),
                system.process_all_channel_messages()
            )
        else:
            print("❌ فشل في تشغيل النظام")
            
    except KeyboardInterrupt:
        print("\n🛑 تم طلب إيقاف النظام...")
    except Exception as e:
        logger.error(f"❌ خطأ غير متوقع: {e}")
    finally:
        await system.stop()

async def run_web_interface():
    """تشغيل الواجهة الويب"""
    import uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=5000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

def print_welcome_banner():
    """طباعة بانر الترحيب"""
    
    banner = """
╔══════════════════════════════════════════════════════════════╗
║               نظام إدارة العقارات المحدث v2.0                ║
║                Real Estate Management System                 ║
╠══════════════════════════════════════════════════════════════╣
║  🏠 معالجة ذكية للعقارات بسلسلة AI متقدمة                    ║
║  📱 تكامل مع Telegram مع نظام وسم متطور                      ║
║  🗃️ تخزين في Notion و Zoho CRM (موديول Aqar الجديد)         ║
║  📊 تقارير يومية وإحصائيات مفصلة                           ║
║  🤖 5 مزودين للذكاء الاصطناعي + تحليل منطقي               ║
╚══════════════════════════════════════════════════════════════╝
    """
    
    print(banner)

if __name__ == "__main__":
    # طباعة بانر الترحيب
    print_welcome_banner()
    
    # التحقق من Python version
    if sys.version_info < (3, 8):
        print("❌ يتطلب Python 3.8 أو أحدث")
        sys.exit(1)
    
    # التحقق من الإعدادات عبر Config
    config = Config()
    if not config.validate():
        print("❌ فشل في التحقق من الإعدادات")
        print("💡 تأكد من إضافة البيانات المطلوبة أو استخدام القيم الافتراضية")
        sys.exit(1)
    
    print(f"✅ تم العثور على {len(config.get_available_ai_providers())} مزود ذكاء اصطناعي")
    
    # تشغيل النظام
    asyncio.run(main())
