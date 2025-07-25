"""
نظام التسجيل - Logging System
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logger(name: str, log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """إعداد نظام التسجيل"""
    
    # إنشاء مجلد السجلات إذا لم يكن موجود
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # اسم ملف السجل
    if not log_file:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = logs_dir / f"real_estate_{timestamp}.log"
    
    # إعداد المُسجل
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # إزالة المعالجات الموجودة لتجنب التكرار
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # إعداد التنسيق
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # معالج الملف
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # معالج وحدة التحكم
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # تنسيق ملون لوحدة التحكم
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

class ColoredFormatter(logging.Formatter):
    """مُنسق ملون للسجلات"""
    
    # ألوان ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # سماوي
        'INFO': '\033[32m',       # أخضر
        'WARNING': '\033[33m',    # أصفر
        'ERROR': '\033[31m',      # أحمر
        'CRITICAL': '\033[35m',   # بنفسجي
        'RESET': '\033[0m'        # إعادة تعيين
    }
    
    def format(self, record):
        """تنسيق السجل مع الألوان"""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # تلوين مستوى السجل
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        return super().format(record)

class PropertyLogger:
    """مُسجل خاص بالعقارات"""
    
    def __init__(self, property_id: str = None):
        self.property_id = property_id
        self.logger = setup_logger(f"property.{property_id}" if property_id else "property")
    
    def log_processing_start(self, property_data: dict):
        """تسجيل بدء معالجة العقار"""
        self.logger.info(f"🏠 بدء معالجة العقار - المنطقة: {property_data.get('المنطقة', 'غير محدد')}")
    
    def log_processing_step(self, step: str, details: str = ""):
        """تسجيل خطوة في المعالجة"""
        message = f"⚙️ {step}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_classification(self, classification: str, reason: str = ""):
        """تسجيل تصنيف العقار"""
        icons = {
            "عقار جديد": "🆕",
            "عقار مكرر": "🔄",
            "عقار متعدد": "📊", 
            "عقار ناجح": "✅",
            "عقار فاشل": "❌"
        }
        
        icon = icons.get(classification, "🏠")
        message = f"{icon} تصنيف العقار: {classification}"
        if reason:
            message += f" - السبب: {reason}"
        
        self.logger.info(message)
    
    def log_success(self, operation: str, details: str = ""):
        """تسجيل عملية ناجحة"""
        message = f"✅ {operation}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_error(self, operation: str, error: str):
        """تسجيل خطأ"""
        self.logger.error(f"❌ {operation} - خطأ: {error}")
    
    def log_warning(self, operation: str, warning: str):
        """تسجيل تحذير"""
        self.logger.warning(f"⚠️ {operation} - تحذير: {warning}")
    
    def log_processing_complete(self, success: bool, final_status: str = ""):
        """تسجيل اكتمال المعالجة"""
        if success:
            self.logger.info(f"🎉 اكتملت معالجة العقار بنجاح - الحالة النهائية: {final_status}")
        else:
            self.logger.error(f"💥 فشلت معالجة العقار - الحالة النهائية: {final_status}")

# إعداد المسجل الرئيسي
main_logger = setup_logger("real_estate_system")

def log_system_event(event: str, level: str = "info", details: str = ""):
    """تسجيل أحداث النظام"""
    message = f"🏢 {event}"
    if details:
        message += f" - {details}"
    
    if level == "error":
        main_logger.error(message)
    elif level == "warning":
        main_logger.warning(message)
    elif level == "debug":
        main_logger.debug(message)
    else:
        main_logger.info(message)
