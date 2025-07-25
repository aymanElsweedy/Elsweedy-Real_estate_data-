"""
قاعدة البيانات المحلية - Local Database
"""

import sqlite3
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from models.property import PropertyData, PropertyStatus
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DatabaseManager:
    """مدير قاعدة البيانات المحلية"""
    
    def __init__(self, db_path: str = "real_estate.db"):
        self.db_path = Path(db_path)
        self.connection = None
        
    async def initialize(self):
        """تهيئة قاعدة البيانات"""
        try:
            self.connection = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,
                isolation_level=None  # autocommit mode
            )
            self.connection.row_factory = sqlite3.Row  # للوصول بالأسماء
            
            await asyncio.to_thread(self._create_tables)
            logger.info("✅ تم تهيئة قاعدة البيانات")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")
            raise
    
    def _create_tables(self):
        """إنشاء الجداول"""
        
        # جدول العقارات
        properties_table = """
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_message_id INTEGER UNIQUE,
            region TEXT,
            unit_code TEXT,
            unit_type TEXT,
            unit_condition TEXT,
            area TEXT,
            floor TEXT,
            price TEXT,
            features TEXT,
            address TEXT,
            employee_name TEXT,
            owner_name TEXT,
            owner_phone TEXT,
            availability TEXT DEFAULT 'متاح',
            photos_status TEXT DEFAULT 'بدون صور',
            full_details TEXT,
            statement TEXT,
            status TEXT DEFAULT 'قيد المعالجة',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notion_property_id TEXT,
            notion_owner_id TEXT,
            zoho_lead_id TEXT,
            processing_attempts INTEGER DEFAULT 0,
            error_messages TEXT,
            raw_text TEXT,
            ai_extracted BOOLEAN DEFAULT 0,
            duplicate_signature TEXT
        )
        """
        
        # جدول المعالجة
        processing_log_table = """
        CREATE TABLE IF NOT EXISTS processing_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER,
            operation TEXT,
            status TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (property_id) REFERENCES properties (id)
        )
        """
        
        # جدول إعدادات النظام
        system_settings_table = """
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # إنشاء الجداول
        cursor = self.connection.cursor()
        cursor.execute(properties_table)
        cursor.execute(processing_log_table)
        cursor.execute(system_settings_table)
        
        # إنشاء الفهارس
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_telegram_message ON properties(telegram_message_id)",
            "CREATE INDEX IF NOT EXISTS idx_owner_phone ON properties(owner_phone)",
            "CREATE INDEX IF NOT EXISTS idx_status ON properties(status)",
            "CREATE INDEX IF NOT EXISTS idx_duplicate_signature ON properties(duplicate_signature)",
            "CREATE INDEX IF NOT EXISTS idx_created_at ON properties(created_at)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    async def save_property(self, property_data: PropertyData) -> int:
        """حفظ عقار في قاعدة البيانات"""
        
        try:
            # إنشاء توقيع التكرار
            duplicate_signature = property_data.get_duplicate_check_signature()
            
            sql = """
            INSERT INTO properties (
                telegram_message_id, region, unit_code, unit_type, unit_condition,
                area, floor, price, features, address, employee_name, owner_name,
                owner_phone, availability, photos_status, full_details, statement,
                status, notion_property_id, notion_owner_id, zoho_lead_id,
                processing_attempts, error_messages, raw_text, ai_extracted,
                duplicate_signature
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                property_data.telegram_message_id,
                property_data.region,
                property_data.unit_code,
                property_data.unit_type,
                property_data.unit_condition,
                property_data.area,
                property_data.floor,
                property_data.price,
                property_data.features,
                property_data.address,
                property_data.employee_name,
                property_data.owner_name,
                property_data.owner_phone,
                property_data.availability,
                property_data.photos_status,
                property_data.full_details,
                property_data.statement,
                property_data.status.value,
                property_data.notion_property_id,
                property_data.notion_owner_id,
                property_data.zoho_lead_id,
                property_data.processing_attempts,
                json.dumps(property_data.error_messages, ensure_ascii=False),
                property_data.raw_text,
                property_data.ai_extracted,
                duplicate_signature
            )
            
            cursor = await asyncio.to_thread(self.connection.execute, sql, values)
            property_id = cursor.lastrowid
            
            logger.info(f"✅ تم حفظ العقار في قاعدة البيانات: {property_id}")
            return property_id
            
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ العقار: {e}")
            raise
    
    async def update_property(self, property_id: int, property_data: PropertyData) -> bool:
        """تحديث عقار موجود"""
        
        try:
            duplicate_signature = property_data.get_duplicate_check_signature()
            
            sql = """
            UPDATE properties SET
                region = ?, unit_code = ?, unit_type = ?, unit_condition = ?,
                area = ?, floor = ?, price = ?, features = ?, address = ?,
                employee_name = ?, owner_name = ?, owner_phone = ?, availability = ?,
                photos_status = ?, full_details = ?, statement = ?, status = ?,
                notion_property_id = ?, notion_owner_id = ?, zoho_lead_id = ?,
                processing_attempts = ?, error_messages = ?, updated_at = CURRENT_TIMESTAMP,
                duplicate_signature = ?
            WHERE id = ?
            """
            
            values = (
                property_data.region, property_data.unit_code, property_data.unit_type,
                property_data.unit_condition, property_data.area, property_data.floor,
                property_data.price, property_data.features, property_data.address,
                property_data.employee_name, property_data.owner_name, property_data.owner_phone,
                property_data.availability, property_data.photos_status, property_data.full_details,
                property_data.statement, property_data.status.value, property_data.notion_property_id,
                property_data.notion_owner_id, property_data.zoho_lead_id,
                property_data.processing_attempts, 
                json.dumps(property_data.error_messages, ensure_ascii=False),
                duplicate_signature, property_id
            )
            
            await asyncio.to_thread(self.connection.execute, sql, values)
            logger.info(f"✅ تم تحديث العقار: {property_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث العقار: {e}")
            return False
    
    async def get_property(self, property_id: int) -> Optional[PropertyData]:
        """الحصول على عقار بالمعرف"""
        
        try:
            sql = "SELECT * FROM properties WHERE id = ?"
            cursor = await asyncio.to_thread(self.connection.execute, sql, (property_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_property_data(row)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على العقار: {e}")
            return None
    
    async def get_property_by_telegram_id(self, telegram_id: int) -> Optional[PropertyData]:
        """الحصول على عقار برقم رسالة Telegram"""
        
        try:
            sql = "SELECT * FROM properties WHERE telegram_message_id = ?"
            cursor = await asyncio.to_thread(self.connection.execute, sql, (telegram_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_property_data(row)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في البحث بمعرف Telegram: {e}")
            return None
    
    async def find_duplicate_properties(self, property_data: PropertyData) -> List[PropertyData]:
        """البحث عن عقارات مكررة"""
        
        try:
            duplicate_signature = property_data.get_duplicate_check_signature()
            
            sql = """
            SELECT * FROM properties 
            WHERE duplicate_signature = ? AND status != 'عقار فاشل'
            ORDER BY created_at DESC
            """
            
            cursor = await asyncio.to_thread(self.connection.execute, sql, (duplicate_signature,))
            rows = cursor.fetchall()
            
            return [self._row_to_property_data(row) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ خطأ في البحث عن العقارات المكررة: {e}")
            return []
    
    async def find_owner_properties(self, owner_phone: str) -> List[PropertyData]:
        """البحث عن عقارات المالك"""
        
        try:
            sql = """
            SELECT * FROM properties 
            WHERE owner_phone = ? AND status != 'عقار فاشل'
            ORDER BY created_at DESC
            """
            
            cursor = await asyncio.to_thread(self.connection.execute, sql, (owner_phone,))
            rows = cursor.fetchall()
            
            return [self._row_to_property_data(row) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ خطأ في البحث عن عقارات المالك: {e}")
            return []
    
    async def get_pending_properties(self) -> List[PropertyData]:
        """الحصول على العقارات المعلقة"""
        
        try:
            sql = """
            SELECT * FROM properties 
            WHERE status IN ('قيد المعالجة', 'عقار فاشل')
            ORDER BY created_at ASC
            """
            
            cursor = await asyncio.to_thread(self.connection.execute, sql)
            rows = cursor.fetchall()
            
            return [self._row_to_property_data(row) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على العقارات المعلقة: {e}")
            return []
    
    async def log_processing_step(self, property_id: int, operation: str, 
                                status: str, details: str = ""):
        """تسجيل خطوة معالجة"""
        
        try:
            sql = """
            INSERT INTO processing_log (property_id, operation, status, details)
            VALUES (?, ?, ?, ?)
            """
            
            await asyncio.to_thread(
                self.connection.execute, 
                sql, 
                (property_id, operation, status, details)
            )
            
        except Exception as e:
            logger.error(f"❌ خطأ في تسجيل خطوة المعالجة: {e}")
    
    def _row_to_property_data(self, row) -> PropertyData:
        """تحويل صف قاعدة البيانات إلى PropertyData"""
        
        property_data = PropertyData()
        
        # الحقول الأساسية
        property_data.region = row['region'] or ""
        property_data.unit_code = row['unit_code'] or ""
        property_data.unit_type = row['unit_type'] or ""
        property_data.unit_condition = row['unit_condition'] or ""
        property_data.area = row['area'] or ""
        property_data.floor = row['floor'] or ""
        property_data.price = row['price'] or ""
        property_data.features = row['features'] or ""
        property_data.address = row['address'] or ""
        property_data.employee_name = row['employee_name'] or ""
        property_data.owner_name = row['owner_name'] or ""
        property_data.owner_phone = row['owner_phone'] or ""
        property_data.availability = row['availability'] or "متاح"
        property_data.photos_status = row['photos_status'] or "بدون صور"
        property_data.full_details = row['full_details'] or ""
        property_data.statement = row['statement'] or ""
        
        # الحالة والتواريخ
        property_data.status = PropertyStatus(row['status'])
        if row['created_at']:
            property_data.created_at = datetime.fromisoformat(row['created_at'])
        if row['updated_at']:
            property_data.updated_at = datetime.fromisoformat(row['updated_at'])
        
        # المعرفات
        property_data.telegram_message_id = row['telegram_message_id']
        property_data.notion_property_id = row['notion_property_id']
        property_data.notion_owner_id = row['notion_owner_id']
        property_data.zoho_lead_id = row['zoho_lead_id']
        
        # بيانات المعالجة
        property_data.processing_attempts = row['processing_attempts'] or 0
        property_data.raw_text = row['raw_text'] or ""
        property_data.ai_extracted = bool(row['ai_extracted'])
        
        # رسائل الخطأ
        if row['error_messages']:
            try:
                property_data.error_messages = json.loads(row['error_messages'])
            except:
                property_data.error_messages = []
        
        return property_data
    
    async def get_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات النظام"""
        
        try:
            stats = {}
            
            # إحصائيات العقارات حسب الحالة
            sql = """
            SELECT status, COUNT(*) as count 
            FROM properties 
            GROUP BY status
            """
            cursor = await asyncio.to_thread(self.connection.execute, sql)
            status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
            stats['status_counts'] = status_counts
            
            # إحصائيات اليوم
            sql = """
            SELECT COUNT(*) as today_count 
            FROM properties 
            WHERE DATE(created_at) = DATE('now', 'localtime')
            """
            cursor = await asyncio.to_thread(self.connection.execute, sql)
            stats['today_count'] = cursor.fetchone()['today_count']
            
            # إجمالي العقارات
            sql = "SELECT COUNT(*) as total FROM properties"
            cursor = await asyncio.to_thread(self.connection.execute, sql)
            stats['total_properties'] = cursor.fetchone()['total']
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على الإحصائيات: {e}")
            return {}
    
    async def close(self):
        """إغلاق الاتصال"""
        if self.connection:
            self.connection.close()
            logger.info("✅ تم إغلاق اتصال قاعدة البيانات")
