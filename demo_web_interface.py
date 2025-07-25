
"""
الواجهة الويب التجريبية - Demo Web Interface
"""

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, Any
import asyncio
from datetime import datetime
import random

# إنشاء تطبيق FastAPI
app = FastAPI(
    title="نظام إدارة العقارات - العرض التجريبي",
    description="عرض تجريبي شامل لنظام إدارة العقارات",
    version="2.0.0-demo"
)

# إعداد الملفات الثابتة والقوالب
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# بيانات تجريبية
demo_stats = {
    "total_properties": 156,
    "successful": 142,
    "failed": 8,
    "duplicate": 6,
    "multiple": 12,
    "pending": 4,
    "success_rate": 91.0,
    "last_update": datetime.now().isoformat()
}

demo_properties = [
    {
        "id": 1001,
        "region": "احياء تجمع",
        "unit_type": "شقة",
        "area": "120",
        "price": "25000",
        "owner_name": "سارة أحمد",
        "owner_phone": "01111111111",
        "employee_name": "بلبل",
        "status": "successful",
        "created_at": "2024-01-25T10:30:00",
        "notion_url": "https://www.notion.so/demo-property-1001",
        "zoho_url": "https://crm.zoho.com/demo-record-1001"
    },
    {
        "id": 1002,
        "region": "اندلس",
        "unit_type": "فيلا",
        "area": "250",
        "price": "45000",
        "owner_name": "محمد حسن",
        "owner_phone": "01222222222",
        "employee_name": "يوسف عماد",
        "status": "successful",
        "created_at": "2024-01-25T11:15:00",
        "notion_url": "https://www.notion.so/demo-property-1002",
        "zoho_url": "https://crm.zoho.com/demo-record-1002"
    },
    {
        "id": 1003,
        "region": "جاردينيا هايتس",
        "unit_type": "شقة",
        "area": "180",
        "price": "1500000",
        "owner_name": "أميرة خالد",
        "owner_phone": "01333444555",
        "employee_name": "محمود سامي",
        "status": "successful",
        "created_at": "2024-01-25T12:00:00",
        "notion_url": "https://www.notion.so/demo-property-1003",
        "zoho_url": "https://crm.zoho.com/demo-record-1003"
    },
    {
        "id": 1004,
        "region": "رحاب",
        "unit_type": "شقة",
        "area": "90",
        "price": "18000",
        "owner_name": "أحمد علي",
        "owner_phone": "01444555666",
        "employee_name": "اسلام",
        "status": "pending",
        "created_at": "2024-01-25T12:30:00"
    }
]

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """الصفحة الرئيسية - لوحة المراقبة التجريبية"""
    
    # تحديث الإحصائيات بشكل ديناميكي
    demo_stats["last_update"] = datetime.now().isoformat()
    demo_stats["total_properties"] += random.randint(0, 2)
    
    return templates.TemplateResponse("demo_index.html", {
        "request": request,
        "stats": demo_stats,
        "recent_properties": demo_properties[:10],
        "current_time": datetime.now(),
        "system_status": "يعمل",
        "is_demo": True
    })

@app.get("/api/properties")
async def get_properties(
    status: str = None,
    limit: int = 50,
    offset: int = 0
):
    """API للحصول على العقارات التجريبية"""
    
    properties = demo_properties.copy()
    
    # فلترة حسب الحالة
    if status:
        properties = [p for p in properties if p["status"] == status]
    
    # تطبيق التصفح
    total = len(properties)
    properties = properties[offset:offset + limit]
    
    return {
        "properties": properties,
        "total": total,
        "limit": limit,
        "offset": offset,
        "is_demo": True
    }

@app.get("/api/property/{property_id}")
async def get_property_details(property_id: int):
    """الحصول على تفاصيل عقار تجريبي"""
    
    # البحث عن العقار
    property_data = None
    for prop in demo_properties:
        if prop["id"] == property_id:
            property_data = prop.copy()
            break
    
    if not property_data:
        return {"error": "العقار غير موجود"}
    
    # إضافة تفاصيل إضافية
    property_data.update({
        "unit_condition": "مفروش",
        "floor": "الثالث",
        "features": "مكيفه، فيو مفتوح، اسانسير",
        "address": f"{property_data['region']}, القاهرة الجديدة",
        "availability": "متاح",
        "photos_status": "متوفر صور",
        "processing_attempts": 1,
        "updated_at": datetime.now().isoformat(),
        "is_demo": True
    })
    
    return property_data

@app.post("/api/property/{property_id}/reprocess")
async def reprocess_property(property_id: int):
    """محاكاة إعادة معالجة عقار"""
    
    await asyncio.sleep(1)  # محاكاة وقت المعالجة
    
    return {
        "message": "تم طلب إعادة المعالجة (تجريبي)",
        "property_id": property_id,
        "status": "success",
        "is_demo": True
    }

@app.get("/api/stats")
async def get_system_stats():
    """الحصول على إحصائيات النظام التجريبية"""
    
    # تحديث الإحصائيات
    demo_stats["last_update"] = datetime.now().isoformat()
    demo_stats["system_status"] = "يعمل (تجريبي)"
    demo_stats["is_demo"] = True
    
    return demo_stats

@app.post("/api/system/start")
async def start_system():
    """محاكاة بدء النظام"""
    await asyncio.sleep(0.5)
    return {
        "message": "تم بدء النظام التجريبي",
        "status": "running",
        "is_demo": True
    }

@app.post("/api/system/stop")
async def stop_system():
    """محاكاة إيقاف النظام"""
    await asyncio.sleep(0.5)
    return {
        "message": "تم إيقاف النظام التجريبي",
        "status": "stopped",
        "is_demo": True
    }

@app.post("/api/demo/simulate")
async def simulate_processing():
    """محاكاة معالجة عقار جديد"""
    
    await asyncio.sleep(2)  # محاكاة وقت المعالجة
    
    # إضافة عقار جديد
    new_property = {
        "id": 1000 + len(demo_properties) + 1,
        "region": random.choice(["احياء تجمع", "اندلس", "جاردينيا هايتس", "رحاب"]),
        "unit_type": random.choice(["شقة", "فيلا", "دوبليكس"]),
        "area": str(random.randint(80, 300)),
        "price": str(random.randint(15000, 50000)),
        "owner_name": f"مالك تجريبي {random.randint(100, 999)}",
        "owner_phone": f"0111{random.randint(1000000, 9999999)}",
        "employee_name": random.choice(["بلبل", "محمود سامي", "يوسف عماد"]),
        "status": "successful",
        "created_at": datetime.now().isoformat(),
        "notion_url": f"https://www.notion.so/demo-property-{1000 + len(demo_properties) + 1}",
        "zoho_url": f"https://crm.zoho.com/demo-record-{1000 + len(demo_properties) + 1}"
    }
    
    demo_properties.append(new_property)
    demo_stats["total_properties"] += 1
    demo_stats["successful"] += 1
    
    return {
        "message": "تم محاكاة معالجة عقار جديد",
        "property": new_property,
        "is_demo": True
    }

@app.get("/api/health")
async def health_check():
    """فحص صحة النظام التجريبي"""
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "متصل (تجريبي)",
        "processor": "يعمل (تجريبي)",
        "total_properties": demo_stats["total_properties"],
        "is_demo": True
    }

if __name__ == "__main__":
    import uvicorn
    print("🌐 بدء تشغيل الواجهة الويب التجريبية...")
    print("📱 الواجهة متاحة على: http://0.0.0.0:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000)
