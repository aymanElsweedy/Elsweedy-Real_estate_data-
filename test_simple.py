#!/usr/bin/env python3
"""
سكريبت بسيط لاختبار تخزين عقارين في Notion وZoho
"""

import asyncio
import os
from datetime import datetime
from models.property import PropertyData, PropertyStatus
from services.ai_service import AIService
from services.notion_service import NotionService
from services.zoho_service import ZohoService
from utils.logger import setup_logger

logger = setup_logger(__name__)

# بيانات العقارين التجريبيين
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

async def test_notion_storage():
    """اختبار تخزين العقارات في Notion"""
    notion_secret = os.getenv("NOTION_INTEGRATION_SECRET")
    properties_db_id = os.getenv("NOTION_PROPERTIES_DB_ID")
    owners_db_id = os.getenv("NOTION_OWNERS_DB_ID")
    
    if not all([notion_secret, properties_db_id, owners_db_id]):
        logger.error("❌ إعدادات Notion غير مكتملة")
        return False
    
    try:
        logger.info("🔄 بدء اختبار Notion...")
        notion_service = NotionService(notion_secret, properties_db_id, owners_db_id)
        
        results = []
        for i, property_dict in enumerate(TEST_PROPERTIES, 1):
            logger.info(f"📝 معالجة العقار {i}: {property_dict['المنطقة']}")
            
            property_data = PropertyData.from_dict(property_dict)
            property_data.status = PropertyStatus.NEW
            property_data.created_at = datetime.now()
            
            # إنشاء صفحة المالك
            owner_id = await notion_service.create_owner_page(property_data.to_dict())
            if owner_id:
                logger.info(f"✅ تم إنشاء صفحة المالك: {owner_id}")
                
                # إنشاء صفحة العقار
                property_id = await notion_service.create_property_page(
                    property_data.to_dict(), owner_id
                )
                if property_id:
                    logger.info(f"✅ تم إنشاء صفحة العقار: {property_id}")
                    property_url = notion_service.get_property_url(property_id)
                    results.append({
                        "property": property_dict,
                        "owner_id": owner_id,
                        "property_id": property_id,
                        "property_url": property_url
                    })
                    logger.info(f"🔗 رابط العقار: {property_url}")
                else:
                    logger.error(f"❌ فشل في إنشاء صفحة العقار")
            else:
                logger.error(f"❌ فشل في إنشاء صفحة المالك")
            
            await asyncio.sleep(1)
        
        logger.info(f"✅ تم إكمال اختبار Notion - تم إنشاء {len(results)} عقار")
        return results
        
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار Notion: {e}")
        return False

async def test_zoho_storage(properties_data):
    """اختبار تخزين العقارات في Zoho"""
    client_id = os.getenv("ZOHO_CLIENT_ID")
    client_secret = os.getenv("ZOHO_CLIENT_SECRET")
    refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
    
    if not all([client_id, client_secret, refresh_token]):
        logger.warning("⚠️ إعدادات Zoho غير مكتملة - سيتم تخطي اختبار Zoho")
        return True
    
    try:
        logger.info("🔄 بدء اختبار Zoho...")
        
        async with ZohoService(client_id, client_secret, refresh_token) as zoho_service:
            results = []
            for i, result in enumerate(properties_data, 1):
                property_dict = result["property"]
                logger.info(f"📝 إنشاء عميل {i} في Zoho: {property_dict['اسم المالك']}")
                
                # إنشاء عميل في Zoho
                lead_id = await zoho_service.create_lead(property_dict)
                if lead_id:
                    logger.info(f"✅ تم إنشاء العميل في Zoho: {lead_id}")
                    lead_url = zoho_service.get_lead_url(lead_id)
                    results.append({
                        "lead_id": lead_id,
                        "lead_url": lead_url
                    })
                    logger.info(f"🔗 رابط العميل: {lead_url}")
                else:
                    logger.error(f"❌ فشل في إنشاء العميل في Zoho")
                
                await asyncio.sleep(1)
        
        logger.info(f"✅ تم إكمال اختبار Zoho - تم إنشاء {len(results)} عميل")
        return results
        
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار Zoho: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    print("🏠 اختبار تخزين عقارين في Notion وZoho")
    print("=" * 50)
    
    # اختبار Notion
    print("\n🔍 اختبار Notion...")
    notion_results = await test_notion_storage()
    
    if notion_results:
        print(f"✅ نجح اختبار Notion - تم إنشاء {len(notion_results)} عقار")
        
        # اختبار Zoho
        print("\n🔍 اختبار Zoho...")
        zoho_results = await test_zoho_storage(notion_results)
        
        # النتائج النهائية
        print("\n" + "=" * 50)
        print("📋 نتائج الاختبار:")
        
        for i, result in enumerate(notion_results, 1):
            property_dict = result["property"]
            print(f"\n{i}. {property_dict['نوع الوحدة']} في {property_dict['المنطقة']}")
            print(f"   المالك: {property_dict['اسم المالك']} ({property_dict['رقم المالك']})")
            print(f"   السعر: {property_dict['السعر']} جنيه")
            print(f"   Notion: {result['property_url']}")
            
            if zoho_results and i <= len(zoho_results):
                print(f"   Zoho: {zoho_results[i-1]['lead_url']}")
    
    else:
        print("❌ فشل اختبار Notion")
    
    print("\n🎉 تم إكمال الاختبار!")

if __name__ == "__main__":
    asyncio.run(main())