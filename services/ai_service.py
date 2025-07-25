"""
خدمة الذكاء الاصطناعي المحدثة - AI Service with Multiple Providers
"""

import json
import asyncio
import re
from typing import Dict, Any, Optional, List
import aiohttp
from datetime import datetime
import anthropic
from anthropic import Anthropic
from utils.logger import setup_logger

logger = setup_logger(__name__)

class AIService:
    """خدمة معالجة النصوص بالذكاء الاصطناعي مع عدة مزودين"""

    def __init__(self, config):
        self.config = config

        # تهيئة جميع مزودي الذكاء الاصطناعي
        self.anthropic_client = None
        if config.ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

        self.ai_providers = [
            {"name": "Gemini", "key": config.GEMINI_API_KEY, "method": self._extract_with_gemini},
            {"name": "OpenAI", "key": config.OPENAI_API_KEY, "method": self._extract_with_openai},
            {"name": "Copilot", "key": config.COPILOT_API_KEY, "method": self._extract_with_copilot},
            {"name": "Mistral", "key": config.MISTRAL_API_KEY, "method": self._extract_with_mistral},
            {"name": "Groq", "key": config.GROQ_API_KEY, "method": self._extract_with_groq}
        ]

        # فلترة المزودين المتاحين فقط
        self.available_providers = [p for p in self.ai_providers if p["key"]]

    async def extract_property_data(self, raw_text: str, allow_logical_analysis: bool = True) -> Optional[Dict[str, Any]]:
        """استخراج بيانات العقار من النص الخام مع سلسلة المزودين"""

        logger.info("🤖 بدء سلسلة استخراج البيانات بالذكاء الاصطناعي")

        # تجربة كل مزود بالتتابع
        for provider in self.available_providers:
            logger.info(f"🔄 تجربة {provider['name']}...")

            # 3 محاولات لكل مزود
            for attempt in range(3):
                try:
                    logger.info(f"📝 المحاولة {attempt + 1}/3 مع {provider['name']}")

                    result = await provider["method"](raw_text)
                    if result:
                        logger.info(f"✅ نجح استخراج البيانات مع {provider['name']}")

                        # إضافة حقل البيان المدمج
                        result["البيان"] = self._generate_property_statement(result)
                        return result

                except Exception as e:
                    logger.warning(f"⚠️ فشل {provider['name']} - المحاولة {attempt + 1}: {e}")

                # فاصل زمني 15 ثانية بين المحاولات
                if attempt < 2:
                    await asyncio.sleep(15)

            logger.error(f"❌ فشل {provider['name']} في جميع المحاولات")

        # في حال فشل جميع المزودين
        logger.warning("⚠️ فشل جميع مزودي الذكاء الاصطناعي")

        if allow_logical_analysis:
            # طلب إذن للتحليل المنطقي
            logger.info("🤔 هل تريد المتابعة بالتحليل المنطقي؟")
            # TODO: إضافة آلية طلب الإذن من المستخدم

            # التحليل المنطقي كحل أخير
            return await self._logical_analysis(raw_text)

        return None

    async def _extract_with_gemini(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """استخراج البيانات باستخدام Gemini"""

        if not self.config.GEMINI_API_KEY:
            return None

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.config.GEMINI_API_KEY}"

            payload = {
                "contents": [{
                    "parts": [{
                        "text": self._get_extraction_prompt() + raw_text
                    }]
                }]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["candidates"][0]["content"]["parts"][0]["text"]
                        return self._parse_json_response(content)

        except Exception as e:
            logger.error(f"خطأ في Gemini: {e}")

        return None

    async def _extract_with_openai(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """استخراج البيانات باستخدام OpenAI"""

        if not self.config.OPENAI_API_KEY:
            return None

        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.config.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "user", "content": self._get_extraction_prompt() + raw_text}
                ],
                "max_tokens": 1000,
                "temperature": 0.1
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        return self._parse_json_response(content)

        except Exception as e:
            logger.error(f"خطأ في OpenAI: {e}")

        return None

    async def _extract_with_copilot(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """استخراج البيانات باستخدام Copilot"""

        if not self.config.COPILOT_API_KEY:
            return None

        try:
            # TODO: تطبيق API Copilot الفعلي
            logger.info("🔧 Copilot API قيد التطوير")
            return None

        except Exception as e:
            logger.error(f"خطأ في Copilot: {e}")

        return None

    async def _extract_with_mistral(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """استخراج البيانات باستخدام Mistral"""

        if not self.config.MISTRAL_API_KEY:
            return None

        try:
            url = "https://api.mistral.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.config.MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "mistral-large-latest",
                "messages": [
                    {"role": "user", "content": self._get_extraction_prompt() + raw_text}
                ],
                "max_tokens": 1000,
                "temperature": 0.1
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        return self._parse_json_response(content)

        except Exception as e:
            logger.error(f"خطأ في Mistral: {e}")

        return None

    async def _extract_with_groq(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """استخراج البيانات باستخدام Groq"""

        if not self.config.GROQ_API_KEY:
            return None

        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "llama-3.1-70b-versatile",
                "messages": [
                    {"role": "user", "content": self._get_extraction_prompt() + raw_text}
                ],
                "max_tokens": 1000,
                "temperature": 0.1
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        return self._parse_json_response(content)

        except Exception as e:
            logger.error(f"خطأ في Groq: {e}")

        return None

    async def _logical_analysis(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """التحليل المنطقي للنص كحل أخير"""

        logger.info("🧠 بدء التحليل المنطقي...")

        try:
            # تحليل منطقي بسيط باستخدام regex وقواعد النص
            extracted_data = {}

            # استخراج رقم الهاتف
            phone_pattern = r'01[0-9]{9}'
            phone_match = re.search(phone_pattern, raw_text)
            if phone_match:
                extracted_data["رقم المالك"] = phone_match.group()

            # استخراج الأسعار
            price_patterns = [
                r'(\d+)\s*ألف',
                r'(\d+)\s*الف',
                r'(\d+),000',
                r'(\d{4,})'
            ]

            for pattern in price_patterns:
                price_match = re.search(pattern, raw_text)
                if price_match:
                    price = price_match.group(1)
                    if 'ألف' in price_match.group() or 'الف' in price_match.group():
                        price = str(int(price) * 1000)
                    extracted_data["السعر"] = price
                    break

            # استخراج المساحة
            area_pattern = r'(\d+)\s*متر'
            area_match = re.search(area_pattern, raw_text)
            if area_match:
                extracted_data["المساحة"] = area_match.group(1)

            # تحديد المنطقة من النص
            regions_map = {
                'تجمع': 'احياء تجمع',
                'اندلس': 'اندلس',
                'رحاب': 'رحاب',
                'جاردينيا': 'جاردينيا هايتس'
            }

            for keyword, region in regions_map.items():
                if keyword in raw_text:
                    extracted_data["المنطقة"] = region
                    break

            # تحديد نوع الوحدة
            if 'شقة' in raw_text or 'شقه' in raw_text:
                extracted_data["نوع الوحدة"] = "شقة"
            elif 'فيلا' in raw_text:
                extracted_data["نوع الوحدة"] = "فيلا"
            elif 'دوبلكس' in raw_text:
                extracted_data["نوع الوحدة"] = "دوبلكس"

            # تحديد حالة الوحدة
            if 'مفروش' in raw_text:
                extracted_data["حالة الوحدة"] = "مفروش"
            elif 'فاضي' in raw_text or 'فاضية' in raw_text:
                extracted_data["حالة الوحدة"] = "فاضي"
            elif 'تمليك' in raw_text:
                extracted_data["حالة الوحدة"] = "تمليك"

            # إكمال الحقول الناقصة بالقيم الافتراضية
            self._fill_default_values(extracted_data)

            # إنشاء كود الوحدة
            extracted_data["كود الوحدة"] = self._generate_unit_code(extracted_data)

            # البيان المدمج
            extracted_data["البيان"] = self._generate_property_statement(extracted_data)

            logger.info("✅ تم التحليل المنطقي بنجاح")
            return extracted_data

        except Exception as e:
            logger.error(f"❌ خطأ في التحليل المنطقي: {e}")

        return None

    def _get_extraction_prompt(self) -> str:
        """الحصول على prompt استخراج البيانات المحدث وفقاً للدليل الجديد"""

        return """
أنت خبير في استخراج بيانات العقارات من النصوص العربية وفقاً لدليل التحليل المحدث.
مهمتك هي تحليل النص المرفق واستخراج المعلومات التالية بدقة تامة:

## قواعد تحليل الحقول الإلزامية:

### المنطقة [المنطقة: ...]
تُحدد المنطقة بناءً على الزونات المحددة:
- z1: دار قرنفل، قرنفل فيلات، بنفسج، ياسمين، ج ش اكاديميه
- z3: سكن شباب، مستقبل، هناجر، نزهه ثالث
- z4: رحاب، جاردينيا سيتي
- z5: كمباوندات، احياء تجمع، بيت وطن، نرجس، لوتس، شويفات، زيزينيا، اندلس، دار اندلس، سكن اندلس، سكن معارض، جنه، جاردينيا هايتس

قواعد إضافية:
- "الحي الخامس" أو "الحي الرابع" → "احياء تجمع"
- "الشباب" أو "التجمع الثالث" أو "اسكان الثالث" → "اسكان شباب"
- إذا لم تُذكر المنطقة، يجب إيقاف التحليل

### نوع الوحدة [نوع الوحدة: ...]
القيم المسموح بها: شقة، فيلا، دوبلكس، بنتهاوس
إذا لم تُذكر، يجب إيقاف التحليل

### حالة الوحدة [حالة الوحدة: ...]
القيم المسموح بها: فاضي، مفروش، تمليك
إذا لم تُذكر، يجب إيقاف التحليل

## الحقول الأخرى:

### المساحة [المساحة: أرقام فقط]
- أرقام فقط، القيمة الافتراضية: 00

### الدور [الدور: بصيغة "دور تاني" بدون "ال"]
- بصيغة مثل "دور تاني" بدون "ال" التعريف
- القيمة الافتراضية: "غير محدد"

### السعر [السعر: أرقام فقط]
- أرقام فقط، القيمة الافتراضية: 00

### المميزات [المميزات: من القائمة فقط]
القيم المسموح بها: تشطيب سوبر لوكس، مدخل خاص، دبل فيس، اسانسير، حصه في ارض، حديقه، فيو مفتوح، فيو جاردن، مسجله شهر عقاري، تقسيط، مكيفه، باقي اقساط
القيمة الافتراضية: "غير محدد"

### العنوان [العنوان: نص قصير]
نص قصير من البيان، القيمة الافتراضية: "غير محدد"

### اسم الموظف [اسم الموظف: من كلمة "تبع"]
الأسماء المعتمدة: بلبل، اسلام، ايمن، تاحه، علياء، محمود سامي، يوسف، عماد، يوسف الجوهري
القيمة الافتراضية: "غير محدد"

### اسم المالك [اسم المالك: اسم كامل]
اسم شخص كامل، القيمة الافتراضية: "غير محدد"

### رقم المالك [رقم المالك: 11 رقم]
رقم مكون من 11 رقم، القيمة الافتراضية: "01000000000"

### اتاحة العقار [اتاحة العقار: متاح، غير متاح، مؤجر]
القيم المسموح بها: متاح، غير متاح، مؤجر
القيمة الافتراضية: "غير محدد"

### حالة الصور [حالة الصور: بصور، بدون صور، صور غير محددة]
القيم المسموح بها: بصور، بدون صور، صور غير محددة
القيمة الافتراضية: "صور غير محددة"

### تفاصيل كاملة [تفاصيل كاملة: النص الأصلي]
النص الأصلي الكامل بعد حذف حقول "اسم المالك" و"رقم المالك" و "اتاحة العقار" و "حالة الصور"
يجب أن يُكتب في سطر واحد فقط بدون أسطر جديدة

## تعليمات مهمة:
1. إذا غابت "المنطقة" أو "نوع الوحدة" أو "حالة الوحدة"، أرجع null
2. استخدم القيم الافتراضية للحقول الأخرى المفقودة
3. أرجع النتيجة في صيغة JSON فقط، بدون أي نص إضافي
4. تأكد من دقة استخراج جميع الحقول وفقاً للقواعد المحددة

النص للتحليل:
"""

    def _parse_json_response(self, content: str) -> Optional[Dict[str, Any]]:
        """تحليل استجابة JSON من مزودي الذكاء الاصطناعي"""

        try:
            # إزالة أي نص إضافي قبل أو بعد JSON
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1

            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                property_data = json.loads(json_str)

                # التحقق من الحقول الإلزامية
                required_fields = ["المنطقة", "نوع الوحدة", "حالة الوحدة"]
                for field in required_fields:
                    if not property_data.get(field):
                        logger.warning(f"⚠️ حقل إلزامي مفقود: {field}")
                        return None

                # إكمال الحقول الناقصة
                self._fill_default_values(property_data)

                # إنشاء كود الوحدة
                property_data["كود الوحدة"] = self._generate_unit_code(property_data)

                return property_data
            else:
                logger.error("❌ لم يتم العثور على JSON صالح في الاستجابة")

        except json.JSONDecodeError as e:
            logger.error(f"❌ خطأ في تحليل JSON: {e}")
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الاستجابة: {e}")

        return None

    def _fill_default_values(self, property_data: Dict[str, Any]):
        """إكمال القيم الافتراضية للحقول المفقودة"""

        defaults = {
            "المساحة": "00",
            "الدور": "غير محدد",
            "السعر": "00",
            "المميزات": "غير محدد",
            "العنوان": "غير محدد",
            "اسم الموظف": "غير محدد",
            "اسم المالك": "غير محدد",
            "رقم المالك": "01000000000",
            "اتاحة العقار": "غير محدد",
            "حالة الصور": "صور غير محددة",
            "تفاصيل كاملة": property_data.get("raw_text", "غير محدد")
        }

        for field, default_value in defaults.items():
            if not property_data.get(field):
                property_data[field] = default_value

    def _generate_unit_code(self, property_data: Dict[str, Any]) -> str:
        """إنشاء كود الوحدة وفقاً للدليل الجديد"""

        # خريطة حالة الوحدة (t1, t2, t3 → 1, 2, 3)
        condition_map = {
            "فاضي": "1",     # t1 → 1
            "مفروش": "2",    # t2 → 2
            "تمليك": "3"     # t3 → 3
        }

        # خريطة المناطق الجديدة وفقاً للدليل
        region_map = {
            # z1
            "دار قرنفل": "1", "قرنفل فيلات": "1", "بنفسج": "1", "ياسمين": "1", "ج ش اكاديميه": "1",
            # z3  
            "سكن شباب": "3", "اسكان شباب": "3", "مستقبل": "3", "هناجر": "3", "نزهه ثالث": "3",
            # z4
            "رحاب": "4", "جاردينيا سيتي": "4",
            # z5
            "كمباوندات": "5", "احياء تجمع": "5", "بيت وطن": "5", "نرجس": "5", "لوتس": "5", 
            "شويفات": "5", "زيزينيا": "5", "اندلس": "5", "دار اندلس": "5", "سكن اندلس": "5", 
            "سكن معارض": "5", "جنه": "5", "جاردينيا هايتس": "5"
        }

        # الحصول على رموز الكود
        condition_code = condition_map.get(property_data.get("حالة الوحدة"), "1")
        region_code = region_map.get(property_data.get("المنطقة"), "5")

        # التاريخ الحالي بصيغة DDMMYY
        current_date = datetime.now().strftime("%d%m%y")

        # رقم تسلسلي (يمكن تمريره من الخارج)
        serial = property_data.get("serial_number", "1")

        # تنسيق الكود: c000-{حالة}-z{منطقة}-{تاريخ}-وحدة-{تسلسلي}
        return f"c000-{condition_code}-z{region_code}-{current_date}-وحدة-{serial}"

    def _generate_property_statement(self, property_data: Dict[str, Any]) -> str:
        """إنشاء بيان العقار المدمج وفقاً للدليل الجديد - تنسيق خاص بأقواس مربعة"""

        # ترتيب الحقول وفقاً للدليل الجديد
        statement_fields = [
            "المنطقة",
            "كود الوحدة",
            "نوع الوحدة", 
            "حالة الوحدة",
            "المساحة",
            "الدور",
            "السعر",
            "المميزات",
            "العنوان",
            "اسم الموظف",
            "اسم المالك",
            "رقم المالك",
            "اتاحة العقار",
            "حالة الصور",
            "تفاصيل كاملة"
        ]

        statement_parts = []
        for field in statement_fields:
            value = property_data.get(field, "غير محدد")
            if value and value != "غير محدد":
                statement_parts.append(f"[{field}: {value}]")
            elif field in ["المنطقة", "كود الوحدة", "نوع الوحدة", "حالة الوحدة"]:
                # الحقول الإلزامية يجب أن تظهر حتى لو كانت فارغة
                statement_parts.append(f"[{field}: {value}]")

        # تنسيق البيان مع أسطر منفصلة
        return "\n".join(statement_parts)

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
            if not value or value == "غير محدد":
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