#!/usr/bin/env python3
"""
سكريبت تجريبي لحفظ عقارين في Notion وZoho
"""

import asyncio
import os
import sys
from datetime import datetime
from models.property import PropertyData, PropertyStatus
from services.notion_service import NotionService
from services.zoho_service import ZohoService
from utils.logger import setup_logger

logger = setup_logger(__name__)

# بيانات العقارات التجريبية
TEST_PROPERTIES = [
    {
        "المنطقة": "التجمع الخامس",
        "كود الوحدة": "TEST-001-2024",
        "نوع الوحدة": "شقة",
        "حالة الوحدة": "مفروش",
        "المساحة": "120",
        "الدور": "الثالث",
        "السعر": "25000",
        "المميزات": "مكيفة، فيو مفتوح، اسانسير، موقف سيارة",
        "العنوان": "شارع التسعين الشمالي، التجمع الخامس، القاهرة الجديدة",
        "اسم الموظف": "أحمد محمد",
        "اسم المالك": "سارة أحمد",
        "رقم المالك": "01234567890",
        "اتاحة العقار": "متاح",
        "حالة الصور": "بصور",
        "تفاصيل كاملة": "شقة مفروشة بالكامل في التجمع الخامس، 120 متر، الدور الثالث، مكيفة، فيو مفتوح، اسانسير، موقف سيارة، إيجار شهري 25000 جنيه.",
        "البيان": "نوع الوحدة: شقة | حالة الوحدة: مفروش | المنطقة: التجمع الخامس | المساحة: 120 | الدور: الثالث | السعر: 25000 | كود الوحدة: TEST-001-2024 | اسم الموظف: أحمد محمد | حالة الصور: بصور"
    },
    {
        "المنطقة": "الشروق",
        "كود الوحدة": "TEST-002-2024",
        "نوع الوحدة": "فيلا",
        "حالة الوحدة": "غير مفروش",
        "المساحة": "250",
        "الدور": "دوبليكس",
        "السعر": "45000",
        "المميزات": "حديقة، جراج، مطبخ جاهز، 3 حمامات",
        "العنوان": "المنطقة الثامنة، مدينة الشروق",
        "اسم الموظف": "فاطمة علي",
        "اسم المالك": "محمد حسن",
        "رقم المالك": "01987654321",
        "اتاحة العقار": "متاح",
        "حالة الصور": "بدون صور",
        "تفاصيل كاملة": "فيلا دوبليكس في مدينة الشروق، 250 متر، غير مفروشة، حديقة خاصة، جراج للسيارات، مطبخ جاهز، 3 حمامات، إيجار شهري 45000 جنيه.",
        "البيان": "نوع الوحدة: فيلا | حالة الوحدة: غير مفروش | المنطقة: الشروق | المساحة: 250 | الدور: دوبليكس | السعر: 45000 | كود الوحدة: TEST-002-2024 | اسم الموظف: فاطمة علي | حالة الصور: بدون صور"
    }
]

async def create_test_property(property_data_dict: dict) -> PropertyData:
    """إنشاء عقار تجريبي"""
    property_data = PropertyData.from_dict(property_data_dict)
    property_data.status = PropertyStatus.NEW
    property_data.created_at = datetime.now()
    property_data.updated_at = datetime.now()
    
    return property_data

async def test_notion_integration(properties: list):
    """اختبار التكامل مع Notion"""
    
    notion_secret = os.getenv("NOTION_INTEGRATION_SECRET")
    properties_db_id = os.getenv("NOTION_PROPERTIES_DB_ID", os.getenv("NOTION_DATABASE_ID"))
    owners_db_id = os.getenv("NOTION_OWNERS_DB_ID", os.getenv("NOTION_DATABASE_ID"))
    
    if not notion_secret:
        logger.error("❌ لم يتم العثور على NOTION_INTEGRATION_SECRET")
        return False
    
    if not properties_db_id:
        logger.error("❌ لم يتم العثور على NOTION_PROPERTIES_DB_ID")
        return False
    
    try:
        logger.info("🔄 بدء اختبار Notion...")
        
        notion_service = NotionService(notion_secret, properties_db_id, owners_db_id or properties_db_id)
        
        for i, property_data in enumerate(properties, 1):
            logger.info(f"📝 إنشاء العقار {i}: {property_data.region}")
            
            # إنشاء صفحة مالك
            owner_id = await notion_service.create_owner_page(property_data.to_dict())
            if owner_id:
                property_data.notion_owner_id = owner_id
                logger.info(f"✅ تم إنشاء صفحة المالك: {owner_id}")
            
            # إنشاء صفحة عقار
            property_id = await notion_service.create_property_page(
                property_data.to_dict(), owner_id
            )
            if property_id:
                property_data.notion_property_id = property_id
                logger.info(f"✅ تم إنشاء صفحة العقار: {property_id}")
                
                # طباعة الرابط
                property_url = notion_service.get_property_url(property_id)
                logger.info(f"🔗 رابط العقار: {property_url}")
            
            await asyncio.sleep(1)  # توقف قصير بين العقارات
        
        logger.info("✅ تم إكمال اختبار Notion بنجاح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار Notion: {e}")
        return False

async def test_zoho_integration(properties: list):
    """اختبار التكامل مع Zoho"""
    
    client_id = os.getenv("ZOHO_CLIENT_ID")
    client_secret = os.getenv("ZOHO_CLIENT_SECRET")
    refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
    
    if not all([client_id, client_secret, refresh_token]):
        logger.warning("⚠️ لم يتم العثور على إعدادات Zoho - سيتم تخطي اختبار Zoho")
        return True
    
    try:
        logger.info("🔄 بدء اختبار Zoho...")
        
        async with ZohoService(client_id, client_secret, refresh_token) as zoho_service:
            for i, property_data in enumerate(properties, 1):
                logger.info(f"📝 إنشاء العميل {i} في Zoho: {property_data.owner_name}")
                
                # إنشاء عميل في Zoho
                lead_id = await zoho_service.create_lead(property_data.to_dict())
                if lead_id:
                    property_data.zoho_lead_id = lead_id
                    logger.info(f"✅ تم إنشاء العميل في Zoho: {lead_id}")
                    
                    # طباعة الرابط
                    lead_url = zoho_service.get_lead_url(lead_id)
                    logger.info(f"🔗 رابط العميل: {lead_url}")
                
                await asyncio.sleep(1)  # توقف قصير بين العقارات
        
        logger.info("✅ تم إكمال اختبار Zoho بنجاح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار Zoho: {e}")
        return False

async def main():
    """الدالة الرئيسية للاختبار"""
    
    print("🏠 اختبار نظام إدارة العقارات")
    print("=" * 50)
    
    # إنشاء العقارات التجريبية
    logger.info("📋 إنشاء العقارات التجريبية...")
    test_properties = []
    
    for property_dict in TEST_PROPERTIES:
        property_data = await create_test_property(property_dict)
        test_properties.append(property_data)
        logger.info(f"✅ تم إنشاء عقار تجريبي: {property_data.region} - {property_data.unit_type}")
    
    print(f"\n📊 تم إنشاء {len(test_properties)} عقار تجريبي")
    
    # اختبار Notion
    print("\n🔍 اختبار التكامل مع Notion...")
    notion_success = await test_notion_integration(test_properties)
    
    # اختبار Zoho
    print("\n🔍 اختبار التكامل مع Zoho...")
    zoho_success = await test_zoho_integration(test_properties)
    
    # النتائج النهائية
    print("\n" + "=" * 50)
    print("📋 نتائج الاختبار:")
    print(f"   Notion: {'✅ نجح' if notion_success else '❌ فشل'}")
    print(f"   Zoho: {'✅ نجح' if zoho_success else '❌ فشل'}")
    
    if notion_success or zoho_success:
        print("\n🎉 تم إنشاء العقارات التجريبية بنجاح!")
        print("\nالعقارات المُنشأة:")
        
        for i, prop in enumerate(test_properties, 1):
            print(f"\n{i}. {prop.unit_type} في {prop.region}")
            print(f"   المالك: {prop.owner_name} ({prop.owner_phone})")
            print(f"   السعر: {prop.price} جنيه")
            
            if prop.notion_property_id:
                property_url = f"https://www.notion.so/{prop.notion_property_id.replace('-', '')}"
                print(f"   Notion: {property_url}")
            
            if prop.zoho_lead_id:
                lead_url = f"https://crm.zoho.com/crm/EntityInfo?module=Leads&id={prop.zoho_lead_id}"
                print(f"   Zoho: {lead_url}")
    
    else:
        print("\n⚠️  لم يتم إنشاء أي عقارات - تحقق من المفاتيح والإعدادات")

if __name__ == "__main__":
    asyncio.run(main())