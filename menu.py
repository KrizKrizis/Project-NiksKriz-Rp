# jobs/menu.py
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType
from vkbottle import Keyboard, Callback, KeyboardButtonColor
from db.database import db

bp = Blueprint("jobs_menu")


async def get_jobs_keyboard(user_id: int):
    user = await db.fetchone("SELECT level FROM users WHERE vk_id = ?", user_id)
    level = user["level"] if user else 1

    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🆕 Начальные", payload={"cmd": "jobs_category", "category": "novice"}), color=KeyboardButtonColor.PRIMARY)
    if level >= 3:
        keyboard.add(Callback("🚖 Постоянные", payload={"cmd": "jobs_category", "category": "permanent"}), color=KeyboardButtonColor.PRIMARY)
    if level >= 10:
        keyboard.add(Callback("💼 Миллионер", payload={"cmd": "jobs_category", "category": "millionaire"}), color=KeyboardButtonColor.PRIMARY)
    if level >= 49:
        keyboard.add(Callback("🚀 Элитные", payload={"cmd": "jobs_category", "category": "elite"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


async def show_categories_event(event: MessageEvent):
    text = "Выберите категорию работ:"
    kb = await get_jobs_keyboard(event.user_id)
    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        message=text,
        keyboard=kb
    )


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_jobs_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "open_jobs":
        await event.show_snackbar(" ")
        await show_categories_event(event)

    elif cmd == "jobs_category":
        category = payload.get("category")
        await event.show_snackbar(" ")

        if category == "novice":
            from jobs.novice.handlers.novice_handlers import show_novice_jobs_event
            await show_novice_jobs_event(event)
        elif category == "permanent":
            from jobs.permanent.handlers.permanent_handlers import show_permanent_jobs_event
            await show_permanent_jobs_event(event)
        elif category == "millionaire":
            from jobs.millionaire.handlers.millionaire_handlers import show_millionaire_jobs_event
            await show_millionaire_jobs_event(event)
        elif category == "elite":
            from jobs.elite.handlers.elite_handlers import show_elite_jobs_event
            await show_elite_jobs_event(event)