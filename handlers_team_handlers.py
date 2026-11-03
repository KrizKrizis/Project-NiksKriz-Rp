# admin/administration/handlers/team.py
import json
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType, Keyboard, Text, KeyboardButtonColor
from db.database import db
from utils.permissions import has_permission, get_admin_info
from admin.team_management import (
    get_team_list, format_team_list, assign_role, remove_role, promote_user,
)
from admin.administration.keyboards.team_keyboards import (
    get_team_management_keyboard, get_role_selection_keyboard,
)

logger = logging.getLogger(__name__)
bp = Blueprint("admin_team")


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
            logger.error(f"admin team edit: {e}")


async def _show_team_menu(event: MessageEvent):
    if not await has_permission(event.user_id, "team.view"):
        await event.show_snackbar(" ")
        return
    team = await get_team_list()
    text = await format_team_list(team)
    info = await get_admin_info(event.user_id)
    permissions = info.get("permissions", {}) if info else {}
    kb = get_team_management_keyboard(permissions)
    await _edit_event(event, text, kb)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_admin_team_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "admin_team":
        await event.show_snackbar(" ")
        await _show_team_menu(event)

    elif cmd == "admin_team_assign":
        if not await has_permission(event.user_id, "team.manage"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_team_assign_id', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID для назначения роли:")

    elif cmd == "admin_team_remove":
        if not await has_permission(event.user_id, "team.manage"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_team_remove_id', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID для снятия роли:")

    elif cmd == "admin_team_promote":
        if not await has_permission(event.user_id, "team.manage"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_team_promote_id', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID для повышения/понижения:")

    elif cmd == "admin_team_assign_confirm":
        target_id = int(payload["target_id"])
        category = int(payload["category"])
        position = payload["position"]
        success, msg = await assign_role(event.user_id, target_id, category, position)
        await event.show_snackbar(msg[:80])
        await _show_team_menu(event)

    elif cmd == "admin_team_promote_confirm":
        target_id = int(payload["target_id"])
        category = int(payload["category"])
        position = payload["position"]
        success, msg = await promote_user(event.user_id, target_id, category, position)
        await event.show_snackbar(msg[:80])
        await _show_team_menu(event)


@bp.on.message()
async def handle_admin_team_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state, data FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row:
        return
    state = state_row["state"]
    text = message.text.strip()

    if state in ("admin_team_assign_id", "admin_team_remove_id", "admin_team_promote_id"):
        if not text.isdigit():
            await message.answer("ID должен быть числом.")
            return
        user = await db.fetchone("SELECT vk_id FROM users WHERE game_id = ?", int(text))
        if not user:
            await message.answer("Игрок не найден.")
            await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)
            return
        target_vk_id = user["vk_id"]

        if state == "admin_team_assign_id":
            await message.answer("Выберите роль:", keyboard=get_role_selection_keyboard(target_vk_id, "assign"))
            await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)
        elif state == "admin_team_remove_id":
            success, msg = await remove_role(message.from_id, target_vk_id)
            await message.answer(msg)
            await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)
        elif state == "admin_team_promote_id":
            await message.answer("Выберите новую роль:", keyboard=get_role_selection_keyboard(target_vk_id, "promote"))
            await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)
    else:
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)