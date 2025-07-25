"""
الواجهة الويب - Web Interface
"""

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, Any, List
import asyncio
from datetime import datetime, timedelta

from utils.database import DatabaseManager
from processors.property_processor import PropertyProcessor
from models.property import PropertyData, PropertyStatus
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# إنشاء تطبيق FastAPI
app = FastAPI(
    title="نظام إدارة العقارات",
    description="نظام شامل لمعالجة وإدارة بيانات العقارات",
    version="1.0.0"
)

# إعداد الملفات الثابتة والقوالب
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# المتغيرات العامة
config = Config()
database = DatabaseManager(config.DATABASE_PATH)
processor = PropertyProcessor()

@app.on_event("startup")
async def startup_event():
    """أحداث بدء التشغيل"""
    await database.initialize()
    logger.info("🌐 تم تشغيل الواجهة الويب")

@app.on_event("shutdown")
async def shutdown_event():
    """أحداث الإغلاق"""
    await database.close()
    logger.info("🌐 تم إغلاق الواجهة الويب")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """الصفحة الرئيسية - لوحة المراقبة"""
    try:
        # الحصول على الإحصائيات
        stats = await database.get_statistics()
        
        # الحصول على العقارات الحديثة
        recent_properties = await database.get_pending_properties()
        recent_properties = recent_properties[:10]  # أحدث 10 عقارات
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "stats": stats,
            "recent_properties": recent_properties,
            "current_time": datetime.now()
        })
        
    except Exception as e:
        logger.error(f"❌ خطأ في لوحة المراقبة: {e}")
        raise HTTPException(status_code=500, detail="خطأ في النظام")

@app.get("/api/properties")
async def get_properties(
    status: str = None,
    limit: int = 50,
    offset: int = 0
):
    """API للحصول على العقارات"""
    try:
        # هذا مثال بسيط - يمكن تطويره أكثر
        properties = await database.get_pending_properties()
        
        # فلترة حسب الحالة إذا طُلب ذلك
        if status:
            properties = [p for p in properties if p.status.value == status]
        
        # تطبيق التصفح
        total = len(properties)
        properties = properties[offset:offset + limit]
        
        # تحويل إلى قواميس
        properties_dict = []
        for prop in properties:
            prop_dict = prop.to_dict()
            prop_dict["id"] = prop.telegram_message_id
            prop_dict["status"] = prop.status.value
            prop_dict["created_at"] = prop.created_at.isoformat()
            prop_dict["processing_attempts"] = prop.processing_attempts
            properties_dict.append(prop_dict)
        
        return {
            "properties": properties_dict,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"❌ خطأ في API العقارات: {e}")
        raise HTTPException(status_code=500, detail="خطأ في النظام")

@app.get("/api/property/{property_id}")
async def get_property_details(property_id: int):
    """الحصول على تفاصيل عقار"""
    try:
        property_data = await database.get_property_by_telegram_id(property_id)
        
        if not property_data:
            raise HTTPException(status_code=404, detail="العقار غير موجود")
        
        prop_dict = property_data.to_dict()
        prop_dict["id"] = property_data.telegram_message_id
        prop_dict["status"] = property_data.status.value
        prop_dict["created_at"] = property_data.created_at.isoformat()
        prop_dict["updated_at"] = property_data.updated_at.isoformat()
        prop_dict["processing_attempts"] = property_data.processing_attempts
        prop_dict["error_messages"] = property_data.error_messages
        prop_dict["notion_property_id"] = property_data.notion_property_id
        prop_dict["notion_owner_id"] = property_data.notion_owner_id
        prop_dict["zoho_lead_id"] = property_data.zoho_lead_id
        
        return prop_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ خطأ في تفاصيل العقار: {e}")
        raise HTTPException(status_code=500, detail="خطأ في النظام")

@app.post("/api/property/{property_id}/reprocess")
async def reprocess_property(property_id: int, background_tasks: BackgroundTasks):
    """إعادة معالجة عقار"""
    try:
        property_data = await database.get_property_by_telegram_id(property_id)
        
        if not property_data:
            raise HTTPException(status_code=404, detail="العقار غير موجود")
        
        # إعادة تعيين حالة العقار للمعالجة
        property_data.status = PropertyStatus.PENDING
        property_data.error_messages = []
        await database.update_property(property_id, property_data)
        
        # إضافة مهمة المعالجة في الخلفية
        background_tasks.add_task(processor.process_property, property_data)
        
        return {"message": "تم طلب إعادة المعالجة", "property_id": property_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ خطأ في إعادة المعالجة: {e}")
        raise HTTPException(status_code=500, detail="خطأ في النظام")

@app.get("/api/stats")
async def get_system_stats():
    """الحصول على إحصائيات النظام"""
    try:
        stats = await database.get_statistics()
        
        # إضافة معلومات إضافية
        stats["system_status"] = "يعمل" if processor.is_running else "متوقف"
        stats["last_update"] = datetime.now().isoformat()
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ خطأ في الإحصائيات: {e}")
        raise HTTPException(status_code=500, detail="خطأ في النظام")

@app.post("/api/system/start")
async def start_system():
    """بدء النظام"""
    try:
        if not processor.is_running:
            await processor.start()
            return {"message": "تم بدء النظام", "status": "running"}
        else:
            return {"message": "النظام يعمل بالفعل", "status": "already_running"}
            
    except Exception as e:
        logger.error(f"❌ خطأ في بدء النظام: {e}")
        raise HTTPException(status_code=500, detail="خطأ في بدء النظام")

@app.post("/api/system/stop")
async def stop_system():
    """إيقاف النظام"""
    try:
        if processor.is_running:
            await processor.stop()
            return {"message": "تم إيقاف النظام", "status": "stopped"}
        else:
            return {"message": "النظام متوقف بالفعل", "status": "already_stopped"}
            
    except Exception as e:
        logger.error(f"❌ خطأ في إيقاف النظام: {e}")
        raise HTTPException(status_code=500, detail="خطأ في إيقاف النظام")

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """صفحة إعدادات التكامل"""
    try:
        # الحصول على الإعدادات الحالية
        current_settings = {
            "notion_secret": config.NOTION_INTEGRATION_SECRET,
            "notion_properties_db": config.NOTION_PROPERTIES_DB_ID,
            "notion_owners_db": config.NOTION_OWNERS_DB_ID,
            "zoho_client_id": config.ZOHO_CLIENT_ID,
            "zoho_client_secret": config.ZOHO_CLIENT_SECRET,
            "zoho_refresh_token": config.ZOHO_REFRESH_TOKEN,
            "telegram_bot_token": config.TELEGRAM_BOT_TOKEN,
            "telegram_notification_token": config.TELEGRAM_NOTIFICATION_BOT_TOKEN,
            "telegram_channel_id": config.TELEGRAM_CHANNEL_ID,
            "telegram_sender_token": config.TELEGRAM_BOT_sender_TOKEN,
            "telegram_sender_chat_id": config.TELEGRAM_sender_CHAT_ID
        }
        
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "settings": current_settings
        })
        
    except Exception as e:
        logger.error(f"❌ خطأ في صفحة الإعدادات: {e}")
        raise HTTPException(status_code=500, detail="خطأ في النظام")

@app.post("/api/settings/update")
async def update_settings(request: Request):
    """تحديث إعدادات التكامل"""
    try:
        form_data = await request.form()
        
        # تحديث إعدادات Notion
        if form_data.get("notion_secret"):
            config.NOTION_INTEGRATION_SECRET = form_data["notion_secret"]
        if form_data.get("notion_properties_db"):
            config.NOTION_PROPERTIES_DB_ID = form_data["notion_properties_db"]
        if form_data.get("notion_owners_db"):
            config.NOTION_OWNERS_DB_ID = form_data["notion_owners_db"]
        
        # تحديث إعدادات Zoho
        if form_data.get("zoho_client_id"):
            config.ZOHO_CLIENT_ID = form_data["zoho_client_id"]
        if form_data.get("zoho_client_secret"):
            config.ZOHO_CLIENT_SECRET = form_data["zoho_client_secret"]
        if form_data.get("zoho_refresh_token"):
            config.ZOHO_REFRESH_TOKEN = form_data["zoho_refresh_token"]
        
        # تحديث إعدادات Telegram
        if form_data.get("telegram_bot_token"):
            config.TELEGRAM_BOT_TOKEN = form_data["telegram_bot_token"]
        if form_data.get("telegram_notification_token"):
            config.TELEGRAM_NOTIFICATION_BOT_TOKEN = form_data["telegram_notification_token"]
        if form_data.get("telegram_channel_id"):
            config.TELEGRAM_CHANNEL_ID = form_data["telegram_channel_id"]
        if form_data.get("telegram_sender_token"):
            config.TELEGRAM_BOT_sender_TOKEN = form_data["telegram_sender_token"]
        if form_data.get("telegram_sender_chat_id"):
            config.TELEGRAM_sender_CHAT_ID = form_data["telegram_sender_chat_id"]
        
        # حفظ الإعدادات في ملف .env أو متغيرات البيئة
        await save_settings_to_env(form_data)
        
        return {"message": "تم تحديث الإعدادات بنجاح", "status": "success"}
        
    except Exception as e:
        logger.error(f"❌ خطأ في تحديث الإعدادات: {e}")
        raise HTTPException(status_code=500, detail="خطأ في تحديث الإعدادات")

@app.post("/api/settings/test")
async def test_integration_settings():
    """اختبار إعدادات التكامل"""
    try:
        test_results = {
            "notion": False,
            "zoho": False,
            "telegram": False,
            "errors": []
        }
        
        # اختبار Notion
        try:
            from services.notion_service import NotionService
            notion_service = NotionService(
                config.NOTION_INTEGRATION_SECRET,
                config.NOTION_PROPERTIES_DB_ID,
                config.NOTION_OWNERS_DB_ID
            )
            # محاولة الاتصال بقاعدة البيانات
            await asyncio.to_thread(
                notion_service.client.databases.retrieve,
                database_id=config.NOTION_PROPERTIES_DB_ID
            )
            test_results["notion"] = True
        except Exception as e:
            test_results["errors"].append(f"Notion: {str(e)}")
        
        # اختبار Zoho
        try:
            from services.zoho_service import ZohoService
            async with ZohoService(
                config.ZOHO_CLIENT_ID,
                config.ZOHO_CLIENT_SECRET,
                config.ZOHO_REFRESH_TOKEN,
                "",
                "Aqar"
            ) as zoho_service:
                await zoho_service.refresh_access_token()
                test_results["zoho"] = True
        except Exception as e:
            test_results["errors"].append(f"Zoho: {str(e)}")
        
        # اختبار Telegram
        try:
            from services.telegram_service import TelegramService
            async with TelegramService(config) as telegram_service:
                url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/getMe"
                async with telegram_service.session.get(url) as response:
                    if response.status == 200:
                        test_results["telegram"] = True
                    else:
                        test_results["errors"].append(f"Telegram: HTTP {response.status}")
        except Exception as e:
            test_results["errors"].append(f"Telegram: {str(e)}")
        
        return test_results
        
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار الإعدادات: {e}")
        raise HTTPException(status_code=500, detail="خطأ في اختبار الإعدادات")

async def save_settings_to_env(form_data):
    """حفظ الإعدادات في متغيرات البيئة"""
    try:
        env_vars = {
            "NOTION_INTEGRATION_SECRET": form_data.get("notion_secret"),
            "NOTION_PROPERTIES_DB_ID": form_data.get("notion_properties_db"),
            "NOTION_OWNERS_DB_ID": form_data.get("notion_owners_db"),
            "ZOHO_CLIENT_ID": form_data.get("zoho_client_id"),
            "ZOHO_CLIENT_SECRET": form_data.get("zoho_client_secret"),
            "ZOHO_REFRESH_TOKEN": form_data.get("zoho_refresh_token"),
            "TELEGRAM_BOT_TOKEN": form_data.get("telegram_bot_token"),
            "TELEGRAM_NOTIFICATION_BOT_TOKEN": form_data.get("telegram_notification_token"),
            "TELEGRAM_CHANNEL_ID": form_data.get("telegram_channel_id"),
            "TELEGRAM_BOT_sender_TOKEN": form_data.get("telegram_sender_token"),
            "TELEGRAM_sender_CHAT_ID": form_data.get("telegram_sender_chat_id")
        }
        
        # يمكن حفظها في ملف .env هنا إذا أردت
        # أو تحديث متغيرات البيئة مباشرة
        for key, value in env_vars.items():
            if value:
                os.environ[key] = value
        
    except Exception as e:
        logger.error(f"❌ خطأ في حفظ الإعدادات: {e}")

@app.get("/api/health")
async def health_check():
    """فحص صحة النظام"""
    try:
        # فحص قاعدة البيانات
        stats = await database.get_statistics()
        
        # فحص المعالج
        processor_status = "يعمل" if processor.is_running else "متوقف"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "متصل",
            "processor": processor_status,
            "total_properties": stats.get("total_properties", 0)
        }
        
    except Exception as e:
        logger.error(f"❌ خطأ في فحص الصحة: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# معالج الأخطاء العام
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """معالج الأخطاء العام"""
    logger.error(f"❌ خطأ غير متوقع: {exc}")
    
    if "text/html" in request.headers.get("accept", ""):
        # صفحة خطأ HTML
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "حدث خطأ في النظام"
        }, status_code=500)
    else:
        # استجابة JSON
        return JSONResponse(
            status_code=500,
            content={"error": "حدث خطأ في النظام"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
