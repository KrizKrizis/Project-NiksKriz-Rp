# player/handlers/experience.py
import logging
import random
from datetime import datetime, timezone
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from player.keyboards.main_menu_keyboards import get_experience_keyboard

logger = logging.getLogger(__name__)
bp = Blueprint("player_experience")


def _parse_datetime(dt_str: str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


async def edit_event_message(event: MessageEvent, text: str, keyboard: str):
    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        message=text,
        keyboard=keyboard
    )


async def get_experience_data(user_id: int):
    user = await db.fetchone("SELECT level, exp, last_exp_bonus_time FROM users WHERE vk_id = ?", user_id)
    if not user:
        return None, None, None

    level = user["level"]
    exp = user["exp"]
    last_bonus_str = user["last_exp_bonus_time"]
    exp_to_next = 5 * level
    progress = int((exp / exp_to_next) * 100) if exp_to_next > 0 else 100

    now = datetime.now(timezone.utc)
    can_claim = False
    if last_bonus_str:
        last_bonus = _parse_datetime(last_bonus_str)
        if last_bonus and (now - last_bonus).total_seconds() >= 3600:
            can_claim = True
    else:
        can_claim = True

    text = (
        f"📈 Уровень: {level}\n"
        f"Опыт: {exp} / {exp_to_next}\n"
        f"Прогресс до следующего уровня: {progress}%\n\n"
        "Бонусный опыт доступен раз в час."
    )
    return text, can_claim, level


async def show_experience_menu_event(event: MessageEvent):
    text, can_claim, _ = await get_experience_data(event.user_id)
    if not text:
        return
    await edit_event_message(event, text, get_experience_keyboard(can_claim))


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_experience_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "open_experience":
        await event.show_snackbar(" ")
        await show_experience_menu_event(event)

    elif cmd == "claim_exp":
        await event.show_snackbar(" ")
        text, can_claim, level = await get_experience_data(event.user_id)
        if not can_claim:
            await event.show_snackbar("⏳ Опыт ещё не готов")
            return

        gained_exp = random.randint(100, 500)
        user = await db.fetchone("SELECT exp FROM users WHERE vk_id = ?", event.user_id)
        new_exp = user["exp"] + gained_exp
        new_level = level
        leveled_up = False
        while new_exp >= 5 * new_level:
            new_exp -= 5 * new_level
            new_level += 1
            leveled_up = True

        now = datetime.now(timezone.utc)
        await db.execute(
            "UPDATE users SET exp = ?, level = ?, last_exp_bonus_time = ? WHERE vk_id = ?",
            new_exp, new_level, now.isoformat(), event.user_id
        )

        await event.show_snackbar(f"🎁 +{gained_exp} опыта")
        await show_experience_menu_event(event)

    elif cmd == "back_to_main":
        from player.handlers.main_menu_handlers import show_main_menu_event
        await show_main_menu_event(event)