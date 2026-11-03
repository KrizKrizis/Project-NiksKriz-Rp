# lottery/handlers/lottery.py
import logging
import random
from datetime import datetime, timezone, timedelta
from vkbottle.bot import Blueprint, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from lottery.keyboards.lottery_keyboards import get_lottery_main_keyboard, get_lottery_result_keyboard

logger = logging.getLogger(__name__)
bp = Blueprint("lottery")

TICKET_PRICE = 1500
DRAW_HOURS = list(range(10, 23))


def get_moscow_now() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=3)


def get_lottery_status() -> tuple:
    now = get_moscow_now()
    current_hour = now.hour
    current_minute = now.minute

    for draw_hour in DRAW_HOURS:
        sale_start_hour = draw_hour - 1
        if current_hour == sale_start_hour and current_minute < 59:
            remaining_minutes = 59 - current_minute
            if remaining_minutes == 0:
                remaining_minutes = 1
            time_to_draw = f"1 ч {remaining_minutes:02d} мин"
            status_text = (
                f"Идёт продажа билетов на розыгрыш в {draw_hour:02d}:00.\n"
                f"Итоги будут через {time_to_draw}.\n"
                f"Стоимость билета: {TICKET_PRICE} NK."
            )
            return status_text, True, {}

    if current_minute == 59:
        if current_hour == 22:
            status_text = "Подводятся итоги последнего розыгрыша дня. Следующая продажа откроется завтра в 09:00."
        elif 9 <= current_hour < 22:
            next_draw = current_hour + 1
            status_text = f"Подводятся итоги розыгрыша. Продажа на розыгрыш {next_draw:02d}:00 начнётся в {next_draw-1:02d}:00."
        else:
            status_text = "В данный момент покупка билетов невозможна."
        return status_text, False, {}

    if current_hour < 9:
        status_text = "В данный момент купить билет невозможно. Продажа начнётся в 09:00 (на розыгрыш в 10:00)."
    elif current_hour >= 23:
        status_text = "В данный момент купить билет невозможно. Следующая продажа завтра в 09:00."
    elif current_hour == 22:
        status_text = "В данный момент купить билет невозможно. Следующая продажа завтра в 09:00."
    else:
        status_text = "В данный момент купить билет невозможно."
    return status_text, False, {}


async def _ensure_draw_for_current_hour():
    now = get_moscow_now()
    if now.minute >= 59:
        return None
    draw_hour = now.hour + 1
    if draw_hour not in DRAW_HOURS:
        return None
    draw_time = now.replace(hour=draw_hour, minute=0, second=0, microsecond=0)
    draw_time_str = draw_time.isoformat()
    row = await db.fetchone("SELECT id FROM lottery_draws WHERE draw_time = ?", draw_time_str)
    if row:
        return row["id"]
    await db.execute(
        "INSERT INTO lottery_draws (draw_time, total_pool, status) VALUES (?, 0, 'pending')",
        draw_time_str
    )
    new_row = await db.fetchone("SELECT id FROM lottery_draws WHERE draw_time = ?", draw_time_str)
    return new_row["id"] if new_row else None


async def _perform_draw(draw_id: int):
    draw = await db.fetchone("SELECT total_pool, status FROM lottery_draws WHERE id = ?", draw_id)
    if not draw or draw["status"] != "pending":
        return
    tickets = await db.fetchall(
        "SELECT user_id, COUNT(*) as cnt FROM lottery_tickets WHERE draw_id = ? GROUP BY user_id",
        draw_id
    )
    if len(tickets) < 3:
        for t in tickets:
            refund = t["cnt"] * TICKET_PRICE
            await db.execute(
                "UPDATE users SET bank_checking = bank_checking + ? WHERE vk_id = ?",
                refund, t["user_id"]
            )
        await db.execute("UPDATE lottery_draws SET status = 'cancelled' WHERE id = ?", draw_id)
        return

    total_pool = sum(t["cnt"] for t in tickets) * TICKET_PRICE
    winners = random.sample([t["user_id"] for t in tickets], k=min(3, len(tickets)))
    prize1 = int(total_pool * 0.5)
    prize2 = int(total_pool * 0.3)
    prize3 = int(total_pool * 0.2)

    if len(winners) >= 1:
        await db.execute("UPDATE users SET bank_checking = bank_checking + ? WHERE vk_id = ?", prize1, winners[0])
    if len(winners) >= 2:
        await db.execute("UPDATE users SET bank_checking = bank_checking + ? WHERE vk_id = ?", prize2, winners[1])
    if len(winners) >= 3:
        await db.execute("UPDATE users SET bank_checking = bank_checking + ? WHERE vk_id = ?", prize3, winners[2])

    await db.execute(
        "UPDATE lottery_draws SET status = 'finished', total_pool = ?, winners = ? WHERE id = ?",
        total_pool, str(winners), draw_id
    )


async def process_finished_draws():
    now = get_moscow_now()
    current_hour_start = now.replace(minute=0, second=0, microsecond=0)
    rows = await db.fetchall("SELECT id FROM lottery_draws WHERE status = 'pending'")
    for row in rows:
        draw = await db.fetchone("SELECT draw_time FROM lottery_draws WHERE id = ?", row["id"])
        if not draw:
            continue
        draw_time = datetime.fromisoformat(draw["draw_time"])
        if draw_time < current_hour_start:
            await _perform_draw(row["id"])


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
            logger.error(f"lottery edit: {e}")


async def show_lottery_menu_event(event: MessageEvent):
    status_text, can_buy, _ = get_lottery_status()
    await _edit_event(event, status_text, get_lottery_main_keyboard(can_buy))


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_lottery_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd in ("open_lottery", "lottery_main"):
        await event.show_snackbar(" ")
        await show_lottery_menu_event(event)

    elif cmd == "lottery_buy_ticket":
        _, can_buy, _ = get_lottery_status()
        if not can_buy:
            await event.show_snackbar("Покупка билетов недоступна")
            await show_lottery_menu_event(event)
            return
        draw_id = await _ensure_draw_for_current_hour()
        if draw_id is None:
            await event.show_snackbar("Не удалось определить тираж")
            return
        user = await db.fetchone("SELECT bank_checking FROM users WHERE vk_id = ?", event.user_id)
        if not user or user["bank_checking"] < TICKET_PRICE:
            await event.show_snackbar("Недостаточно средств")
            return
        await db.execute(
            "UPDATE users SET bank_checking = bank_checking - ? WHERE vk_id = ?",
            TICKET_PRICE, event.user_id
        )
        await db.execute(
            "INSERT INTO lottery_tickets (user_id, draw_id, ticket_count) VALUES (?, ?, 1)",
            event.user_id, draw_id
        )
        await db.execute(
            "UPDATE lottery_draws SET total_pool = total_pool + ? WHERE id = ?",
            TICKET_PRICE, draw_id
        )
        await event.show_snackbar("Билет куплен")
        await _edit_event(event, f"Вы купили билет за {TICKET_PRICE} NK. Удачи!", get_lottery_result_keyboard())

    elif cmd == "lottery_my_tickets":
        await event.show_snackbar(" ")
        tickets = await db.fetchall(
            "SELECT d.draw_time, COUNT(t.id) as cnt FROM lottery_tickets t "
            "JOIN lottery_draws d ON t.draw_id = d.id "
            "WHERE t.user_id = ? AND d.status = 'pending' GROUP BY d.draw_time",
            event.user_id
        )
        if not tickets:
            await _edit_event(event, "У вас нет активных билетов.", get_lottery_result_keyboard())
            return
        lines = ["Ваши билеты:"]
        for t in tickets:
            lines.append(f"• {t['draw_time']} — {t['cnt']} шт.")
        await _edit_event(event, "\n".join(lines), get_lottery_result_keyboard())

    elif cmd == "lottery_noop":
        await event.show_snackbar(" ")