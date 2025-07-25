"""
خدمة Notion - Notion Service  
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from notion_client import Client
from utils.logger import setup_logger

logger = setup_logger(__name__)

class NotionService:
    """خدمة التعامل مع قاعدة بيانات Notion"""
    
    def __init__(self, integration_secret: str, properties_db_id: str, owners_db_id: str):
        self.client = Client(auth=integration_secret)
        self.properties_db_id = properties_db_id
        self.owners_db_id = owners_db_id
        
    async def search_property(self, property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """البحث عن عقار موجود"""
        
        try:
            # البحث بناءً على كود الوحدة
            code_filter = {
                "property": "كود الوحدة",
                "rich_text": {
                    "equals": property_data.get("كود الوحدة", "")
                }
            }
            
            results = await asyncio.to_thread(
                self.client.databases.query,
                database_id=self.properties_db_id,
                filter=code_filter
            )
            
            if results.get("results"):
                logger.info("✅ تم العثور على عقار مطابق")
                return results["results"][0]
                
            # إذا لم نجد بالكود، نبحث بالحقول الأساسية
            complex_filter = {
                "and": [
                    {
                        "property": "رقم المالك",
                        "phone_number": {
                            "equals": property_data.get("رقم المالك", "")
                        }
                    },
                    {
                        "property": "المنطقة", 
                        "select": {
                            "equals": property_data.get("المنطقة", "")
                        }
                    },
                    {
                        "property": "نوع الوحدة",
                        "select": {
                            "equals": property_data.get("نوع الوحدة", "")
                        }
                    }
                ]
            }
            
            results = await asyncio.to_thread(
                self.client.databases.query,
                database_id=self.properties_db_id,
                filter=complex_filter
            )
            
            return results["results"][0] if results.get("results") else None
            
        except Exception as e:
            logger.error(f"❌ خطأ في البحث عن العقار: {e}")
            return None
    
    async def search_owner(self, owner_phone: str) -> Optional[Dict[str, Any]]:
        """البحث عن مالك موجود"""
        
        try:
            owner_filter = {
                "property": "رقم الهاتف",
                "phone_number": {
                    "equals": owner_phone
                }
            }
            
            results = await asyncio.to_thread(
                self.client.databases.query,
                database_id=self.owners_db_id,
                filter=owner_filter
            )
            
            if results.get("results"):
                logger.info("✅ تم العثور على مالك موجود")
                return results["results"][0]
                
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في البحث عن المالك: {e}")
            return None
    
    async def create_property_page(self, property_data: Dict[str, Any], 
                                 owner_id: str = None) -> Optional[str]:
        """إنشاء صفحة عقار جديدة"""
        
        try:
            # إعداد خصائص الصفحة
            properties = {
                "البيان": {
                    "title": [
                        {
                            "text": {
                                "content": property_data.get("البيان", "عقار جديد")
                            }
                        }
                    ]
                },
                "المنطقة": {
                    "select": {
                        "name": property_data.get("المنطقة", "")
                    }
                },
                "كود الوحدة": {
                    "rich_text": [
                        {
                            "text": {
                                "content": property_data.get("كود الوحدة", "")
                            }
                        }
                    ]
                },
                "نوع الوحدة": {
                    "select": {
                        "name": property_data.get("نوع الوحدة", "")
                    }
                },
                "حالة الوحدة": {
                    "select": {
                        "name": property_data.get("حالة الوحدة", "")
                    }
                },
                "المساحة": {
                    "number": int(property_data.get("المساحة", 0)) if property_data.get("المساحة", "").isdigit() else 0
                },
                "الدور": {
                    "rich_text": [
                        {
                            "text": {
                                "content": property_data.get("الدور", "")
                            }
                        }
                    ]
                },
                "السعر": {
                    "number": int(property_data.get("السعر", 0)) if property_data.get("السعر", "").isdigit() else 0
                },
                "المميزات": {
                    "rich_text": [
                        {
                            "text": {
                                "content": property_data.get("المميزات", "")
                            }
                        }
                    ]
                },
                "العنوان": {
                    "rich_text": [
                        {
                            "text": {
                                "content": property_data.get("العنوان", "")
                            }
                        }
                    ]
                },
                "اسم الموظف": {
                    "rich_text": [
                        {
                            "text": {
                                "content": property_data.get("اسم الموظف", "")
                            }
                        }
                    ]
                },
                "رقم المالك": {
                    "phone_number": property_data.get("رقم المالك", "")
                },
                "اتاحة العقار": {
                    "select": {
                        "name": property_data.get("اتاحة العقار", "متاح")
                    }
                },
                "حالة الصور": {
                    "select": {
                        "name": property_data.get("حالة الصور", "بدون صور")
                    }
                },
                "تاريخ الإنشاء": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                }
            }
            
            # ربط المالك إذا كان موجود
            if owner_id:
                properties["المالك"] = {
                    "relation": [
                        {
                            "id": owner_id
                        }
                    ]
                }
            
            # إنشاء الصفحة
            page = await asyncio.to_thread(
                self.client.pages.create,
                parent={"database_id": self.properties_db_id},
                properties=properties
            )
            
            page_id = page["id"]
            
            # إضافة المحتوى إلى الصفحة
            await self._add_property_content(page_id, property_data)
            
            logger.info(f"✅ تم إنشاء صفحة العقار: {page_id}")
            return page_id
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء صفحة العقار: {e}")
            return None
    
    async def create_owner_page(self, property_data: Dict[str, Any]) -> Optional[str]:
        """إنشاء صفحة مالك جديدة"""
        
        try:
            properties = {
                "اسم المالك": {
                    "title": [
                        {
                            "text": {
                                "content": property_data.get("اسم المالك", "مالك جديد")
                            }
                        }
                    ]
                },
                "رقم الهاتف": {
                    "phone_number": property_data.get("رقم المالك", "")
                },
                "عدد العقارات": {
                    "number": 1
                },
                "تاريخ التسجيل": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                }
            }
            
            page = await asyncio.to_thread(
                self.client.pages.create,
                parent={"database_id": self.owners_db_id},
                properties=properties
            )
            
            page_id = page["id"]
            logger.info(f"✅ تم إنشاء صفحة المالك: {page_id}")
            return page_id
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء صفحة المالك: {e}")
            return None
    
    async def update_owner_properties_count(self, owner_id: str) -> bool:
        """تحديث عدد عقارات المالك"""
        
        try:
            # البحث عن عقارات المالك
            owner_filter = {
                "property": "المالك",
                "relation": {
                    "contains": owner_id
                }
            }
            
            results = await asyncio.to_thread(
                self.client.databases.query,
                database_id=self.properties_db_id,
                filter=owner_filter
            )
            
            properties_count = len(results.get("results", []))
            
            # تحديث العدد
            await asyncio.to_thread(
                self.client.pages.update,
                page_id=owner_id,
                properties={
                    "عدد العقارات": {
                        "number": properties_count
                    }
                }
            )
            
            logger.info(f"✅ تم تحديث عدد العقارات للمالك: {properties_count}")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث عدد العقارات: {e}")
            return False
    
    async def _add_property_content(self, page_id: str, property_data: Dict[str, Any]):
        """إضافة محتوى تفصيلي لصفحة العقار"""
        
        try:
            children = [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "تفاصيل العقار"
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": property_data.get("تفاصيل كاملة", "لا توجد تفاصيل متاحة")
                                }
                            }
                        ]
                    }
                }
            ]
            
            await asyncio.to_thread(
                self.client.blocks.children.append,
                block_id=page_id,
                children=children
            )
            
        except Exception as e:
            logger.error(f"❌ خطأ في إضافة المحتوى: {e}")
    
    def get_property_url(self, page_id: str) -> str:
        """الحصول على رابط صفحة العقار"""
        # تنظيف معرف الصفحة من الشرطات
        clean_id = page_id.replace("-", "")
        return f"https://www.notion.so/{clean_id}"
