
"""
إعدادات النظام المحدثة - System Configuration
"""

import os
from typing import Optional

class Config:
    """فئة إعدادات النظام المحدثة"""
    
    def __init__(self):
        # Telegram Bot Configuration - البوتين
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7238037158:AAEIEkWPUaR76ndCbwm9r7b8cyKrEac6sOM")
        self.TELEGRAM_NOTIFICATION_BOT_TOKEN = os.getenv("TELEGRAM_NOTIFICATION_BOT_TOKEN", "8135541726:AAHxZAfaYIksBD1Lma12x5GbVzbpxsKhVmk")
        self.TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "-1002874153693")
        self.TELEGRAM_ARCHIVE_CHANNEL_ID = os.getenv("TELEGRAM_ARCHIVE_CHANNEL_ID", "")
        
        # Notion Configuration
        self.NOTION_INTEGRATION_SECRET = os.getenv("NOTION_INTEGRATION_SECRET", "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")
        self.NOTION_PROPERTIES_DB_ID = os.getenv("NOTION_PROPERTIES_DB_ID", "4f4af5e86fd94104bb8f6a931a187936")
        self.NOTION_OWNERS_DB_ID = os.getenv("NOTION_OWNERS_DB_ID", "224ecf34ff0080009116ee1fae53330e")
        
        # AI Services Configuration - جميع مزودي الذكاء الاصطناعي
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBXGqbXJk0VyivjSwLPidU9HYPqmTfqLCk")
        self.COPILOT_API_KEY = os.getenv("COPILOT_API_KEY", "")
        self.MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "soMr4s2jGPzGrKO00BOjOh7Vrhb5IxMP")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
        
        # Zoho CRM Configuration - موديول Aqar الجديد
        self.ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID", "1000.OBIGSUQKCC2THQM9VY3TXW6NXV9WHV")
        self.ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "58db3c4cfd6522f8cca0282747ef300514f55c1ad8")
        self.ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN", "1000.a7e96420b2fd242b26732fa7f5a4c2f6.8269f1c317bdbbac53666a61d9fbe454")
        self.ZOHO_ACCESS_TOKEN = os.getenv("ZOHO_ACCESS_TOKEN", "")
        self.ZOHO_MODULE_NAME = os.getenv("ZOHO_MODULE_NAME", "Aqar")  # موديول جديد
        
        # Database Configuration
        self.DATABASE_PATH = os.getenv("DATABASE_PATH", "real_estate.db")
        
        # Processing Configuration
        self.MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
        self.PROCESSING_INTERVAL = int(os.getenv("PROCESSING_INTERVAL", "300"))  # 5 minutes
        self.AI_RETRY_DELAY = int(os.getenv("AI_RETRY_DELAY", "15"))  # 15 seconds
        
        # Success Tag Configuration - نظام الوسم الجديد
        self.SUCCESS_TAG = "عقار ناجح ✅"
        self.FAILED_TAG = "عقار فاشل ❌"
        self.DUPLICATE_TAG = "عقار مكرر 🔄"
        self.MULTIPLE_TAG = "عقار متعدد 📊"
        
        # Date Filter Configuration
        self.APPLY_DATE_FILTER = os.getenv("APPLY_DATE_FILTER", "false").lower() == "true"
        self.LAST_SUCCESS_DATE = os.getenv("LAST_SUCCESS_DATE", "")
        
        # خريطة حقول Zoho CRM المحدثة لموديول Aqar
        self.ZOHO_FIELD_MAP = {
            "البيان": "Name",                    # حقل البيان المدمج
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
            "تفاصيل كاملة": "Full_Details",
            "telegram_message_id": "Telegram_Message_ID",
            "notion_property_id": "Notion_Property_ID",
            "notion_owner_id": "Notion_Owner_ID",
            "status": "Status"
        }
        
        # قائمة المناطق المعتمدة
        self.APPROVED_REGIONS = {
            "z1": ["دار قرنفل", "قرنفل فيلات", "بنفسج", "ياسمين", "ج ش اكاديميه"],
            "z3": ["سكن شباب", "مستقبل", "هناجر", "نزهه ثالث"],
            "z4": ["رحاب", "جاردينيا سيتي"],
            "z5": ["كمباوندات", "احياء تجمع", "بيت وطن", "نرجس", "لوتس", "شويفات", 
                   "زيزينيا", "اندلس", "دار اندلس", "سكن اندلس", "سكن معارض", 
                   "جنه", "جاردينيا هايتس"]
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
        """التحقق من صحة الإعدادات"""
        
        required_configs = [
            ("TELEGRAM_BOT_TOKEN", self.TELEGRAM_BOT_TOKEN),
            ("TELEGRAM_CHANNEL_ID", self.TELEGRAM_CHANNEL_ID),
            ("NOTION_INTEGRATION_SECRET", self.NOTION_INTEGRATION_SECRET),
            ("NOTION_PROPERTIES_DB_ID", self.NOTION_PROPERTIES_DB_ID),
            ("NOTION_OWNERS_DB_ID", self.NOTION_OWNERS_DB_ID)
        ]
        
        missing_configs = []
        for config_name, config_value in required_configs:
            if not config_value:
                missing_configs.append(config_name)
        
        if missing_configs:
            print(f"❌ إعدادات مفقودة: {', '.join(missing_configs)}")
            return False
        
        # التحقق من وجود مزود ذكاء اصطناعي واحد على الأقل
        ai_providers = [
            self.ANTHROPIC_API_KEY,
            self.OPENAI_API_KEY,
            self.GEMINI_API_KEY,
            self.MISTRAL_API_KEY,
            self.GROQ_API_KEY
        ]
        
        if not any(ai_providers):
            print("❌ يجب إضافة مزود ذكاء اصطناعي واحد على الأقل")
            return False
        
        print("✅ جميع الإعدادات صحيحة")
        return True
    
    def get_available_ai_providers(self) -> list:
        """الحصول على قائمة مزودي الذكاء الاصطناعي المتاحين"""
        
        providers = []
        
        if self.GEMINI_API_KEY:
            providers.append("Gemini")
        if self.OPENAI_API_KEY:
            providers.append("OpenAI")
        if self.COPILOT_API_KEY:
            providers.append("Copilot")
        if self.MISTRAL_API_KEY:
            providers.append("Mistral")
        if self.GROQ_API_KEY:
            providers.append("Groq")
        if self.ANTHROPIC_API_KEY:
            providers.append("Anthropic")
        
        return providers
    
    def get_region_zone(self, region: str) -> str:
        """الحصول على زون المنطقة"""
        
        for zone, regions in self.APPROVED_REGIONS.items():
            if region in regions:
                return zone.replace("z", "")
        
        return "5"  # افتراضي
