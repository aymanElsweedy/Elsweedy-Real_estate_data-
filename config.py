"""
إعدادات النظام - System Configuration
"""

import os
from typing import Dict, Any, Optional

class Config:
    """فئة إعدادات النظام"""
    
    def __init__(self):
        # Telegram Bot Configuration
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")
        
        # Notion Configuration
        self.NOTION_INTEGRATION_SECRET = os.getenv("NOTION_INTEGRATION_SECRET", "")
        self.NOTION_PROPERTIES_DB_ID = os.getenv("NOTION_PROPERTIES_DB_ID", "")
        self.NOTION_OWNERS_DB_ID = os.getenv("NOTION_OWNERS_DB_ID", "")
        
        # Anthropic AI Configuration
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
        
        # Zoho CRM Configuration
        self.ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID", "")
        self.ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "")
        self.ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN", "")
        self.ZOHO_ACCESS_TOKEN = os.getenv("ZOHO_ACCESS_TOKEN", "")
        
        # Database Configuration
        self.DATABASE_PATH = os.getenv("DATABASE_PATH", "real_estate.db")
        
        # Processing Configuration
        self.MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
        self.PROCESSING_INTERVAL = int(os.getenv("PROCESSING_INTERVAL", "300"))  # 5 minutes
        
        # خريطة حقول Zoho CRM
        self.ZOHO_FIELD_MAP = {
            "البيان": "Name",
            "اتاحة العقار": "field12",
            "اسم الموظف": "field13",
            "نوع الوحدة": "field14",
            "حالة الصور": "field11",
            "الدور": "field10",
            "المساحة": "field9",
            "حالة الوحدة": "field8",
            "المنطقة": "field7",
            "كود الوحدة": "field6",
            "اسم المالك": "field5",
            "رقم المالك": "field4",
            "العنوان": "field3",
            "المميزات": "field2",
            "تفاصيل كاملة": "field1",
            "السعر": "field"
        }
        
        # حقول التحقق من التكرار
        self.DUPLICATE_CHECK_FIELDS = [
            "رقم المالك",
            "المنطقة", 
            "نوع الوحدة",
            "حالة الوحدة",
            "المساحة",
            "الدور"
        ]
        
    def validate(self) -> bool:
        """التحقق من صحة الإعدادات"""
        required_configs = [
            ("TELEGRAM_BOT_TOKEN", self.TELEGRAM_BOT_TOKEN),
            ("NOTION_INTEGRATION_SECRET", self.NOTION_INTEGRATION_SECRET),
            ("ANTHROPIC_API_KEY", self.ANTHROPIC_API_KEY),
        ]
        
        missing_configs = []
        for name, value in required_configs:
            if not value:
                missing_configs.append(name)
        
        if missing_configs:
            print(f"❌ المتغيرات البيئية المفقودة: {', '.join(missing_configs)}")
            print("\n📋 إعداد المتغيرات البيئية المطلوبة:")
            print("export TELEGRAM_BOT_TOKEN='your_bot_token'")
            print("export NOTION_INTEGRATION_SECRET='your_notion_secret'")
            print("export ANTHROPIC_API_KEY='your_anthropic_key'")
            return False
            
        return True
    
    def get_zoho_field_mapping(self) -> Dict[str, str]:
        """الحصول على خريطة حقول Zoho"""
        return self.ZOHO_FIELD_MAP.copy()
    
    def get_duplicate_fields(self) -> list:
        """الحصول على حقول التحقق من التكرار"""
        return self.DUPLICATE_CHECK_FIELDS.copy()
