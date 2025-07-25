#!/usr/bin/env python3
"""
إنشاء عقارين نهائي في Notion وZoho بالحقول الصحيحة
"""

import asyncio
import os
from datetime import datetime
from notion_client import Client
from services.zoho_service import ZohoService
from utils.logger import setup_logger

logger = setup_logger(__name__)

async def create_properties_in_notion():
    """إنشاء العقارين في Notion بالحقول الصحيحة"""
    
    notion_secret = os.getenv("NOTION_INTEGRATION_SECRET")
    properties_db_id = os.getenv("NOTION_PROPERTIES_DB_ID")
    owners_db_id = os.getenv("NOTION_OWNERS_DB_ID")
    
    client = Client(auth=notion_secret)
    
    # بيانات العقارين
    properties_data = [
        {
            "البيان": "شقة مفروشة في التجمع الخامس - 120 متر - 25000 جنيه",
            "المنطقة": "التجمع الخامس",
            "نوع الوحدة": "شقة",
            "حالة الوحدة": "مفروش",
            "المساحة": 120,
            "الدور": "الثالث",
            "السعر": 25000,
            "اتاحة العقار": "متاح",
            "حالة الصور": "بصور",
            "اسم الموظف": "أحمد محمد",
            "كود الوحدة": "TEST-001-2024",
            "العنوان": "شارع التسعين الشمالي، التجمع الخامس، القاهرة الجديدة",
            "المميزات": "مكيفة، فيو مفتوح، اسانسير، موقف سيارة",
            "تفاصيل كاملة": "شقة مفروشة بالكامل في التجمع الخامس، 120 متر، الدور الثالث، مكيفة، فيو مفتوح، اسانسير، موقف سيارة، إيجار شهري 25000 جنيه.",
            "owner_name": "سارة أحمد",
            "owner_phone": "01234567890"
        },
        {
            "البيان": "فيلا دوبليكس في الشروق - 250 متر - 45000 جنيه",
            "المنطقة": "الشروق",
            "نوع الوحدة": "فيلا",
            "حالة الوحدة": "غير مفروش",
            "المساحة": 250,
            "الدور": "دوبليكس",
            "السعر": 45000,
            "اتاحة العقار": "متاح",
            "حالة الصور": "بدون صور",
            "اسم الموظف": "فاطمة علي",
            "كود الوحدة": "TEST-002-2024",
            "العنوان": "المنطقة الثامنة، مدينة الشروق",
            "المميزات": "حديقة، جراج، مطبخ جاهز، 3 حمامات",
            "تفاصيل كاملة": "فيلا دوبليكس في مدينة الشروق، 250 متر، غير مفروشة، حديقة خاصة، جراج للسيارات، مطبخ جاهز، 3 حمامات، إيجار شهري 45000 جنيه.",
            "owner_name": "محمد حسن",
            "owner_phone": "01987654321"
        }
    ]
    
    results = []
    
    for i, property_data in enumerate(properties_data, 1):
        try:
            logger.info(f"📝 إنشاء العقار {i}: {property_data['البيان']}")
            
            # أولاً: إنشاء المالك
            owner_page = await asyncio.to_thread(
                client.pages.create,
                parent={"database_id": owners_db_id},
                properties={
                    "اسم المالك": {
                        "title": [
                            {
                                "text": {
                                    "content": property_data["owner_name"]
                                }
                            }
                        ]
                    },
                    "رقم المالك": {
                        "phone_number": property_data["owner_phone"]
                    }
                }
            )
            
            owner_id = owner_page["id"]
            owner_url = f"https://www.notion.so/{owner_id.replace('-', '')}"
            logger.info(f"✅ تم إنشاء المالك: {owner_id}")
            
            # ثانياً: إنشاء العقار
            property_page = await asyncio.to_thread(
                client.pages.create,
                parent={"database_id": properties_db_id},
                properties={
                    "البيان": {
                        "title": [
                            {
                                "text": {
                                    "content": property_data["البيان"]
                                }
                            }
                        ]
                    },
                    "المنطقة": {
                        "select": {
                            "name": property_data["المنطقة"]
                        }
                    },
                    "نوع الوحدة": {
                        "select": {
                            "name": property_data["نوع الوحدة"]
                        }
                    },
                    "حالة الوحدة": {
                        "multi_select": [
                            {
                                "name": property_data["حالة الوحدة"]
                            }
                        ]
                    },
                    "المساحة": {
                        "number": property_data["المساحة"]
                    },
                    "الدور": {
                        "multi_select": [
                            {
                                "name": property_data["الدور"]
                            }
                        ]
                    },
                    "السعر": {
                        "number": property_data["السعر"]
                    },
                    "اتاحة العقار": {
                        "select": {
                            "name": property_data["اتاحة العقار"]
                        }
                    },
                    "حالة الصور": {
                        "select": {
                            "name": property_data["حالة الصور"]
                        }
                    },
                    "اسم الموظف": {
                        "select": {
                            "name": property_data["اسم الموظف"]
                        }
                    },
                    "كود الوحدة": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": property_data["كود الوحدة"]
                                }
                            }
                        ]
                    },
                    "العنوان": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": property_data["العنوان"]
                                }
                            }
                        ]
                    },
                    "المميزات": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": property_data["المميزات"]
                                }
                            }
                        ]
                    },
                    "تفاصيل كاملة": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": property_data["تفاصيل كاملة"]
                                }
                            }
                        ]
                    },
                    "المالك": {
                        "relation": [
                            {
                                "id": owner_id
                            }
                        ]
                    }
                }
            )
            
            property_id = property_page["id"]
            property_url = f"https://www.notion.so/{property_id.replace('-', '')}"
            logger.info(f"✅ تم إنشاء العقار: {property_id}")
            
            results.append({
                "property_data": property_data,
                "owner_id": owner_id,
                "owner_url": owner_url,
                "property_id": property_id,
                "property_url": property_url
            })
            
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء العقار {i}: {e}")
    
    return results

async def create_leads_in_zoho(properties_results):
    """إنشاء العملاء في Zoho"""
    
    client_id = os.getenv("ZOHO_CLIENT_ID")
    client_secret = os.getenv("ZOHO_CLIENT_SECRET")
    refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
    
    if not all([client_id, client_secret, refresh_token]):
        logger.warning("⚠️ إعدادات Zoho غير مكتملة - سيتم تخطي Zoho")
        return []
    
    try:
        async with ZohoService(client_id, client_secret, refresh_token) as zoho_service:
            zoho_results = []
            
            for i, result in enumerate(properties_results, 1):
                property_data = result["property_data"]
                logger.info(f"📝 إنشاء عميل {i} في Zoho: {property_data['owner_name']}")
                
                # تحضير بيانات Zoho
                zoho_data = {
                    "البيان": property_data["البيان"],
                    "اتاحة العقار": property_data["اتاحة العقار"],
                    "اسم الموظف": property_data["اسم الموظف"],
                    "نوع الوحدة": property_data["نوع الوحدة"],
                    "حالة الصور": property_data["حالة الصور"],
                    "الدور": property_data["الدور"],
                    "المساحة": str(property_data["المساحة"]),
                    "حالة الوحدة": property_data["حالة الوحدة"],
                    "المنطقة": property_data["المنطقة"],
                    "كود الوحدة": property_data["كود الوحدة"],
                    "اسم المالك": property_data["owner_name"],
                    "رقم المالك": property_data["owner_phone"],
                    "العنوان": property_data["العنوان"],
                    "المميزات": property_data["المميزات"],
                    "تفاصيل كاملة": property_data["تفاصيل كاملة"],
                    "السعر": str(property_data["السعر"])
                }
                
                lead_id = await zoho_service.create_lead(zoho_data)
                if lead_id:
                    lead_url = zoho_service.get_lead_url(lead_id)
                    zoho_results.append({
                        "lead_id": lead_id,
                        "lead_url": lead_url
                    })
                    logger.info(f"✅ تم إنشاء العميل في Zoho: {lead_id}")
                else:
                    logger.error(f"❌ فشل في إنشاء العميل في Zoho")
                
                await asyncio.sleep(1)
            
            return zoho_results
            
    except Exception as e:
        logger.error(f"❌ خطأ في Zoho: {e}")
        return []

async def main():
    """الدالة الرئيسية"""
    print("🏠 إنشاء عقارين في Notion وZoho")
    print("=" * 50)
    
    # إنشاء العقارات في Notion
    print("\n📝 إنشاء العقارات في Notion...")
    notion_results = await create_properties_in_notion()
    
    if notion_results:
        print(f"✅ تم إنشاء {len(notion_results)} عقار في Notion")
        
        # إنشاء العملاء في Zoho
        print("\n📝 إنشاء العملاء في Zoho...")
        zoho_results = await create_leads_in_zoho(notion_results)
        
        # النتائج النهائية
        print("\n" + "=" * 50)
        print("🎉 النتائج النهائية:")
        
        for i, result in enumerate(notion_results, 1):
            property_data = result["property_data"]
            print(f"\n{i}. {property_data['نوع الوحدة']} في {property_data['المنطقة']}")
            print(f"   المالك: {property_data['owner_name']} ({property_data['owner_phone']})")
            print(f"   المساحة: {property_data['المساحة']} متر")
            print(f"   السعر: {property_data['السعر']} جنيه")
            print(f"   📋 Notion - المالك: {result['owner_url']}")
            print(f"   🏠 Notion - العقار: {result['property_url']}")
            
            if i <= len(zoho_results) and zoho_results:
                print(f"   👤 Zoho - العميل: {zoho_results[i-1]['lead_url']}")
        
        print(f"\n📊 الملخص:")
        print(f"   ✅ Notion: {len(notion_results)} عقار")
        print(f"   ✅ Zoho: {len(zoho_results) if zoho_results else 0} عميل")
        
    else:
        print("❌ فشل في إنشاء العقارات")

if __name__ == "__main__":
    asyncio.run(main())