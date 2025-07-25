
#!/usr/bin/env python3
"""
إعداد المتغيرات البيئية للنظام الحقيقي
"""

import os

def setup_environment_variables():
    """إعداد متغيرات البيئة المطلوبة"""
    
    print("🔧 إعداد متغيرات البيئة للنظام الحقيقي")
    print("=" * 60)
    
    # متغيرات Notion
    print("\n🗃️ إعداد Notion:")
    print("1. اذهب إلى https://www.notion.so/my-integrations")
    print("2. أنشئ Integration جديد")
    print("3. انسخ الرمز المميز وأضفه كـ Secret بالاسم: NOTION_TOKEN")
    print("4. أنشئ قاعدة بيانات للعقارات وانسخ ID وأضفه كـ: NOTION_PROPERTIES_DB")
    print("5. أنشئ قاعدة بيانات للمالكين وانسخ ID وأضفه كـ: NOTION_OWNERS_DB")
    
    # متغيرات Zoho
    print("\n📊 إعداد Zoho CRM:")
    print("1. اذهب إلى https://api-console.zoho.com/")
    print("2. أنشئ تطبيق جديد")
    print("3. احصل على Client ID و Client Secret")
    print("4. احصل على Refresh Token")
    print("5. أضف هذه القيم كـ Secrets:")
    print("   - ZOHO_CLIENT_ID")
    print("   - ZOHO_CLIENT_SECRET") 
    print("   - ZOHO_REFRESH_TOKEN")
    print("   - ZOHO_ACCESS_TOKEN (اختياري)")
    
    # متغيرات AI
    print("\n🤖 إعداد خدمات الذكاء الاصطناعي:")
    print("أضف واحد أو أكثر من هذه المفاتيح كـ Secrets:")
    print("   - GEMINI_API_KEY")
    print("   - OPENAI_API_KEY")
    print("   - ANTHROPIC_API_KEY")
    print("   - MISTRAL_API_KEY")
    print("   - GROQ_API_KEY")
    
    print("\n✅ بعد إضافة المتغيرات، شغل النظام بـ:")
    print("python real_system.py")

if __name__ == "__main__":
    setup_environment_variables()
