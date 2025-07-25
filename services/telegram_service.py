
"""
خدمة Telegram المحدثة - Telegram Service with Dual Bots and Tagging
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from utils.logger import setup_logger

logger = setup_logger(__name__)

class TelegramService:
    """خدمة التعامل مع Telegram مع دعم البوتين والوسم"""
    
    def __init__(self, config):
        self.config = config
        self.main_bot_token = config.TELEGRAM_BOT_TOKEN
        self.notification_bot_token = config.TELEGRAM_NOTIFICATION_BOT_TOKEN
        self.channel_id = config.TELEGRAM_CHANNEL_ID
        self.archive_channel_id = config.TELEGRAM_ARCHIVE_CHANNEL_ID
        
        self.main_bot_url = f"https://api.telegram.org/bot{self.main_bot_token}"
        # إذا لم يكن بوت الإشعارات متاحاً، استخدم البوت الرئيسي
        if self.notification_bot_token and self.notification_bot_token.strip():
            self.notification_bot_url = f"https://api.telegram.org/bot{self.notification_bot_token}"
        else:
            self.notification_bot_url = self.main_bot_url
            logger.warning("⚠️ بوت الإشعارات غير متاح - سيتم استخدام البوت الرئيسي")
        
        self.session = None
        
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_channel_messages(self, limit: int = 100, apply_filter: bool = True) -> List[Dict[str, Any]]:
        """الحصول على رسائل القناة مع تطبيق فلتر الوسم"""
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            url = f"{self.main_bot_url}/getUpdates"
            params = {"limit": limit, "allowed_updates": ["channel_post"]}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("ok"):
                        messages = []
                        for update in data.get("result", []):
                            if "channel_post" in update:
                                channel_post = update["channel_post"]
                                if str(channel_post.get("chat", {}).get("id")) == self.channel_id:
                                    formatted_message = self._format_message(channel_post)
                                    
                                    # تطبيق فلتر الوسم
                                    if apply_filter and self._should_process_message(formatted_message):
                                        messages.append(formatted_message)
                                    elif not apply_filter:
                                        messages.append(formatted_message)
                        
                        logger.info(f"✅ تم الحصول على {len(messages)} رسالة من القناة")
                        return messages
                    else:
                        logger.error(f"❌ خطأ API: {data.get('description')}")
                else:
                    logger.error(f"❌ خطأ HTTP: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على الرسائل: {e}")
            
        return []
    
    def _should_process_message(self, message: Dict[str, Any]) -> bool:
        """تحديد ما إذا كان يجب معالجة الرسالة أم لا بناءً على الفلترة"""
        
        text = message.get("text", "")
        
        # تخطي الرسائل الموسومة بـ "عقار ناجح"
        if self.config.SUCCESS_TAG in text:
            return False
        
        # تطبيق فلتر التاريخ إذا كان مفعلاً
        if self.config.APPLY_DATE_FILTER and self.config.LAST_SUCCESS_DATE:
            try:
                last_success_date = datetime.fromisoformat(self.config.LAST_SUCCESS_DATE)
                message_date = message.get("date")
                
                if isinstance(message_date, datetime) and message_date < last_success_date:
                    return False
            except Exception as e:
                logger.warning(f"⚠️ خطأ في فلتر التاريخ: {e}")
        
        # معالجة الرسائل النصية فقط
        return bool(text.strip())
    
    def _format_message(self, channel_post: Dict[str, Any]) -> Dict[str, Any]:
        """تنسيق الرسالة"""
        return {
            "message_id": channel_post.get("message_id"),
            "text": channel_post.get("text", ""),
            "date": datetime.fromtimestamp(channel_post.get("date", 0)),
            "chat_id": channel_post.get("chat", {}).get("id"),
            "entities": channel_post.get("entities", []),
            "reply_markup": channel_post.get("reply_markup", {}),
            "raw_data": channel_post
        }
    
    async def send_message_to_channel(self, text: str, parse_mode: str = "HTML") -> bool:
        """إرسال رسالة إلى القناة باستخدام البوت الرئيسي"""
        return await self.send_message(text, parse_mode, use_main_bot=True)
    
    async def send_notification(self, text: str, parse_mode: str = "HTML") -> bool:
        """إرسال إشعار باستخدام بوت الإشعارات"""
        if self.notification_bot_token and self.notification_bot_token.strip():
            logger.info("📢 إرسال إشعار باستخدام بوت الإشعارات")
            return await self.send_message(text, parse_mode, use_main_bot=False)
        else:
            logger.warning("⚠️ بوت الإشعارات غير متاح - استخدام البوت الرئيسي")
            return await self.send_message(text, parse_mode, use_main_bot=True)
    
    async def send_message(self, text: str, parse_mode: str = "HTML", use_main_bot: bool = True) -> bool:
        """إرسال رسالة إلى القناة"""
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # اختيار البوت المناسب
            bot_url = self.main_bot_url if use_main_bot else self.notification_bot_url
            
            url = f"{bot_url}/sendMessage"
            data = {
                "chat_id": self.channel_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("ok"):
                        if use_main_bot:
                            bot_name = "الرئيسي"
                        else:
                            bot_name = "الإشعارات" if (self.notification_bot_token and self.notification_bot_token.strip()) else "الرئيسي (احتياطي)"
                        logger.info(f"✅ تم إرسال الرسالة بواسطة بوت {bot_name}")
                        return True
                    else:
                        logger.error(f"❌ خطأ في إرسال الرسالة: {result.get('description')}")
                else:
                    logger.error(f"❌ خطأ HTTP في إرسال الرسالة: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال الرسالة: {e}")
            
        return False
    
    async def delete_message(self, message_id: int) -> bool:
        """حذف رسالة"""
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            url = f"{self.main_bot_url}/deleteMessage"
            data = {
                "chat_id": self.channel_id,
                "message_id": message_id
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("ok"):
                        logger.info(f"✅ تم حذف الرسالة {message_id}")
                        return True
                    else:
                        logger.error(f"❌ خطأ في حذف الرسالة: {result.get('description')}")
                else:
                    logger.error(f"❌ خطأ HTTP في حذف الرسالة: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في حذف الرسالة: {e}")
            
        return False
    
    async def edit_message(self, message_id: int, new_text: str, parse_mode: str = "HTML") -> bool:
        """تعديل رسالة"""
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            url = f"{self.main_bot_url}/editMessageText"
            data = {
                "chat_id": self.channel_id,
                "message_id": message_id,
                "text": new_text,
                "parse_mode": parse_mode
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("ok"):
                        logger.info(f"✅ تم تعديل الرسالة {message_id}")
                        return True
                    else:
                        logger.error(f"❌ خطأ في تعديل الرسالة: {result.get('description')}")
                else:
                    logger.error(f"❌ خطأ HTTP في تعديل الرسالة: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في تعديل الرسالة: {e}")
            
        return False
    
    async def add_message_tag(self, message_id: int, tag: str) -> bool:
        """إضافة وسم للرسالة عبر التعديل"""
        
        try:
            # الحصول على النص الأصلي للرسالة
            original_text = await self._get_message_text(message_id)
            if not original_text:
                return False
            
            # إضافة الوسم في بداية الرسالة
            tagged_text = f"{tag}\n\n{original_text}"
            
            # تعديل الرسالة مع الوسم
            return await self.edit_message(message_id, tagged_text)
            
        except Exception as e:
            logger.error(f"❌ خطأ في إضافة الوسم: {e}")
            return False
    
    async def _get_message_text(self, message_id: int) -> Optional[str]:
        """الحصول على نص الرسالة"""
        
        try:
            # في Telegram API، لا يمكن الحصول على رسالة واحدة مباشرة
            # لذا نحصل على آخر الرسائل ونبحث عن المطلوبة
            messages = await self.get_channel_messages(limit=100, apply_filter=False)
            
            for message in messages:
                if message["message_id"] == message_id:
                    return message["text"]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على نص الرسالة: {e}")
            return None
    
    async def send_to_archive(self, text: str, original_message_id: int) -> bool:
        """إرسال الرسالة إلى القناة الأرشيفية"""
        
        if not self.archive_channel_id:
            logger.warning("⚠️ لم يتم تعيين قناة الأرشيف")
            return False
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            url = f"{self.main_bot_url}/sendMessage"
            
            # إضافة معلومات الأرشفة
            archived_text = f"📁 <b>مؤرشف من الرسالة #{original_message_id}</b>\n\n{text}"
            
            data = {
                "chat_id": self.archive_channel_id,
                "text": archived_text,
                "parse_mode": "HTML"
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("ok"):
                        logger.info(f"✅ تم أرشفة الرسالة {original_message_id}")
                        return True
                    else:
                        logger.error(f"❌ خطأ في الأرشفة: {result.get('description')}")
                        
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال الأرشيف: {e}")
            
        return False
    
    def format_property_notification(self, property_data: Dict[str, Any], 
                                   classification: str, 
                                   similar_property_link: str = None) -> str:
        """تنسيق إشعار العقار"""
        
        icon_map = {
            "عقار جديد": "🆕",
            "عقار مكرر": "🔄", 
            "عقار متعدد": "📊",
            "عقار ناجح": "✅",
            "عقار فاشل": "❌"
        }
        
        icon = icon_map.get(classification, "🏠")
        
        message = f"{icon} <b>{classification}</b>\n\n"
        message += f"📋 <b>البيان:</b> {property_data.get('البيان', 'غير محدد')}\n"
        message += f"🏘️ <b>المنطقة:</b> {property_data.get('المنطقة', 'غير محدد')}\n"
        message += f"🏠 <b>نوع الوحدة:</b> {property_data.get('نوع الوحدة', 'غير محدد')}\n"
        message += f"📐 <b>المساحة:</b> {property_data.get('المساحة', 'غير محدد')} متر\n"
        message += f"💰 <b>السعر:</b> {property_data.get('السعر', 'غير محدد')} جنيه\n"
        message += f"👤 <b>المالك:</b> {property_data.get('اسم المالك', 'غير محدد')}\n"
        message += f"📱 <b>رقم المالك:</b> {property_data.get('رقم المالك', 'غير محدد')}\n"
        
        if similar_property_link and classification == "عقار مكرر":
            message += f"\n🔗 <b>العقار المشابه:</b> {similar_property_link}"
        
        # إضافة معلومات إضافية للإشعارات
        message += f"\n\n⏰ <b>وقت المعالجة:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        if property_data.get("notion_property_id"):
            notion_link = f"https://www.notion.so/{property_data['notion_property_id'].replace('-', '')}"
            message += f"\n🔗 <b>رابط Notion:</b> {notion_link}"
            
        return message
    
    def format_success_message(self, property_data: Dict[str, Any]) -> str:
        """تنسيق رسالة العقار الناجح وفقاً للدليل الجديد"""
        
        formatted_message = f"{self.config.SUCCESS_TAG}\n\n"
        
        # إضافة البيان المدمج بالتنسيق الجديد (كل حقل في سطر منفصل مع أقواس مربعة)
        statement = property_data.get('البيان', '')
        if statement:
            formatted_message += statement
        else:
            # إنشاء البيان يدوياً إذا لم يكن موجوداً
            fields = [
                'المنطقة', 'كود الوحدة', 'نوع الوحدة', 'حالة الوحدة', 'المساحة', 
                'الدور', 'السعر', 'المميزات', 'العنوان', 'اسم الموظف',
                'اسم المالك', 'رقم المالك', 'اتاحة العقار', 'حالة الصور', 'تفاصيل كاملة'
            ]
            
            for field in fields:
                value = property_data.get(field, 'غير محدد')
                formatted_message += f"[{field}: {value}]\n"
        
        return formatted_message
    
    def format_failed_message(self, property_data: Dict[str, Any]) -> str:
        """تنسيق رسالة العقار الفاشل"""
        
        formatted_message = f"{self.config.FAILED_TAG}\n\n"
        
        # إضافة البيان المتاح
        if property_data.get('البيان'):
            statement_lines = property_data.get('البيان', '').split(' | ')
            for line in statement_lines:
                if line.strip():
                    formatted_message += f"[{line}]\n"
        else:
            # إضافة الحقول المتاحة
            fields = [
                'المنطقة', 'نوع الوحدة', 'حالة الوحدة', 'المساحة', 
                'الدور', 'السعر', 'اسم الموظف', 'حالة الصور'
            ]
            
            for field in fields:
                value = property_data.get(field, 'غير محدد')
                formatted_message += f"[{field}: {value}]\n"
        
        # إضافة التفاصيل الكاملة
        formatted_message += f"\n[تفاصيل كاملة: {property_data.get('تفاصيل كاملة', property_data.get('raw_text', 'غير محدد'))}]"
        
        return formatted_message
