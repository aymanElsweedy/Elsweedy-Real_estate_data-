#!/usr/bin/env python3
"""
نظام إدارة العقارات - Real Estate Management System
نظام شامل لمعالجة وإدارة بيانات العقارات مع التكامل مع Telegram وNotion وZoho CRM
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
    """النظام الرئيسي لإدارة العقارات"""
    
    def __init__(self):
        self.config = Config()
        self.processor = PropertyProcessor()
        self.is_running = False
        
    async def start(self):
        """بدء تشغيل النظام"""
        logger.info("🏠 بدء تشغيل نظام إدارة العقارات...")
        
        try:
            # التحقق من المتطلبات
            if not self.config.validate():
                logger.error("❌ فشل في التحقق من الإعدادات")
                return False
                
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

    async def process_pending_properties(self):
        """معالجة العقارات المعلقة"""
        if self.is_running:
            await self.processor.process_all_pending()

async def main():
    """الدالة الرئيسية"""
    system = RealEstateSystem()
    
    try:
        # بدء النظام
        if await system.start():
            print("🏠 نظام إدارة العقارات يعمل...")
            print("🌐 الواجهة متاحة على: http://0.0.0.0:5000")
            print("⏸️  اضغط Ctrl+C للتوقف")
            
            # تشغيل الواجهة والمعالجة
            await asyncio.gather(
                run_web_interface(),
                system.process_pending_properties()
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

if __name__ == "__main__":
    # التحقق من Python version
    if sys.version_info < (3, 8):
        print("❌ يتطلب Python 3.8 أو أحدث")
        sys.exit(1)
    
    # تشغيل النظام
    asyncio.run(main())
