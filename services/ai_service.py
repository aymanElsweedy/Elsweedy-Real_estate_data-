"""
خدمة الذكاء الاصطناعي - AI Service
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
import anthropic
from anthropic import Anthropic
from utils.logger import setup_logger

logger = setup_logger(__name__)

class AIService:
    """خدمة معالجة النصوص بالذكاء الاصطناعي"""
    
    def __init__(self, api_key: str):
        # The newest Anthropic model is "claude-sonnet-4-20250514", not "claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022" nor "claude-3-sonnet-20240229". 
        # If the user doesn't specify a model, always prefer using "claude-sonnet-4-20250514" as it is the latest model.
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        
    async def extract_property_data(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """استخراج بيانات العقار من النص الخام"""
        
        prompt = """
أنت خبير في استخراج بيانات العقارات من النصوص العربية. 
مهمتك هي تحليل النص المرفق واستخراج المعلومات التالية بدقة:

الحقول المطلوبة:
- المنطقة: اسم المنطقة أو الحي
- كود الوحدة: الرقم التعريفي للوحدة
- نوع الوحدة: (شقة، فيلا، محل، مكتب، إلخ)
- حالة الوحدة: (مفروش، غير مفروش، نصف مفروش)
- المساحة: المساحة بالمتر المربع (رقم فقط)
- الدور: رقم الدور أو وصفه
- السعر: السعر بالجنيه (رقم فقط)
- المميزات: قائمة المميزات مفصولة بفاصلة
- العنوان: العنوان التفصيلي
- اسم الموظف: اسم الموظف المسؤول
- اسم المالك: اسم مالك العقار
- رقم المالك: رقم هاتف المالك
- اتاحة العقار: (متاح، غير متاح، محجوز)
- حالة الصور: (بصور، بدون صور)
- تفاصيل كاملة: ملخص شامل للعقار

أرجع النتيجة في صيغة JSON فقط، بدون أي نص إضافي.

مثال للإخراج:
{
  "المنطقة": "جاردينيا هايتس",
  "كود الوحدة": "000-1-5-220725-123",
  "نوع الوحدة": "شقة",
  "حالة الوحدة": "مفروش",
  "المساحة": "150",
  "الدور": "دور تالت",
  "السعر": "20000",
  "المميزات": "مكيفه, فيو مفتوح, اسانسير, انترنت",
  "العنوان": "شارع التسعين الشمالي، التجمع الخامس",
  "اسم الموظف": "يوسف عماد",
  "اسم المالك": "هدي المفتي",
  "رقم المالك": "01000011109",
  "اتاحة العقار": "متاح",
  "حالة الصور": "بصور",
  "تفاصيل كاملة": "شقة مفروشة بالكامل في التجمع الخامس، 150 متر، دور ثالث، مكيفة، فيو مفتوح، اسانسير، انترنت، إيجار شهري 20000 جنيه."
}

النص للتحليل:
"""
        
        try:
            message = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt + raw_text
                    }
                ]
            )
            
            content = message.content[0].text.strip()
            
            # إزالة أي نص إضافي قبل أو بعد JSON
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                property_data = json.loads(json_str)
                
                # إضافة حقل البيان المدمج
                property_data["البيان"] = self._generate_property_statement(property_data)
                
                logger.info("✅ تم استخراج بيانات العقار بنجاح")
                return property_data
            else:
                logger.error("❌ لم يتم العثور على JSON صالح في الاستجابة")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ خطأ في تحليل JSON: {e}")
        except Exception as e:
            logger.error(f"❌ خطأ في استخراج البيانات: {e}")
            
        return None
    
    def _generate_property_statement(self, property_data: Dict[str, Any]) -> str:
        """إنشاء بيان العقار المدمج"""
        
        statement_fields = [
            "نوع الوحدة",
            "حالة الوحدة", 
            "المنطقة",
            "المساحة",
            "الدور",
            "السعر",
            "كود الوحدة",
            "اسم الموظف",
            "حالة الصور"
        ]
        
        statement_parts = []
        for field in statement_fields:
            value = property_data.get(field, "")
            if value:
                statement_parts.append(f"{field}: {value}")
        
        return " | ".join(statement_parts)
    
    async def validate_property_data(self, property_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """التحقق من صحة بيانات العقار"""
        
        required_fields = [
            "المنطقة",
            "نوع الوحدة", 
            "حالة الوحدة",
            "المساحة",
            "الدور",
            "السعر",
            "اسم المالك",
            "رقم المالك"
        ]
        
        missing_fields = []
        invalid_fields = []
        
        for field in required_fields:
            value = property_data.get(field, "").strip()
            if not value:
                missing_fields.append(field)
            elif field in ["المساحة", "السعر"] and not value.isdigit():
                invalid_fields.append(f"{field} (يجب أن يكون رقم)")
            elif field == "رقم المالك" and not self._validate_phone_number(value):
                invalid_fields.append(f"{field} (تنسيق غير صحيح)")
        
        errors = missing_fields + invalid_fields
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("✅ بيانات العقار صحيحة")
        else:
            logger.warning(f"⚠️ مشاكل في البيانات: {', '.join(errors)}")
        
        return is_valid, errors
    
    def _validate_phone_number(self, phone: str) -> bool:
        """التحقق من صحة رقم الهاتف"""
        # إزالة المسافات والرموز
        clean_phone = ''.join(char for char in phone if char.isdigit())
        
        # التحقق من أن الرقم يبدأ بـ 01 ويحتوي على 11 رقم
        return len(clean_phone) == 11 and clean_phone.startswith('01')
    
    async def enhance_property_description(self, property_data: Dict[str, Any]) -> str:
        """تحسين وصف العقار"""
        
        prompt = f"""
بناءً على البيانات التالية للعقار، اكتب وصفاً تسويقياً جذاباً ومختصراً:

البيانات:
{json.dumps(property_data, ensure_ascii=False, indent=2)}

الوصف يجب أن يكون:
- مختصر (لا يتجاوز 200 كلمة)
- جذاب وتسويقي
- يركز على المميزات الرئيسية
- باللغة العربية
- بدون مقدمات أو خاتمات

أرجع الوصف فقط بدون أي نص إضافي.
"""
        
        try:
            message = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            enhanced_description = message.content[0].text.strip()
            logger.info("✅ تم تحسين وصف العقار")
            return enhanced_description
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحسين الوصف: {e}")
            return property_data.get("تفاصيل كاملة", "")
