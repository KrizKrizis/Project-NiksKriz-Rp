# admin/project_leadership/handlers/team.py
import json
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType, Keyboard, Text, KeyboardButtonColor
from db.database import db
from utils.permissions import get_admin_info
from admin.team_management import (
    get_team_list, format_team_list, assign_role, remove_role, promote_user,
    give_warning, award_admin_coins, get_team_statistics,
)

logger = logging.getLogger(__name__)
bp = Blueprint("founder_team")


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
            logger.error(f"team edit: {e}")


async def show_team_menu_event(event: MessageEvent):
    team = await get_team_list()
    text = await format_team_list(team)
    kb = Keyboard(inline=True)
    kb.add(Text("Назначить роль", payload={"cmd": "team_assign_role"}), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("Снять роль", payload={"cmd": "team_remove_role"}), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("Повысить/Понизить", payload={"cmd": "team_promote"}), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("Выдать выговор", payload={"cmd": "team_warning"}), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text("📊 Статистика", payload={"cmd": "team_statistics"}), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("🔙 Назад", payload={"cmd": "founder_main"}), color=KeyboardButtonColor.SECONDARY)
    await _edit_event(event, text, kb.get_json())


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_team_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "team_management":
        await event.show_snackbar(" ")
        await show_team_menu_event(event)

    elif cmd == "team_assign_role":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'team_assign_id_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID игрока, которому хотите назначить роль:", "")

    elif cmd == "team_remove_role":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'team_remove_id_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID игрока, у которого хотите снять роль:", "")

    elif cmd == "team_promote":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'team_promote_id_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID игрока для повышения/понижения:", "")

    elif cmd == "team_warning":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'team_warning_id_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID игрока для выдачи выговора:", "")

    elif cmd == "team_rewards":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'team_reward_id_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID игрока для начисления админ-койнов:", "")

    elif cmd == "team_statistics":
        await event.show_snackbar(" ")
        stats = await get_team_statistics()
        await _edit_event(event, stats, "")

    elif cmd == "team_assign_confirm":
        target_id = int(payload["target_id"])
        category = int(payload["category"])
        position = payload["position"]
        success, msg = await assign_role(event.user_id, target_id, category, position)
        await event.show_snackbar(msg)
        await show_team_menu_event(event)

    elif cmd == "team_promote_confirm":
        target_id = int(payload["target_id"])
        category = int(payload["category"])
        position = payload["position"]
        success, msg = await promote_user(event.user_id, target_id, category, position)
        await event.show_snackbar(msg)
        await show_team_menu_event(event)


@bp.on.message()
async def handle_team_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state, data FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row:
        return
    state = state_row["state"]
    text = message.text.strip()

    # Сначала — состояния, которые НЕ являются вводом ID
    if state == "team_warning_reason_input":
        target_id = json.loads(state_row["data"])["target_id"]
        success, msg = await give_warning(message.from_id, target_id, text)
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "team_reward_amount_input":
        target_id = json.loads(state_row["data"])["target_id"]
        if not text.isdigit():
            await message.answer("Сумма должна быть числом.")
            return
        success, msg = await award_admin_coins(message.from_id, target_id, int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state in ("team_assign_id_input", "team_remove_id_input", "team_promote_id_input", "team_warning_id_input", "team_reward_id_input"):
        if not text.isdigit():
            await message.answer("ID должен быть числом.")
            return
        user = await db.fetchone("SELECT vk_id FROM users WHERE game_id = ?", int(text))
        if not user:
            await message.answer("Игрок не найден.")
            await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)
            return
        target_vk_id = user["vk_id"]

        if state == "team_assign_id_input":
            kb = Keyboard(inline=True)
            roles = [
                ("Хелпер", 1, "1.1"), ("Администратор", 2, "2.1"),
                ("Старший администратор", 2, "2.2"), ("ЗГА", 2, "2.3"),
                ("ГА", 2, "2.4"), ("Куратор", 3, "3.1"),
                ("Тестировщик", 3, "3.2"), ("Зам. основателя", 3, "3.3"),
            ]
            for name, cat, pos in roles:
                kb.add(Text(name, payload={"cmd": "team_assign_confirm", "target_id": target_vk_id, "category": cat, "position": pos}), color=KeyboardButtonColor.PRIMARY)
            kb.row()
            kb.add(Text("🔙 Отмена", payload={"cmd": "team_management"}), color=KeyboardButtonColor.SECONDARY)
            await message.answer("Выберите роль для назначения:", keyboard=kb.get_json())
            await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

        elif state == "team_remove_id_input":
            success, msg = await remove_role(message.from_id, target_vk_id)
            await message.answer(msg)
            await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

        elif state == "team_promote_id_input":
            kb = Keyboard(inline=True)
            roles = [
                ("Хелпер", 1, "1.1"), ("Администратор", 2, "2.1"),
                ("Старший администратор", 2, "2.2"), ("ЗГА", 2, "2.3"),
                ("ГА", 2, "2.4"), ("Куратор", 3, "3.1"),
                ("Тестировщик", 3, "3.2"), ("Зам. основателя", 3, "3.3"),
            ]
            for name, cat, pos in roles:
                kb.add(Text(name, payload={"cmd": "team_promote_confirm", "target_id": target_vk_id, "category": cat, "position": pos}), color=KeyboardButtonColor.PRIMARY)
            kb.row()
            kb.add(Text("🔙 Отмена", payload={"cmd": "team_management"}), color=KeyboardButtonColor.SECONDARY)
            await message.answer("Выберите новую роль:", keyboard=kb.get_json())
            await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

        elif state == "team_warning_id_input":
            await db.execute(
                "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'team_warning_reason_input', ?)",
                message.from_id, json.dumps({"target_id": target_vk_id})
            )
            await message.answer("Введите причину выговора:")

        elif state == "team_reward_id_input":
            await db.execute(
                "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'team_reward_amount_input', ?)",
                message.from_id, json.dumps({"target_id": target_vk_id})
            )
            await message.answer("Введите сумму админ-койнов:")