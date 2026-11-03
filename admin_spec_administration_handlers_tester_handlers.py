# admin/spec_administration/handlers/tester.py
import json
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from utils.permissions import has_permission
from admin.test_panel_management import (
    give_test_balance, give_test_level, reset_test_data, get_test_logs,
)
from admin.spec_administration.keyboards.tester_keyboards import get_tester_menu_keyboard

logger = logging.getLogger(__name__)
bp = Blueprint("tester")


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
            logger.error(f"tester edit: {e}")


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_tester_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "spec_test_panel":
        if not await has_permission(event.user_id, "test_panel"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        await _edit_event(event, "🛠 Тест-панель", get_tester_menu_keyboard())

    elif cmd == "test_balance":
        if not await has_permission(event.user_id, "test_panel"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'test_balance_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите виртуальный баланс:")

    elif cmd == "test_level":
        if not await has_permission(event.user_id, "test_panel"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'test_level_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите виртуальный уровень:")

    elif cmd == "test_reset":
        if not await has_permission(event.user_id, "test_panel"):
            await event.show_snackbar(" ")
            return
        success, msg = await reset_test_data(event.user_id)
        await event.show_snackbar(msg[:80])
        await _edit_event(event, "🛠 Тест-панель", get_tester_menu_keyboard())

    elif cmd == "test_logs":
        if not await has_permission(event.user_id, "test_panel"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        logs = await get_test_logs(event.user_id)
        await _edit_event(event, logs)


@bp.on.message()
async def handle_tester_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row:
        return
    state = state_row["state"]
    text = message.text.strip()

    if state == "test_balance_input":
        if not text.isdigit():
            await message.answer("Введите число.")
            return
        success, msg = await give_test_balance(message.from_id, int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "test_level_input":
        if not text.isdigit():
            await message.answer("Введите число.")
            return
        success, msg = await give_test_level(message.from_id, int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    else:
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)