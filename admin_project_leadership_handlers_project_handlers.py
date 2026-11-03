# admin/project_leadership/handlers/project.py
import json
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType, Keyboard, Text, KeyboardButtonColor
from db.database import db
from admin.project_management import (
    list_project_settings, get_project_settings_keyboard, get_setting_category_keyboard,
    edit_setting_value, list_promocodes, create_promocode, delete_promocode,
)

logger = logging.getLogger(__name__)
bp = Blueprint("founder_project")


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
            logger.error(f"project edit: {e}")


async def show_project_menu_event(event: MessageEvent):
    from admin.project_leadership.keyboards.leadership_menu_keyboards import get_project_menu_keyboard
    await _edit_event(event, "⚙️ Проект", get_project_menu_keyboard())


async def show_project_settings_event(event: MessageEvent):
    text = await list_project_settings()
    kb = await get_project_settings_keyboard()
    await _edit_event(event, text, kb)


async def show_promocodes_event(event: MessageEvent):
    promos = await list_promocodes()
    lines = ["🎁 Промокоды:"]
    for p in promos:
        lines.append(f"  • {p['code']} (осталось: {p['uses_left']})")
    text = "\n".join(lines) if promos else "Промокодов нет."
    kb = Keyboard(inline=True)
    kb.add(Text("Создать промокод", payload={"cmd": "project_promocode_create"}), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("Удалить промокод", payload={"cmd": "project_promocode_delete"}), color=KeyboardButtonColor.NEGATIVE)
    kb.row()
    kb.add(Text("🔙 Назад", payload={"cmd": "founder_project"}), color=KeyboardButtonColor.SECONDARY)
    await _edit_event(event, text, kb.get_json())


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_project_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "founder_project":
        await event.show_snackbar(" ")
        await show_project_menu_event(event)

    elif cmd == "project_settings":
        await event.show_snackbar(" ")
        await show_project_settings_event(event)

    elif cmd == "project_setting_category":
        await event.show_snackbar(" ")
        category = payload.get("category")
        kb = await get_setting_category_keyboard(category)
        await _edit_event(event, f"Настройки категории {category}:", kb)

    elif cmd == "project_setting_edit":
        await event.show_snackbar(" ")
        key = payload.get("key")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'project_setting_value_input', ?)",
            event.user_id, json.dumps({"key": key})
        )
        await _edit_event(event, f"Введите новое значение для {key}:", "")

    elif cmd == "project_promocodes":
        await event.show_snackbar(" ")
        await show_promocodes_event(event)

    elif cmd == "project_promocode_create":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'promocode_code_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите код промокода:", "")

    elif cmd == "project_promocode_delete":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'promocode_delete_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите код промокода для удаления:", "")

    elif cmd == "project_statistics":
        await event.show_snackbar(" ")
        users_count = await db.fetchone("SELECT COUNT(*) as cnt FROM users")
        businesses_count = await db.fetchone("SELECT COUNT(*) as cnt FROM businesses WHERE owner_id IS NOT NULL")
        text = f"📊 Статистика проекта:\nИгроков: {users_count['cnt']}\nБизнесов владеют: {businesses_count['cnt']}"
        await _edit_event(event, text, "")


@bp.on.message()
async def handle_project_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state, data FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row:
        return
    state = state_row["state"]
    text = message.text.strip()

    if state == "project_setting_value_input":
        key = json.loads(state_row["data"])["key"]
        success, msg = await edit_setting_value(message.from_id, key, text)
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "promocode_code_input":
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'promocode_reward_type_input', ?)",
            message.from_id, json.dumps({"code": text})
        )
        await message.answer("Введите тип награды (money/item/business):")

    elif state == "promocode_reward_type_input":
        data = json.loads(state_row["data"])
        data["reward_type"] = text
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'promocode_reward_id_input', ?)",
            message.from_id, json.dumps(data)
        )
        await message.answer("Введите ID награды (для предмета/бизнеса), для денег введите 0:")

    elif state == "promocode_reward_id_input":
        data = json.loads(state_row["data"])
        data["reward_id"] = text
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'promocode_amount_input', ?)",
            message.from_id, json.dumps(data)
        )
        await message.answer("Введите сумму/количество награды:")

    elif state == "promocode_amount_input":
        if not text.isdigit():
            await message.answer("Сумма должна быть числом.")
            return
        data = json.loads(state_row["data"])
        data["reward_amount"] = int(text)
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'promocode_uses_input', ?)",
            message.from_id, json.dumps(data)
        )
        await message.answer("Введите количество использований:")

    elif state == "promocode_uses_input":
        if not text.isdigit():
            await message.answer("Количество должно быть числом.")
            return
        data = json.loads(state_row["data"])
        success, msg = await create_promocode(
            message.from_id, data["code"], data["reward_type"],
            data.get("reward_id", ""), data["reward_amount"], int(text)
        )
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "promocode_delete_input":
        success, msg = await delete_promocode(message.from_id, text)
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    else:
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)