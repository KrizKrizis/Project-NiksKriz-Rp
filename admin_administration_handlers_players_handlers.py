# admin/administration/handlers/players.py
import json
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType, Keyboard, Text, KeyboardButtonColor
from db.database import db
from utils.permissions import get_admin_info, has_permission
from admin.player_management import (
    get_player_page, get_total_pages, get_player_profile, search_player, format_search_results,
    block_player, unblock_player, give_item, take_item, give_money, take_money,
)
from admin.administration.keyboards.players_keyboards import (
    get_admin_players_keyboard, get_admin_player_manage_keyboard,
)

logger = logging.getLogger(__name__)
bp = Blueprint("admin_players")


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
            logger.error(f"admin players edit: {e}")


async def _get_permissions(user_id: int) -> dict:
    info = await get_admin_info(user_id)
    return info.get("permissions", {}) if info else {}


async def _show_players_page_event(event: MessageEvent, page: int):
    permissions = await _get_permissions(event.user_id)
    if not permissions.get("players.view", False):
        await event.show_snackbar(" ")
        return
    players = await get_player_page(page)
    total_pages = await get_total_pages()
    lines = [f"Страница {page}"]
    for p in players:
        status = "🔴" if p["is_blocked"] else "🟢"
        lines.append(f"{status} {p['game_id']} | {p['first_name']} {p['last_name']} | LVL {p['level']}")
    kb = get_admin_players_keyboard(page, total_pages, permissions)
    await _edit_event(event, "\n".join(lines), kb)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_admin_players_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "admin_players":
        await event.show_snackbar(" ")
        await _show_players_page_event(event, 1)

    elif cmd == "admin_players_page":
        await event.show_snackbar(" ")
        await _show_players_page_event(event, int(payload.get("page", 1)))

    elif cmd == "admin_player_stats_request":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_stats_id_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID игрока:")

    elif cmd == "admin_player_logs_request":
        if not await has_permission(event.user_id, "players.view_extended"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_logs_id_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID игрока для просмотра логов:")

    elif cmd == "admin_player_search_request":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_search_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите имя, фамилию, @username или ID:")

    elif cmd == "admin_player_manage_request":
        await event.show_snackbar(" ")
        permissions = await _get_permissions(event.user_id)
        if not any(permissions.get(k, False) for k in [
            "players.freeze", "players.target_block", "players.full_ban",
            "players.give_money", "players.take_money", "players.give_item", "players.take_item"
        ]):
            return
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_manage_id_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID игрока для управления:")

    elif cmd == "admin_manage_freeze":
        target_id = int(payload.get("target_id"))
        if not await has_permission(event.user_id, "players.freeze"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_freeze_duration', ?)",
            event.user_id, json.dumps({"target_id": target_id})
        )
        await _edit_event(event, "Введите длительность заморозки в днях (0 = навсегда):")

    elif cmd == "admin_manage_target_block":
        target_id = int(payload.get("target_id"))
        if not await has_permission(event.user_id, "players.target_block"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_target_duration', ?)",
            event.user_id, json.dumps({"target_id": target_id})
        )
        await _edit_event(event, "Введите длительность точечной блокировки в днях (0 = навсегда):")

    elif cmd == "admin_manage_full_ban":
        target_id = int(payload.get("target_id"))
        if not await has_permission(event.user_id, "players.full_ban"):
            await event.show_snackbar(" ")
            return
        success, msg = await block_player(event.user_id, target_id, "full", 0)
        await event.show_snackbar(msg[:80])
        await _show_players_page_event(event, 1)

    elif cmd == "admin_manage_unblock":
        target_id = int(payload.get("target_id"))
        if not await has_permission(event.user_id, "players.unblock"):
            await event.show_snackbar(" ")
            return
        success, msg = await unblock_player(event.user_id, target_id)
        await event.show_snackbar(msg[:80])
        await _show_players_page_event(event, 1)

    elif cmd == "admin_manage_give_money":
        target_id = int(payload.get("target_id"))
        if not await has_permission(event.user_id, "players.give_money"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_give_money_amount', ?)",
            event.user_id, json.dumps({"target_id": target_id})
        )
        await _edit_event(event, "Введите сумму для выдачи:")

    elif cmd == "admin_manage_take_money":
        target_id = int(payload.get("target_id"))
        if not await has_permission(event.user_id, "players.take_money"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_take_money_amount', ?)",
            event.user_id, json.dumps({"target_id": target_id})
        )
        await _edit_event(event, "Введите сумму для изъятия:")

    elif cmd == "admin_manage_give_item":
        target_id = int(payload.get("target_id"))
        if not await has_permission(event.user_id, "players.give_item"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_give_item_id', ?)",
            event.user_id, json.dumps({"target_id": target_id})
        )
        await _edit_event(event, "Введите ID предмета:")

    elif cmd == "admin_manage_take_item":
        target_id = int(payload.get("target_id"))
        if not await has_permission(event.user_id, "players.take_item"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_take_item_id', ?)",
            event.user_id, json.dumps({"target_id": target_id})
        )
        await _edit_event(event, "Введите ID предмета:")


@bp.on.message()
async def handle_admin_players_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state, data FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row:
        return
    state = state_row["state"]
    text = message.text.strip()
    data = json.loads(state_row["data"])
    target_id = data.get("target_id")

    if state == "admin_stats_id_input":
        if not text.isdigit():
            await message.answer("ID должен быть числом.")
            return
        user = await db.fetchone("SELECT vk_id FROM users WHERE game_id = ?", int(text))
        if not user:
            await message.answer("Игрок не найден.")
            await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)
            return
        profile = await get_player_profile(user["vk_id"], message.from_id)
        await message.answer(profile)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "admin_logs_id_input":
        if not text.isdigit():
            await message.answer("ID должен быть числом.")
            return
        user = await db.fetchone("SELECT vk_id FROM users WHERE game_id = ?", int(text))
        if not user:
            await message.answer("Игрок не найден.")
            await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)
            return
        logs = await db.fetchall(
            "SELECT * FROM admin_log WHERE admin_id = ? ORDER BY id DESC LIMIT 20", user["vk_id"]
        )
        lines = ["📋 Логи игрока:"]
        for l in logs:
            lines.append(f"  • {l['action']}: {l['details']} ({l['timestamp']})")
        await message.answer("\n".join(lines) if logs else "Логов нет.")
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "admin_search_input":
        results = await search_player(text)
        await message.answer(await format_search_results(results))
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "admin_manage_id_input":
        if not text.isdigit():
            await message.answer("ID должен быть числом.")
            return
        user = await db.fetchone("SELECT vk_id FROM users WHERE game_id = ?", int(text))
        if not user:
            await message.answer("Игрок не найден.")
            await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)
            return
        permissions = await _get_permissions(message.from_id)
        kb = get_admin_player_manage_keyboard(user["vk_id"], permissions)
        await message.answer("Выберите действие:", keyboard=kb)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "admin_freeze_duration":
        if not text.isdigit():
            await message.answer("Длительность должна быть числом.")
            return
        success, msg = await block_player(message.from_id, target_id, "freeze", int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "admin_target_duration":
        if not text.isdigit():
            await message.answer("Длительность должна быть числом.")
            return
        success, msg = await block_player(message.from_id, target_id, "target", int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "admin_give_money_amount":
        if not text.isdigit():
            await message.answer("Сумма должна быть числом.")
            return
        success, msg = await give_money(message.from_id, target_id, int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "admin_take_money_amount":
        if not text.isdigit():
            await message.answer("Сумма должна быть числом.")
            return
        success, msg = await take_money(message.from_id, target_id, int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "admin_give_item_id":
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_give_item_qty', ?)",
            message.from_id, json.dumps({"target_id": target_id, "item_id": text})
        )
        await message.answer("Введите количество:")

    elif state == "admin_take_item_id":
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'admin_take_item_qty', ?)",
            message.from_id, json.dumps({"target_id": target_id, "item_id": text})
        )
        await message.answer("Введите количество:")

    elif state == "admin_give_item_qty":
        if not text.isdigit():
            await message.answer("Количество должно быть числом.")
            return
        success, msg = await give_item(message.from_id, target_id, data.get("item_id"), int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "admin_take_item_qty":
        if not text.isdigit():
            await message.answer("Количество должно быть числом.")
            return
        success, msg = await take_item(message.from_id, target_id, data.get("item_id"), int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    else:
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)