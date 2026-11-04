# mars/handlers/mars.py
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from mars.keyboards.mars_keyboards import get_investments_keyboard, get_invest_back_keyboard

logger = logging.getLogger(__name__)
bp = Blueprint("mars")

GLOBAL_GOAL = 1_000_000_000
PLAYER_LIMIT = 10_000_000


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
            logger.error(f"mars edit: {e}")


async def _get_total_invested() -> int:
    row = await db.fetchone("SELECT COALESCE(SUM(amount), 0) as total FROM mars_investments")
    return row["total"] if row else 0


async def _get_user_invested(user_id: int) -> int:
    row = await db.fetchone(
        "SELECT COALESCE(SUM(amount), 0) as total FROM mars_investments WHERE user_id = ?",
        user_id
    )
    return row["total"] if row else 0


async def show_investments_menu_event(event: MessageEvent):
    total = await _get_total_invested()
    user_total = await _get_user_invested(event.user_id)
    progress = (total / GLOBAL_GOAL) * 100 if GLOBAL_GOAL else 0
    text = (
        f"🚀 Инвестиции в терраформирование Марса\n\n"
        f"Общий прогресс: {total:,} / {GLOBAL_GOAL:,} NK ({progress:.2f}%)\n"
        f"Ваш вклад: {user_total:,} NK\n"
        f"Лимит на игрока: {PLAYER_LIMIT:,} NK"
    )
    await _edit_event(event, text, get_investments_keyboard())


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_mars_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd in ("open_investments", "invest_main", "invest_progress"):
        await event.show_snackbar(" ")
        await show_investments_menu_event(event)

    elif cmd == "invest_start":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'awaiting_invest_amount', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите сумму для инвестирования (от 1 до 10 000 000 NK):")


@bp.on.message()
async def handle_invest_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row or state_row["state"] != "awaiting_invest_amount":
        return

    text = message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        await message.answer("Сумма должна быть положительным целым числом.")
        return

    amount = int(text)
    user_id = message.from_id
    already = await _get_user_invested(user_id)
    if already + amount > PLAYER_LIMIT:
        await message.answer(f"Вы превышаете лимит. Осталось доступно: {PLAYER_LIMIT - already} NK.")
        return

    user = await db.fetchone("SELECT bank_checking FROM users WHERE vk_id = ?", user_id)
    if not user or user["bank_checking"] < amount:
        await message.answer("Недостаточно средств на основном счёте.")
        return

    await db.execute(
        "UPDATE users SET bank_checking = bank_checking - ? WHERE vk_id = ?",
        amount, user_id
    )
    await db.execute(
        "INSERT INTO mars_investments (user_id, amount) VALUES (?, ?)",
        user_id, amount
    )
    await db.execute("DELETE FROM user_states WHERE user_id = ?", user_id)

    total = await _get_total_invested()
    await message.answer(
        f"✅ Вы инвестировали {amount:,} NK. Общий сбор: {total:,} NK.",
        keyboard=get_invest_back_keyboard()
    )

    if total >= GLOBAL_GOAL:
        await _handle_goal_reached()


async def _handle_goal_reached():
    investors = await db.fetchall(
        "SELECT user_id, SUM(amount) as total_amount FROM mars_investments "
        "GROUP BY user_id HAVING SUM(amount) >= 10000000"
    )
    for inv in investors:
        user_id = inv["user_id"]
        items = await db.fetchall(
            "SELECT item_id FROM inventory WHERE user_id = ? AND item_id IN ('4.3.10', '4.5.4', '4.5.3')",
            user_id
        )
        if {row["item_id"] for row in items} == {'4.3.10', '4.5.4', '4.5.3'}:
            existing = await db.fetchone(
                "SELECT id FROM inventory WHERE user_id = ? AND item_id = '4.8.1'",
                user_id
            )
            if not existing:
                await db.execute(
                    "INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, '4.8.1', 1)",
                    user_id
                )
                try:
                    import builtins
                    if hasattr(builtins, "bot"):
                        await builtins.bot.api.messages.send(
                            user_id=user_id,
                            message="🎉 Поздравляем! Вы получили Базу на Марсе!",
                            random_id=0
                        )
                except Exception as e:
                    logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")