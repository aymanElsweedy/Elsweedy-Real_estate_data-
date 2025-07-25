"""
نماذج البيانات - Data Models
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class PropertyStatus(Enum):
    """حالات العقار"""
    NEW = "عقار جديد"
    DUPLICATE = "عقار مكرر"
    MULTIPLE = "عقار متعدد"
    SUCCESSFUL = "عقار ناجح"
    FAILED = "عقار فاشل"
    PENDING = "قيد المعالجة"

class PropertyAvailability(Enum):
    """إتاحة العقار"""
    AVAILABLE = "متاح"
    UNAVAILABLE = "غير متاح"
    RESERVED = "محجوز"

class PropertyCondition(Enum):
    """حالة العقار"""
    FURNISHED = "مفروش"
    UNFURNISHED = "غير مفروش"
    SEMI_FURNISHED = "نصف مفروش"

class PropertyType(Enum):
    """نوع العقار"""
    APARTMENT = "شقة"
    VILLA = "فيلا"
    SHOP = "محل"
    OFFICE = "مكتب"
    WAREHOUSE = "مخزن"
    LAND = "أرض"

@dataclass
class PropertyData:
    """نموذج بيانات العقار"""
    
    # المعلومات الأساسية
    region: str = ""  # المنطقة
    unit_code: str = ""  # كود الوحدة
    unit_type: str = ""  # نوع الوحدة
    unit_condition: str = ""  # حالة الوحدة
    area: str = ""  # المساحة
    floor: str = ""  # الدور
    price: str = ""  # السعر
    features: str = ""  # المميزات
    address: str = ""  # العنوان
    
    # معلومات الموظف والمالك
    employee_name: str = ""  # اسم الموظف
    owner_name: str = ""  # اسم المالك
    owner_phone: str = ""  # رقم المالك
    
    # حالة العقار
    availability: str = "متاح"  # اتاحة العقار
    photos_status: str = "بدون صور"  # حالة الصور
    full_details: str = ""  # تفاصيل كاملة
    
    # حقول النظام
    statement: str = ""  # البيان
    status: PropertyStatus = PropertyStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # معرفات خارجية
    telegram_message_id: Optional[int] = None
    notion_property_id: Optional[str] = None
    notion_owner_id: Optional[str] = None
    zoho_lead_id: Optional[str] = None
    
    # بيانات إضافية
    processing_attempts: int = 0
    error_messages: List[str] = field(default_factory=list)
    raw_text: str = ""
    ai_extracted: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            "المنطقة": self.region,
            "كود الوحدة": self.unit_code,
            "نوع الوحدة": self.unit_type,
            "حالة الوحدة": self.unit_condition,
            "المساحة": self.area,
            "الدور": self.floor,
            "السعر": self.price,
            "المميزات": self.features,
            "العنوان": self.address,
            "اسم الموظف": self.employee_name,
            "اسم المالك": self.owner_name,
            "رقم المالك": self.owner_phone,
            "اتاحة العقار": self.availability,
            "حالة الصور": self.photos_status,
            "تفاصيل كاملة": self.full_details,
            "البيان": self.statement
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropertyData':
        """إنشاء من قاموس"""
        property_data = cls()
        
        # تحديث الحقول من القاموس
        field_mapping = {
            "المنطقة": "region",
            "كود الوحدة": "unit_code", 
            "نوع الوحدة": "unit_type",
            "حالة الوحدة": "unit_condition",
            "المساحة": "area",
            "الدور": "floor",
            "السعر": "price",
            "المميزات": "features",
            "العنوان": "address",
            "اسم الموظف": "employee_name",
            "اسم المالك": "owner_name",
            "رقم المالك": "owner_phone",
            "اتاحة العقار": "availability",
            "حالة الصور": "photos_status",
            "تفاصيل كاملة": "full_details",
            "البيان": "statement"
        }
        
        for arabic_key, english_attr in field_mapping.items():
            if arabic_key in data:
                setattr(property_data, english_attr, data[arabic_key])
        
        return property_data
    
    def is_valid(self) -> tuple[bool, List[str]]:
        """التحقق من صحة البيانات"""
        required_fields = [
            ("المنطقة", self.region),
            ("نوع الوحدة", self.unit_type),
            ("حالة الوحدة", self.unit_condition), 
            ("المساحة", self.area),
            ("الدور", self.floor),
            ("السعر", self.price),
            ("اسم المالك", self.owner_name),
            ("رقم المالك", self.owner_phone)
        ]
        
        missing_fields = []
        for field_name, field_value in required_fields:
            if not field_value or not field_value.strip():
                missing_fields.append(field_name)
        
        # التحقق من صحة رقم الهاتف
        if self.owner_phone and not self._validate_phone(self.owner_phone):
            missing_fields.append("رقم المالك (تنسيق غير صحيح)")
        
        # التحقق من أن المساحة والسعر أرقام
        if self.area and not self.area.isdigit():
            missing_fields.append("المساحة (يجب أن يكون رقم)")
            
        if self.price and not self.price.isdigit():
            missing_fields.append("السعر (يجب أن يكون رقم)")
        
        return len(missing_fields) == 0, missing_fields
    
    def _validate_phone(self, phone: str) -> bool:
        """التحقق من صحة رقم الهاتف"""
        clean_phone = ''.join(char for char in phone if char.isdigit())
        return len(clean_phone) == 11 and clean_phone.startswith('01')
    
    def generate_statement(self) -> str:
        """إنشاء البيان"""
        statement_parts = []
        
        if self.unit_type:
            statement_parts.append(f"نوع الوحدة: {self.unit_type}")
        if self.unit_condition:
            statement_parts.append(f"حالة الوحدة: {self.unit_condition}")
        if self.region:
            statement_parts.append(f"المنطقة: {self.region}")
        if self.area:
            statement_parts.append(f"المساحة: {self.area}")
        if self.floor:
            statement_parts.append(f"الدور: {self.floor}")
        if self.price:
            statement_parts.append(f"السعر: {self.price}")
        if self.unit_code:
            statement_parts.append(f"كود الوحدة: {self.unit_code}")
        if self.employee_name:
            statement_parts.append(f"اسم الموظف: {self.employee_name}")
        if self.photos_status:
            statement_parts.append(f"حالة الصور: {self.photos_status}")
        
        self.statement = " | ".join(statement_parts)
        return self.statement
    
    def get_duplicate_check_signature(self) -> str:
        """إنشاء توقيع للتحقق من التكرار"""
        # الحقول المطلوبة للتحقق من التكرار
        signature_parts = [
            self.owner_phone,
            self.region,
            self.unit_type,
            self.unit_condition,
            self.area,
            self.floor
        ]
        
        return "|".join(part.strip().lower() for part in signature_parts if part)
    
    def update_timestamp(self):
        """تحديث وقت التعديل"""
        self.updated_at = datetime.now()
