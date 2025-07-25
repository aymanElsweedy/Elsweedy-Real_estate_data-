
#!/usr/bin/env python3
"""
إعدادات النظام الحقيقي - Real System Configuration
"""

import os
from datetime import datetime

class RealConfig:
    """إعدادات النظام الحقيقي لمعالجة الرسائل"""
    
    # ===== إعدادات Telegram =====
    # البوت الرئيسي للمعالجة (يستلم من قناة الأرشيف)
    TELEGRAM_BOT_TOKEN = "7613162592:AAFnqn3_1lPPClVUa1jckOXj44C2MGCVLHs"
    
    # بوت الإشعارات
    TELEGRAM_NOTIFICATION_BOT_TOKEN = "8220146739:AAELNrVXHGJodSaEMwglQwIQZemz8C_4NTY"
    
    # القناة الرئيسية (Real_estate Archive) - هي نفسها قناة الأرشيف
    TELEGRAM_CHANNEL_ID = "-1002711636474"
    TELEGRAM_ARCHIVE_CHANNEL_ID = "-1002711636474"  # نفس القناة
    
    # معرفات المحادثة للإشعارات
    TELEGRAM_SENDER_CHAT_ID = "7613162592"
    TELEGRAM_NOTIFICATION_CHAT_ID = "8220146739"
    
    # ===== إعدادات Notion =====
    # يجب الحصول عليها من Notion Integration
    NOTION_INTEGRATION_SECRET = os.getenv("NOTION_TOKEN", "")
    NOTION_PROPERTIES_DB_ID = os.getenv("NOTION_PROPERTIES_DB", "")
    NOTION_OWNERS_DB_ID = os.getenv("NOTION_OWNERS_DB", "")
    
    # ===== إعدادات Zoho CRM =====
    # يجب الحصول عليها من Zoho Developer Console
    ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID", "")
    ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "")
    ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN", "")
    ZOHO_ACCESS_TOKEN = os.getenv("ZOHO_ACCESS_TOKEN", "")
    ZOHO_MODULE_NAME = "Aqar"
    
    # ===== إعدادات الذكاء الاصطناعي =====
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    COPILOT_API_KEY = os.getenv("COPILOT_API_KEY", "")
    
    # ===== إعدادات النظام =====
    SUCCESS_TAG = "عقار ناجح ✅"
    FAILED_TAG = "عقار فاشل ❌"
    DUPLICATE_TAG = "عقار مكرر 🔄"
    
    PROCESSING_INTERVAL = 30  # ثانية
    MAX_RETRY_ATTEMPTS = 3
    
    # فلتر التاريخ
    APPLY_DATE_FILTER = False
    LAST_SUCCESS_DATE = None
    
    # قاعدة البيانات
    DATABASE_PATH = "real_estate_real.db"
    
    def validate(self) -> bool:
        """التحقق من صحة الإعدادات"""
        
        required_fields = []
        
        # فحص Telegram (إلزامي)
        if not self.TELEGRAM_BOT_TOKEN:
            required_fields.append("TELEGRAM_BOT_TOKEN")
        
        # فحص Notion (اختياري - سيطبع تحذير)
        notion_available = (
            self.NOTION_INTEGRATION_SECRET and 
            self.NOTION_PROPERTIES_DB_ID and 
            self.NOTION_OWNERS_DB_ID
        )
        
        # فحص Zoho (اختياري - سيطبع تحذير)
        zoho_available = (
            self.ZOHO_CLIENT_ID and 
            self.ZOHO_CLIENT_SECRET and 
            self.ZOHO_REFRESH_TOKEN
        )
        
        # فحص الذكاء الاصطناعي (يجب توفر واحد على الأقل)
        ai_available = any([
            self.GEMINI_API_KEY,
            self.OPENAI_API_KEY,
            self.ANTHROPIC_API_KEY,
            self.MISTRAL_API_KEY,
            self.GROQ_API_KEY
        ])
        
        # طباعة حالة الخدمات
        print("🔍 حالة الخدمات:")
        print(f"   📱 Telegram: ✅ متاح")
        print(f"   🗃️ Notion: {'✅ متاح' if notion_available else '⚠️ غير مُعد'}")
        print(f"   📊 Zoho CRM: {'✅ متاح' if zoho_available else '⚠️ غير مُعد'}")
        print(f"   🤖 AI: {'✅ متاح' if ai_available else '❌ غير متاح'}")
        
        if not ai_available:
            required_fields.append("AI API Key (واحد على الأقل)")
        
        if required_fields:
            print(f"❌ إعدادات مفقودة: {', '.join(required_fields)}")
            return False
        
        return True
    
    def get_available_ai_providers(self) -> list:
        """الحصول على مزودي الذكاء الاصطناعي المتاحين"""
        
        providers = []
        if self.GEMINI_API_KEY:
            providers.append("Gemini")
        if self.OPENAI_API_KEY:
            providers.append("OpenAI")
        if self.ANTHROPIC_API_KEY:
            providers.append("Anthropic")
        if self.MISTRAL_API_KEY:
            providers.append("Mistral")
        if self.GROQ_API_KEY:
            providers.append("Groq")
        
        return providers
