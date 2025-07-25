#!/usr/bin/env python3
"""
فحص وإنشاء الحقول الصحيحة في Notion
"""

import asyncio
import os
from notion_client import Client
from utils.logger import setup_logger

logger = setup_logger(__name__)

async def check_notion_databases():
    """فحص قواعد البيانات وإنشاء العقارات بحقول بسيطة"""
    
    notion_secret = os.getenv("NOTION_INTEGRATION_SECRET")
    properties_db_id = os.getenv("NOTION_PROPERTIES_DB_ID")
    owners_db_id = os.getenv("NOTION_OWNERS_DB_ID")
    
    if not all([notion_secret, properties_db_id, owners_db_id]):
        logger.error("❌ إعدادات Notion غير مكتملة")
        return
    
    client = Client(auth=notion_secret)
    
    try:
        # فحص قواعد البيانات
        logger.info("🔍 فحص قاعدة بيانات العقارات...")
        properties_db = await asyncio.to_thread(
            client.databases.retrieve,
            database_id=properties_db_id
        )
        
        logger.info("🔍 فحص قاعدة بيانات الملاك...")
        owners_db = await asyncio.to_thread(
            client.databases.retrieve,
            database_id=owners_db_id
        )
        
        print("\n📊 حقول قاعدة بيانات العقارات:")
        for name, field in properties_db["properties"].items():
            print(f"  - {name}: {field['type']}")
        
        print("\n📊 حقول قاعدة بيانات الملاك:")
        for name, field in owners_db["properties"].items():
            print(f"  - {name}: {field['type']}")
        
        # إنشاء عقارين بحقول بسيطة
        await create_simple_properties(client, properties_db_id, owners_db_id)
        
    except Exception as e:
        logger.error(f"❌ خطأ في فحص قواعد البيانات: {e}")

async def create_simple_properties(client, properties_db_id, owners_db_id):
    """إنشاء عقارين بحقول بسيطة"""
    
    logger.info("📝 إنشاء العقارات...")
    
    # بيانات بسيطة للعقارين
    properties = [
        {
            "title": "شقة في التجمع الخامس - 120 متر",
            "region": "التجمع الخامس",
            "type": "شقة",
            "price": "25000",
            "owner": "سارة أحمد",
            "phone": "01234567890"
        },
        {
            "title": "فيلا في الشروق - 250 متر", 
            "region": "الشروق",
            "type": "فيلا",
            "price": "45000",
            "owner": "محمد حسن",
            "phone": "01987654321"
        }
    ]
    
    for i, property_data in enumerate(properties, 1):
        try:
            logger.info(f"📝 إنشاء العقار {i}: {property_data['title']}")
            
            # إنشاء صفحة بحقول أساسية فقط
            page = await asyncio.to_thread(
                client.pages.create,
                parent={"database_id": properties_db_id},
                properties={
                    "Name": {  # اسم الصفحة
                        "title": [
                            {
                                "text": {
                                    "content": property_data["title"]
                                }
                            }
                        ]
                    }
                }
            )
            
            page_id = page["id"]
            logger.info(f"✅ تم إنشاء العقار: {page_id}")
            
            # طباعة رابط العقار
            property_url = f"https://www.notion.so/{page_id.replace('-', '')}"
            print(f"🔗 العقار {i}: {property_url}")
            
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء العقار {i}: {e}")

async def main():
    """الدالة الرئيسية"""
    print("🏠 فحص وإنشاء العقارات في Notion")
    print("=" * 50)
    
    await check_notion_databases()
    
    print("\n✅ تم إكمال الاختبار!")

if __name__ == "__main__":
    asyncio.run(main())