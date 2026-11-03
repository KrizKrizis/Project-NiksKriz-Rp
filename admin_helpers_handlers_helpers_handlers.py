# admin/helpers/handlers/helpers.py
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType, Keyboard, Text, KeyboardButtonColor
from db.database import db
from admin.player_management import (
    format_player_list_page, get_total_pages, get_player_profile,
)
from admin.helpers.keyboards.helpers_menu_keyboards import get_helpers_main_keyboard

logger = logging.getLogger(__name__)
bp = Blueprint("helpers")


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
            logger.error(f"helpers edit: {e}")


async def show_helpers_menu(message: Message, edit: bool = False):
    if edit:
        try:
            await message.edit("🛠 Меню хелпера", keyboard=get_helpers_main_keyboard())
        except Exception:
            await message.answer("🛠 Меню хелпера", keyboard=get_helpers_main_keyboard())
    else:
        await message.answer("🛠 Меню хелпера", keyboard=get_helpers_main_keyboard())


async def _show_helpers_players(event: MessageEvent, page: int):
    text, _ = await format_player_list_page(page)
    total_pages = await get_total_pages()
    kb = Keyboard(inline=True)
    left_color = KeyboardButtonColor.SECONDARY if page <= 1 else KeyboardButtonColor.PRIMARY
    right_color = KeyboardButtonColor.SECONDARY if page >= total_pages else KeyboardButtonColor.POSITIVE
    kb.add(Text("⬅️", payload={"cmd": "helpers_players_page", "page": page - 1 if page > 1 else 1}), color=left_color)
    kb.add(Text("📊 Статистика", payload={"cmd": "helpers_player_stats"}), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("➡️", payload={"cmd": "helpers_players_page", "page": page + 1 if page < total_pages else page}), color=right_color)
    kb.row()
    kb.add(Text("🔙 Назад", payload={"cmd": "helpers_main"}), color=KeyboardButtonColor.SECONDARY)
    await _edit_event(event, text, kb.get_json())


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_helpers_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd in ("helpers_main", "admin_main_menu"):
        await event.show_snackbar(" ")
        await _edit_event(event, "🛠 Меню хелпера", get_helpers_main_keyboard())

    elif cmd == "helpers_players":
        await event.show_snackbar(" ")
        await _show_helpers_players(event, 1)

    elif cmd == "helpers_players_page":
        await event.show_snackbar(" ")
        await _show_helpers_players(event, int(payload.get("page", 1)))

    elif cmd == "helpers_player_stats":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'helpers_stats_id_input', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите игровой ID игрока для просмотра статистики:")

    elif cmd == "helpers_requests":
        await event.show_snackbar(" ")
        await _edit_event(event, "📬 Обращений пока нет.")

    elif cmd == "helpers_stats":
        await event.show_snackbar(" ")
        await _edit_event(event, "📊 Ваша статистика за сегодня: 0 обращений.")


@bp.on.message()
async def handle_helpers_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row:
        return
    if state_row["state"] == "helpers_stats_id_input":
        text = message.text.strip()
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
    else:
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)