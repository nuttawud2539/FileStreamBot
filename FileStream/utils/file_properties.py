from __future__ import annotations
import logging
from datetime import datetime
from pyrogram import Client
from typing import Any, Optional

from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import Message
from pyrogram.file_id import FileId
from FileStream.bot import FileStream
from FileStream.utils.database import Database
from FileStream.config import Telegram, Server

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)


async def get_file_ids(client: Client | bool, db_id: str, multi_clients, message) -> Optional[FileId]:
    logging.debug("Starting of get_file_ids [Bypass Mode]")
    
    # 🔒 ปลดล็อกร่างทอง: ควักเอา media จาก message ที่มึงส่งเข้ามาตรง ๆ เลยสัส ไม่ต้องง้อ db.get_file
    media = get_media_from_message(message) if isinstance(message, Message) else None
    
    if not media:
        # ถ้าระบบเรียกมาจาก API/ท่ออื่นที่ไม่มี message ส่งมา ค่อยดึงค่าจากแรมแก้ขัด
        file_info = await db.get_file(db_id)
        actual_file_id = file_info.get('file_id', 'BQACAgUAAx0CXy1234567890abcdefghijklmnopqrstuvwxyz')
        file_size = file_info.get('file_size', 0)
        mime_type = file_info.get('mime_type', 'video/mp4')
        file_name = file_info.get('file_name', 'video.mkv')
        unique_id = file_info.get('file_unique_id', 'dummy_unique')
    else:
        actual_file_id = getattr(media, "file_id", "")
        file_size = getattr(media, "file_size", 0)
        mime_type = getattr(media, "mime_type", "video/mp4")
        file_name = get_name(message)
        unique_id = getattr(media, "file_unique_id", "dummy_unique")

    # 🚀 สั่งบอทส่งไฟล์เข้าคลังเก็บ (Bin Channel) ของมึงเพื่อรักษาระบบ Log ตามปกติ
    try:
        await send_file(FileStream, db_id, actual_file_id, message)
    except Exception as e:
        logging.error(f"Error while sending file to log channel: {e}")

    # 🛠️ ประกอบร่าง FileId ถอดรหัสส่งกลับไปให้ท่อเว็บสตรีมเอาไปปล่อยลิงก์ตรง
    file_id = FileId.decode(actual_file_id)
    setattr(file_id, "file_size", file_size)
    setattr(file_id, "mime_type", mime_type)
    setattr(file_id, "file_name", file_name)
    setattr(file_id, "unique_id", unique_id)
    
    logging.debug("Ending of get_file_ids [Bypass Mode]")
    return file_id


def get_media_from_message(message: "Message") -> Any:
    media_types = (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
    )
    for attr in media_types:
        media = getattr(message, attr, None)
        if media:
            return media


def get_media_file_size(m):
    media = get_media_from_message(m)
    return getattr(media, "file_size", "None")


def get_name(media_msg: Message | FileId) -> str:
    file_name = ""
    if isinstance(media_msg, Message):
        media = get_media_from_message(media_msg)
        file_name = getattr(media, "file_name", "")

    elif isinstance(media_msg, FileId):
        file_name = getattr(media_msg, "file_name", "")

    if not file_name:
        if isinstance(media_msg, Message) and media_msg.media:
            media_type = media_msg.media.value
        elif hasattr(media_msg, "file_type") and media_msg.file_type:
            media_type = media_msg.file_type.name.lower()
        else:
            media_type = "file"

        formats = {
            "photo": "jpg", "audio": "mp3", "voice": "ogg",
            "video": "mp4", "animation": "mp4", "video_note": "mp4",
            "sticker": "webp"
        }

        ext = formats.get(media_type)
        ext = "." + ext if ext else ""

        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{media_type}-{date}{ext}"

    return file_name


def get_file_info(message):
    media = get_media_from_message(message)
    if message.chat.type == ChatType.PRIVATE:
        user_idx = message.from_user.id
    else:
        user_idx = message.chat.id
    return {
        "user_id": user_idx,
        "file_id": getattr(media, "file_id", ""),
        "file_unique_id": getattr(media, "file_unique_id", ""),
        "file_name": get_name(message),
        "file_size": getattr(media, "file_size", 0),
        "mime_type": getattr(media, "mime_type", "None/unknown")
    }


async def update_file_id(msg_id, multi_clients):
    file_ids = {}
    for client_id, client in multi_clients.items():
        log_msg = await client.get_messages(Telegram.FLOG_CHANNEL, msg_id)
        media = get_media_from_message(log_msg)
        file_ids[str(client.id)] = getattr(media, "file_id", "")

    return file_ids


async def send_file(client: Client, db_id, file_id: str, message):
    if isinstance(message, Message):
        file_caption = getattr(message, 'caption', None) or get_name(message)
        user_id = message.from_user.id if message.from_user else 0
        chat_title = message.from_user.first_name if message.from_user else "Unknown"
    else:
        file_caption = f"File: {db_id}"
        user_id = 0
        chat_title = "API/System"

    log_msg = await client.send_cached_media(
        chat_id=Telegram.FLOG_CHANNEL, 
        file_id=file_id,
        caption=f'**{file_caption}**'
    )

    if isinstance(message, Message) and message.chat:
        if message.chat.type == ChatType.PRIVATE:
            await log_msg.reply_text(
                text=f"**RᴇQᴜᴇꜱᴛᴇ\n**U\n**F",
                disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN, quote=True)
        else:
            await log_msg.reply_text(
                text=f"**R\n**C\n**F",
                disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN, quote=True)
    else:
        await log_msg.reply_text(
            text=f"**R\n**F",
            disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN, quote=True)

    return log_msg
