# admin/project_leadership/handlers/system.py
import json
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType, Keyboard, Text, KeyboardButtonColor
from db.database import db
from admin.system_management import (
    create_backup, get_recent_logs, get_chat_config,
    format_chat_config, set_chat_id, get_scheduler_status, reload_config,
)
from admin.project_leadership.keyboards.system_keyboards import get_system_menu_keyboard

logger = logging.getLogger(__name__)
bp = Blueprint("founder_system")


async def _edit_event(event: MessageEvent, text: str, keyboard: str = ""):
    try:
        await event.ctx_api.messages.edit(
            peer_id=event.peer_id,
            conversation_message_id=event.conversation_message_id,
            message=text, keyboard=keyboard
        )
    except Exception:
        try:
            await event.ctx_api.messages.send(
                peer_id=event.peer_id, message=text, keyboard=keyboard, random_id=0
            )
        except Exception as e:
            logger.error(f"system edit: {e}")


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_system_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "system_menu":
        await event.show_snackbar(" ")
        await _edit_event(event, "💻 Система", get_system_menu_keyboard())

    elif cmd == "system_reload_cache":
        from utils.permissions import reload_admin_cache
        await reload_admin_cache()
        await event.show_snackbar("Кеш ролей сброшен")

    elif cmd == "system_backup":
        success, msg = await create_backup()
        await event.show_snackbar(msg[:80])

    elif cmd == "system_logs":
        await event.show_snackbar(" ")
        logs = await get_recent_logs(50)
        await _edit_event(event, logs, "")

    elif cmd == "system_chats":
        await event.show_snackbar(" ")
        chats = await get_chat_config()
        text = await format_chat_config(chats)
        kb = Keyboard(inline=True)
        for c in chats:
            kb.add(Text(f"Режим {c['chat_mode']}", payload={"cmd": "system_chat_set", "mode": c["chat_mode"]}), color=KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text("🔙 Назад", payload={"cmd": "system_menu"}), color=KeyboardButtonColor.SECONDARY)
        await _edit_event(event, text, kb.get_json())

    elif cmd == "system_chat_set":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'system_chat_id_input', ?)",
            event.user_id, json.dumps({"mode": int(payload.get("mode"))})
        )
        await _edit_event(event, "Введите новый ID чата:", "")

    elif cmd == "system_scheduler":
        await event.show_snackbar(" ")
        status = await get_scheduler_status()
        kb = Keyboard(inline=True)
        kb.add(Text("🔄 Обновить", payload={"cmd": "system_scheduler"}), color=KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text("🔙 Назад", payload={"cmd": "system_menu"}), color=KeyboardButtonColor.SECONDARY)
        await _edit_event(event, status, kb.get_json())

    elif cmd == "system_reload_config":
        success, msg = await reload_config()
        await event.show_snackbar(msg[:80])


@bp.on.message()
async def handle_system_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state, data FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row:
        return
    if state_row["state"] == "system_chat_id_input":
        text = message.text.strip()
        if not text.isdigit():
            await message.answer("ID чата должен быть числом.")
            return
        mode = json.loads(state_row["data"])["mode"]
        success, msg = await set_chat_id(mode, int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)
    else:
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)