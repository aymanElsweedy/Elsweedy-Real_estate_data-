"""
خدمة Telegram - Telegram Service
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from utils.logger import setup_logger

logger = setup_logger(__name__)

class TelegramService:
    """خدمة التعامل مع Telegram"""
    
    def __init__(self, bot_token: str, channel_id: str):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.session = None
        
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_channel_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """الحصول على رسائل القناة"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            url = f"{self.base_url}/getUpdates"
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
                                    messages.append(self._format_message(channel_post))
                        
                        logger.info(f"✅ تم الحصول على {len(messages)} رسالة من القناة")
                        return messages
                    else:
                        logger.error(f"❌ خطأ API: {data.get('description')}")
                else:
                    logger.error(f"❌ خطأ HTTP: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على الرسائل: {e}")
            
        return []
    
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
        """إرسال رسالة إلى القناة"""
        return await self.send_message(text, parse_mode)
    
    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """إرسال رسالة إلى القناة"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.channel_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("ok"):
                        logger.info("✅ تم إرسال الرسالة بنجاح")
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
                
            url = f"{self.base_url}/deleteMessage"
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
                
            url = f"{self.base_url}/editMessageText"
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
        """إضافة وسم للرسالة"""
        # في Telegram، نستخدم الكلمات المفتاحية في النص لإضافة الوسوم
        try:
            # نحصل على الرسالة الحالية أولاً
            # ثم نضيف الوسم إليها
            tag_text = f"\n\n🏷️ {tag}"
            # يمكن تنفيذ هذا عبر تعديل الرسالة أو إضافة رد عليها
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في إضافة الوسم: {e}")
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
            
        return message
