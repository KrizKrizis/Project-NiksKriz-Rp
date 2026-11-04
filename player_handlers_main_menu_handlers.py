# player/handlers/main_menu.py
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from utils.permissions import get_admin_info
from player.handlers.profile_handlers import format_profile
from player.keyboards.main_menu_keyboards import (
    get_terms_keyboard, get_choose_name_keyboard,
    get_tips_keyboard, get_main_menu_keyboard,
)
from config import FOUNDER_ID, TECH_ADMIN_ID, GROUP_ID

logger = logging.getLogger(__name__)
bp = Blueprint("player_main_menu")

TERMS_TEXT = (
    "📜 Пользовательское соглашение и Конфиденциальность\n\n"
    "Добро пожаловать в NiksKriz Corporation! Перед началом игры, пожалуйста, ознакомьтесь с базовыми правилами:\n\n"
    "1️⃣ **Статус проекта:** Это развлекательный текстовый бот (RPG). Все события, персонажи и экономика вымышлены.\n\n"
    "2️⃣ **Конфиденциальность:** Мы храним только ваш VK ID, имя и игровую статистику. Мы не запрашиваем пароли, номера телефонов.\n\n"
    "3️⃣ **Игровая валюта:** Внутриигровые ценности не имеют реальной стоимости.\n\n"
    "4️⃣ **Ответственность:** Администрация не несёт ответственности за сделки между игроками.\n\n"
    "5️⃣ **Честная игра:** Использование скриптов и багов приводит к блокировке.\n\n"
    "Нажимая «Согласиться», вы подтверждаете, что вам 14+ и вы принимаете условия."
)


async def edit_event_message(event: MessageEvent, text: str, keyboard: str):
    try:
        await event.ctx_api.messages.edit(
            peer_id=event.peer_id,
            conversation_message_id=event.conversation_message_id,
            message=text,
            keyboard=keyboard,
        )
    except Exception:
        try:
            await event.ctx_api.messages.send(
                peer_id=event.peer_id, message=text, keyboard=keyboard, random_id=0
            )
        except Exception as e:
            logger.error(f"edit_event_message: {e}")


async def get_or_create_user(user_id: int, first_name: str = "", last_name: str = ""):
    existing = await db.fetchone("SELECT * FROM users WHERE vk_id = ?", user_id)
    if existing:
        if user_id == FOUNDER_ID and existing["game_id"] != 0:
            await db.execute("UPDATE users SET game_id = 0 WHERE vk_id = ?", user_id)
            existing = await db.fetchone("SELECT * FROM users WHERE vk_id = ?", user_id)
        elif user_id == TECH_ADMIN_ID and existing["game_id"] != 1:
            await db.execute("UPDATE users SET game_id = 1 WHERE vk_id = ?", user_id)
            existing = await db.fetchone("SELECT * FROM users WHERE vk_id = ?", user_id)
        return existing

    if user_id == FOUNDER_ID:
        new_game_id = 0
    elif user_id == TECH_ADMIN_ID:
        new_game_id = 1
    else:
        max_row = await db.fetchone("SELECT MAX(game_id) as max_id FROM users WHERE game_id > 1")
        max_game_id = max_row["max_id"] if max_row and max_row["max_id"] is not None else 1
        new_game_id = max(max_game_id + 1, 2)

    if not first_name and not last_name:
        try:
            vk_users = await bp.api.users.get(user_id)
            if vk_users:
                first_name = vk_users[0].first_name or ""
                last_name = vk_users[0].last_name or ""
        except Exception as e:
            logger.warning(f"Не удалось получить имя из VK: {e}")

    await db.execute(
        "INSERT INTO users (vk_id, game_id, first_name, last_name, balance, exp, level, current_city, reputation, accepted_terms) "
        "VALUES (?, ?, ?, ?, 10000, 4, 1, 'Величие', 0, 0)",
        user_id, new_game_id, first_name, last_name
    )
    return await db.fetchone("SELECT * FROM users WHERE vk_id = ?", user_id)


async def show_main_menu_event(event: MessageEvent):
    user = await get_or_create_user(event.user_id)
    if not user or user["accepted_terms"] != 1:
        await edit_event_message(event, TERMS_TEXT, get_terms_keyboard())
        return
    info = await get_admin_info(event.user_id)
    cat = info["category"] if info else None
    text = await format_profile(user, info)
    await edit_event_message(event, text, get_main_menu_keyboard(cat))


async def show_main_menu(message: Message, edit: bool = False):
    user = await get_or_create_user(message.from_id)
    if not user or user["accepted_terms"] != 1:
        await message.answer(TERMS_TEXT, keyboard=get_terms_keyboard())
        return
    info = await get_admin_info(message.from_id)
    cat = info["category"] if info else None
    text = await format_profile(user, info)
    keyboard = get_main_menu_keyboard(cat)
    if edit:
        try:
            await message.edit(text, keyboard=keyboard)
        except Exception:
            await message.answer(text, keyboard=keyboard)
    else:
        await message.answer(text, keyboard=keyboard)


@bp.on.message(text=["/start", "Начать", "начать"])
async def start_handler(message: Message):
    user = await db.fetchone(
        "SELECT accepted_terms, first_name FROM users WHERE vk_id = ?", message.from_id
    )
    if user and user["accepted_terms"] == 1:
        if not user["first_name"]:
            await send_choose_name_step_text(message)
        else:
            await show_main_menu(message, edit=False)
    else:
        await message.answer(TERMS_TEXT, keyboard=get_terms_keyboard())


@bp.on.message(text=["Я", "я"])
async def call_main_menu(message: Message):
    user = await db.fetchone(
        "SELECT accepted_terms, first_name FROM users WHERE vk_id = ?", message.from_id
    )
    if not user or user["accepted_terms"] != 1:
        await message.answer(TERMS_TEXT, keyboard=get_terms_keyboard())
        return
    await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)
    if not user["first_name"]:
        await send_choose_name_step_text(message)
    else:
        await show_main_menu(message, edit=False)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_message_event(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "intro_next_1":
        await event.show_snackbar(" ")
        await edit_event_message(event, TERMS_TEXT, get_terms_keyboard())

    elif cmd == "intro_accept":
        await event.show_snackbar(" ")
        user = await db.fetchone("SELECT * FROM users WHERE vk_id = ?", event.user_id)
        if not user:
            await get_or_create_user(event.user_id)
        await db.execute("UPDATE users SET accepted_terms = 1 WHERE vk_id = ?", event.user_id)
        await send_choose_name_step_event(event)

    elif cmd == "intro_decline":
        await event.show_snackbar("Вы отказались от соглашения")
        await edit_event_message(
            event,
            "Вы отказались от соглашения.\nЧтобы начать заново — напишите /start.",
            ""
        )

    elif cmd == "choose_name_vk":
        await event.show_snackbar(" ")
        await db.execute("DELETE FROM user_states WHERE user_id = ?", event.user_id)
        await send_tips_step_event(event)

    elif cmd == "choose_name_custom":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'awaiting_custom_name', '{}')",
            event.user_id
        )
        await edit_event_message(event, "Введи своё уникальное имя (до 20 символов):", "")

    elif cmd == "intro_finish":
        await event.show_snackbar(" ")
        await show_main_menu_event(event)

    elif cmd in ("refresh_profile", "back_to_main"):
        await event.show_snackbar(" ")
        await show_main_menu_event(event)

    elif cmd == "open_bank":
        from bank.handlers.bank_handlers import show_bank_menu_event
        await event.show_snackbar(" ")
        await show_bank_menu_event(event)

    elif cmd == "open_jobs":
        from jobs.menu import show_categories_event
        await event.show_snackbar(" ")
        await show_categories_event(event)

    elif cmd == "open_city":
        from city.handlers.cities_handlers import show_city_menu_event
        await event.show_snackbar(" ")
        await show_city_menu_event(event)

    elif cmd == "open_experience":
        from player.handlers.experience_handlers import show_experience_menu_event
        await event.show_snackbar(" ")
        await show_experience_menu_event(event)

    elif cmd == "open_admin_panel":
        from admin.base import show_admin_panel_event
        await event.show_snackbar(" ")
        await show_admin_panel_event(event)

    elif cmd == "noop":
        await event.show_snackbar(" ")


async def send_choose_name_step_event(event: MessageEvent):
    user = await db.fetchone("SELECT game_id FROM users WHERE vk_id = ?", event.user_id)
    game_id = user["game_id"] if user else 99
    pioneer = f"(👥 Первопроходцы: {game_id - 1}/100)" if 2 <= game_id <= 101 else ""
    text = (
        f"🎉 Ты новый гражданин страны NiksKriz Corporation!\n"
        f"В честь твоего прибытия {pioneer} мэр города Величие дарит тебе 10 000 NK и 4 опыта.\n"
        f"⭐ Репутация: 0\n\nКак мне к тебе обращаться?"
    )
    await edit_event_message(event, text, get_choose_name_keyboard())


async def send_tips_step_event(event: MessageEvent):
    text = (
        "📌 Несколько советов перед стартом:\n\n"
        "1️⃣ Выбери банк.\n2️⃣ Отправляйся на работу.\n3️⃣ Ищи инвестиции, когда будет много денег."
    )
    await edit_event_message(event, text, get_tips_keyboard())


async def send_choose_name_step_text(message: Message):
    user = await db.fetchone("SELECT game_id FROM users WHERE vk_id = ?", message.from_id)
    game_id = user["game_id"] if user else 99
    pioneer = f"(👥 Первопроходцы: {game_id - 1}/100)" if 2 <= game_id <= 101 else ""
    text = (
        f"🎉 Ты новый гражданин страны NiksKriz Corporation!\n"
        f"В честь твоего прибытия {pioneer} мэр города Величие дарит тебе 10 000 NK и 4 опыта.\n"
        f"⭐ Репутация: 0\n\nКак мне к тебе обращаться?"
    )
    await message.answer(text, keyboard=get_choose_name_keyboard())


@bp.on.message()
async def handle_custom_name_input(message: Message):
    if message.payload or not message.text:
        return
    state = await db.fetchone("SELECT state FROM user_states WHERE user_id = ?", message.from_id)
    if not state or state["state"] != "awaiting_custom_name":
        return

    text = message.text.strip()
    if not text or len(text) > 20:
        await message.answer("Имя должно быть от 1 до 20 символов. Попробуй ещё раз.")
        return

    existing = await db.fetchone("SELECT vk_id FROM users WHERE nickname = ?", text)
    if existing:
        await message.answer("Это имя уже занято. Введи другое.")
        return

    await db.execute("UPDATE users SET nickname = ? WHERE vk_id = ?", text, message.from_id)
    await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    try:
        history = await message.ctx_api.messages.get_history(peer_id=message.peer_id, count=5)
        target = None
        for m in history.items:
            if m.from_id < 0:
                target = m.conversation_message_id
                break
        if target:
            await message.ctx_api.messages.delete(
                peer_id=message.peer_id, cmids=str(target), delete_for_all=True
            )
    except Exception as e:
        logger.error(f"Не удалось удалить предыдущее сообщение: {e}")

    await message.answer(
        "📌 Несколько советов перед стартом:\n\n"
        "1️⃣ Выбери банк.\n2️⃣ Отправляйся на работу.\n3️⃣ Ищи инвестиции, когда будет много денег.",
        keyboard=get_tips_keyboard()
    )