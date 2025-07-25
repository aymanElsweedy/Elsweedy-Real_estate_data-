
"""
إعدادات تجريبية للنظام - Demo Configuration
"""

import os
from typing import Optional

class DemoConfig:
    """فئة إعدادات تجريبية"""
    
    def __init__(self):
        # Telegram Bot Configuration (تجريبي)
        self.TELEGRAM_BOT_TOKEN = "DEMO_TOKEN"
        self.TELEGRAM_NOTIFICATION_BOT_TOKEN = "DEMO_NOTIFICATION_TOKEN"
        self.TELEGRAM_CHANNEL_ID = "-1002711636474"
        self.TELEGRAM_ARCHIVE_CHANNEL_ID = "-1002711636474"
        
        # Notion Configuration (تجريبي)
        self.NOTION_INTEGRATION_SECRET = "DEMO_NOTION_SECRET"
        self.NOTION_PROPERTIES_DB_ID = "DEMO_PROPERTIES_DB"
        self.NOTION_OWNERS_DB_ID = "DEMO_OWNERS_DB"
        
        # AI Services Configuration (تجريبي)
        self.ANTHROPIC_API_KEY = "DEMO_ANTHROPIC_KEY"
        self.OPENAI_API_KEY = ""
        self.GEMINI_API_KEY = ""
        self.COPILOT_API_KEY = ""
        self.MISTRAL_API_KEY = ""
        self.GROQ_API_KEY = ""
        
        # Zoho CRM Configuration (تجريبي)
        self.ZOHO_CLIENT_ID = "DEMO_ZOHO_CLIENT"
        self.ZOHO_CLIENT_SECRET = "DEMO_ZOHO_SECRET"
        self.ZOHO_REFRESH_TOKEN = "DEMO_ZOHO_TOKEN"
        self.ZOHO_ACCESS_TOKEN = ""
        self.ZOHO_MODULE_NAME = "Aqar"
        
        # Database Configuration
        self.DATABASE_PATH = "demo_real_estate.db"
        
        # Processing Configuration
        self.MAX_RETRY_ATTEMPTS = 3
        self.PROCESSING_INTERVAL = 30  # 30 seconds for demo
        self.AI_RETRY_DELAY = 5  # 5 seconds for demo
        
        # Success Tag Configuration
        self.SUCCESS_TAG = "عقار ناجح ✅"
        self.FAILED_TAG = "عقار فاشل ❌"
        self.DUPLICATE_TAG = "عقار مكرر 🔄"
        self.MULTIPLE_TAG = "عقار متعدد 📊"
        
        # Date Filter Configuration
        self.APPLY_DATE_FILTER = False
        self.LAST_SUCCESS_DATE = ""
        
        # Telegram API Configuration
        self.TELEGRAM_API_ID = "23358202"
        self.TELEGRAM_API_HASH = "demo_hash"
        self.TELEGRAM_BOT_sender_TOKEN = "7613162592:AAFnqn3_1lPPClVUa1jckOXj44C2MGCVLHs"
        self.TELEGRAM_sender_CHAT_ID = "7613162592"
        self.TELEGRAM_NOTIFICATION_CHAT_ID = "8220146739"
        
        # خريطة حقول Zoho CRM
        self.ZOHO_FIELD_MAP = {
            "البيان": "Name",
            "المنطقة": "Region",
            "كود الوحدة": "Unit_Code",
            "نوع الوحدة": "Unit_Type",
            "حالة الوحدة": "Unit_Condition",
            "المساحة": "Area",
            "الدور": "Floor",
            "السعر": "Price",
            "المميزات": "Features",
            "العنوان": "Address",
            "اسم الموظف": "Employee_Name",
            "اسم المالك": "Owner_Name",
            "رقم المالك": "Owner_Phone",
            "اتاحة العقار": "Availability",
            "حالة الصور": "Photos_Status",
            "تفاصيل كاملة": "Full_Details"
        }
        
        # قائمة المناطق المعتمدة
        self.APPROVED_REGIONS = {
            "z1": ["دار قرنفل", "قرنفل فيلات", "بنفسج", "ياسمين"],
            "z3": ["سكن شباب", "مستقبل", "هناجر", "نزهه ثالث"],
            "z4": ["رحاب", "جاردينيا سيتي"],
            "z5": ["كمباوندات", "احياء تجمع", "بيت وطن", "نرجس", "لوتس", 
                   "شويفات", "زيزينيا", "اندلس", "دار اندلس", "سكن اندلس", 
                   "سكن معارض", "جنه", "جاردينيا هايتس"]
        }
        
        # قائمة أسماء الموظفين المعتمدة
        self.APPROVED_EMPLOYEES = [
            "بلبل", "اسلام", "ايمن", "تاحه", "علياء", 
            "محمود سامي", "يوسف", "عماد", "يوسف الجوهري"
        ]
        
        # قائمة المميزات المعتمدة
        self.APPROVED_FEATURES = [
            "تشطيب سوبر لوكس", "مدخل خاص", "دبل فيس", "اسانسير", 
            "حصه في ارض", "حديقه", "فيو مفتوح", "فيو جاردن", 
            "مسجله شهر عقاري", "تقسيط", "مكيفه", "باقي اقساط"
        ]
    
    def validate(self) -> bool:
        """التحقق من صحة الإعدادات التجريبية"""
        print("✅ إعدادات تجريبية - جميع الخدمات متاحة")
        return True
    
    def get_available_ai_providers(self) -> list:
        """الحصول على قائمة مزودي الذكاء الاصطناعي المتاحين"""
        return ["Demo AI Provider"]
    
    def get_region_zone(self, region: str) -> str:
        """الحصول على زون المنطقة"""
        for zone, regions in self.APPROVED_REGIONS.items():
            if region in regions:
                return zone.replace("z", "")
        return "5"
