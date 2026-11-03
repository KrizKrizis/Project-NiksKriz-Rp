# admin/project_leadership/handlers/players.py
import json
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType, Keyboard, Text, KeyboardButtonColor
from db.database import db
from utils.permissions import get_admin_info
from admin.player_management import (
    format_player_list_page, get_player_profile, search_player, format_search_results,
    block_player, unblock_player, give_item, take_item, give_money, take_money,
)

logger = logging.getLogger(__name__)
bp = Blueprint("founder_players")


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
            logger.error(f"players edit: {e}")


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_players_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "players_page":
        await event.show_snackbar(" ")
        page = int(payload.get("page", 1))
        text, kb = await format_player_list_page(page)
        await _edit_event(event, text, kb or "")

    elif cmd == "player_stats_request":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'player_stats_id_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID игрока для просмотра статистики:", "")

    elif cmd == "player_logs_request":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'player_logs_id_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID игрока для просмотра логов:", "")

    elif cmd == "player_search_request":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'player_search_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите имя, фамилию, @username или ID игрока:", "")

    elif cmd == "player_manage_request":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'player_manage_id_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID игрока для управления:", "")

    elif cmd == "manage_freeze":
        target_id = int(payload.get("target_id"))
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'manage_freeze_duration', ?)",
            event.user_id, json.dumps({"target_id": target_id})
        )
        await _edit_event(event, "Введите длительность заморозки в днях (0 = навсегда):", "")

    elif cmd == "manage_target_block":
        target_id = int(payload.get("target_id"))
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'manage_target_duration', ?)",
            event.user_id, json.dumps({"target_id": target_id})
        )
        await _edit_event(event, "Введите длительность точечной блокировки в днях (0 = навсегда):", "")

    elif cmd == "manage_full_ban":
        target_id = int(payload.get("target_id"))
        success, msg = await block_player(event.user_id, target_id, "full", 0)
        await event.show_snackbar(msg)
        text, kb = await format_player_list_page(1)
        await _edit_event(event, text, kb or "")

    elif cmd == "manage_unblock":
        target_id = int(payload.get("target_id"))
        success, msg = await unblock_player(event.user_id, target_id)
        await event.show_snackbar(msg)
        text, kb = await format_player_list_page(1)
        await _edit_event(event, text, kb or "")

    elif cmd == "manage_give_money":
        target_id = int(payload.get("target_id"))
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'manage_money_amount_give', ?)",
            event.user_id, json.dumps({"target_id": target_id})
        )
        await _edit_event(event, "Введите сумму для выдачи:", "")

    elif cmd == "manage_take_money":
        target_id = int(payload.get("target_id"))
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'manage_money_amount_take', ?)",
            event.user_id, json.dumps({"target_id": target_id})
        )
        await _edit_event(event, "Введите сумму для изъятия:", "")

    elif cmd == "manage_give_item":
        target_id = int(payload.get("target_id"))
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'manage_item_id_give', ?)",
            event.user_id, json.dumps({"target_id": target_id})
        )
        await _edit_event(event, "Введите ID предмета для выдачи:", "")

    elif cmd == "manage_take_item":
        target_id = int(payload.get("target_id"))
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'manage_item_id_take', ?)",
            event.user_id, json.dumps({"target_id": target_id})
        )
        await _edit_event(event, "Введите ID предмета для изъятия:", "")


@bp.on.message()
async def handle_player_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state, data FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row:
        return
    state = state_row["state"]
    text = message.text.strip()
    data = json.loads(state_row["data"])
    target_id = data.get("target_id")

    if state == "player_stats_id_input":
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

    elif state == "player_logs_id_input":
        if not text.isdigit():
            await message.answer("ID должен быть числом.")
            return
        user = await db.fetchone("SELECT vk_id FROM users WHERE game_id = ?", int(text))
        if not user:
            await message.answer("Игрок не найден.")
            await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)
            return
        logs = await db.fetchall(
            "SELECT * FROM admin_log WHERE admin_id = ? ORDER BY id DESC LIMIT 20",
            user["vk_id"]
        )
        if not logs:
            await message.answer("Логов нет.")
        else:
            lines = ["📋 Логи игрока:"]
            for l in logs:
                lines.append(f"  • {l['action']}: {l['details']} ({l['timestamp']})")
            await message.answer("\n".join(lines))
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "player_search_input":
        results = await search_player(text)
        formatted = await format_search_results(results)
        await message.answer(formatted)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "player_manage_id_input":
        if not text.isdigit():
            await message.answer("ID должен быть числом.")
            return
        user = await db.fetchone("SELECT vk_id FROM users WHERE game_id = ?", int(text))
        if not user:
            await message.answer("Игрок не найден.")
            await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)
            return
        kb = Keyboard(inline=True)
        kb.add(Text("Заморозить", payload={"cmd": "manage_freeze", "target_id": user["vk_id"]}), color=KeyboardButtonColor.PRIMARY)
        kb.add(Text("Точечная блокировка", payload={"cmd": "manage_target_block", "target_id": user["vk_id"]}), color=KeyboardButtonColor.PRIMARY)
        kb.add(Text("Полный бан", payload={"cmd": "manage_full_ban", "target_id": user["vk_id"]}), color=KeyboardButtonColor.NEGATIVE)
        kb.add(Text("Разблокировать", payload={"cmd": "manage_unblock", "target_id": user["vk_id"]}), color=KeyboardButtonColor.PRIMARY)
        kb.add(Text("Выдать деньги", payload={"cmd": "manage_give_money", "target_id": user["vk_id"]}), color=KeyboardButtonColor.PRIMARY)
        kb.add(Text("Изъять деньги", payload={"cmd": "manage_take_money", "target_id": user["vk_id"]}), color=KeyboardButtonColor.PRIMARY)
        kb.add(Text("Выдать предмет", payload={"cmd": "manage_give_item", "target_id": user["vk_id"]}), color=KeyboardButtonColor.PRIMARY)
        kb.add(Text("Изъять предмет", payload={"cmd": "manage_take_item", "target_id": user["vk_id"]}), color=KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text("🔙 Назад", payload={"cmd": "founder_players"}), color=KeyboardButtonColor.SECONDARY)
        await message.answer("Выберите действие:", keyboard=kb.get_json())
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "manage_freeze_duration":
        if not text.isdigit():
            await message.answer("Длительность должна быть числом.")
            return
        success, msg = await block_player(message.from_id, target_id, "freeze", int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "manage_target_duration":
        if not text.isdigit():
            await message.answer("Длительность должна быть числом.")
            return
        success, msg = await block_player(message.from_id, target_id, "target", int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "manage_money_amount_give":
        if not text.isdigit():
            await message.answer("Сумма должна быть числом.")
            return
        success, msg = await give_money(message.from_id, target_id, int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "manage_money_amount_take":
        if not text.isdigit():
            await message.answer("Сумма должна быть числом.")
            return
        success, msg = await take_money(message.from_id, target_id, int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "manage_item_id_give":
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'manage_item_qty_give', ?)",
            message.from_id, json.dumps({"target_id": target_id, "item_id": text})
        )
        await message.answer("Введите количество:")

    elif state == "manage_item_id_take":
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'manage_item_qty_take', ?)",
            message.from_id, json.dumps({"target_id": target_id, "item_id": text})
        )
        await message.answer("Введите количество:")

    elif state == "manage_item_qty_give":
        if not text.isdigit():
            await message.answer("Количество должно быть числом.")
            return
        success, msg = await give_item(message.from_id, target_id, data.get("item_id"), int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "manage_item_qty_take":
        if not text.isdigit():
            await message.answer("Количество должно быть числом.")
            return
        success, msg = await take_item(message.from_id, target_id, data.get("item_id"), int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    else:
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)