# business/handlers/business.py
import json
import logging
from datetime import datetime, timezone, timedelta
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType, Keyboard, KeyboardButtonColor, Text
from db.database import db
from services.business_service import (
    get_user_businesses, sell_business_to_state, list_business_for_auction,
    remove_business_from_auction, withdraw_business_balance, pay_business_tax,
    pay_business_products, set_bank_commission, get_business_by_id,
    hire_manager, fire_manager, get_managers_for_business, pay_manager_salary,
    elect_director, vote_for_director, complaint_on_manager,
)
from business.keyboards.business_keyboards import (
    get_business_main_keyboard, get_my_businesses_keyboard, get_business_panel_keyboard,
    get_bank_commission_keyboard, get_managers_keyboard, get_managers_list_keyboard,
    get_managers_reputation_keyboard, get_complaint_reason_keyboard, get_candidates_keyboard,
    get_back_to_business_keyboard,
)

logger = logging.getLogger(__name__)
bp = Blueprint("business")

MANAGER_FIRM_ID = "2.4.3"  # Фирма менеджеров — из ids.py


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
            logger.error(f"business edit: {e}")


async def show_business_menu_event(event: MessageEvent):
    await _edit_event(event, "🏢 Бизнесы", get_business_main_keyboard())


async def _show_business_panel(event: MessageEvent, business_id: str):
    biz = await db.fetchone(
        "SELECT * FROM businesses WHERE business_id = ? AND owner_id = ?",
        business_id, event.user_id
    )
    if not biz:
        await _edit_event(event, "Бизнес не найден или не принадлежит вам.", get_business_main_keyboard())
        return
    special_income_type = biz["special_income_type"]
    is_on_auction = bool(biz["is_on_auction"])
    commission_rate = biz["commission_rate"] if special_income_type == "bank_commission" else 0.0
    kb = get_business_panel_keyboard(business_id, is_on_auction, special_income_type, commission_rate)
    text = (
        f"Название: {biz['name']}\n"
        f"Баланс бизнеса: {biz['business_balance']} NK\n"
        f"Доход (мин-макс): {biz['income_min']}-{biz['income_max']} NK\n"
        f"Продукты: {biz['product_cost']} NK (каждые 6ч)\n"
        f"Налог: {biz['tax_amount']} NK (каждые 12ч)\n"
    )
    if special_income_type == "bank_commission":
        text += f"Текущая комиссия: {commission_rate:.0%}\n"
    await _edit_event(event, text, kb)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_business_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd in ("open_businesses", "business_main"):
        await event.show_snackbar(" ")
        await show_business_menu_event(event)

    elif cmd == "business_my":
        await event.show_snackbar(" ")
        businesses = await get_user_businesses(event.user_id)
        if not businesses:
            await _edit_event(event, "У вас нет бизнесов.", get_back_to_business_keyboard())
            return
        await _edit_event(event, "Ваши бизнесы:", get_my_businesses_keyboard(businesses))

    elif cmd == "business_panel":
        await event.show_snackbar(" ")
        await _show_business_panel(event, payload.get("business_id"))

    elif cmd == "business_withdraw":
        business_id = payload.get("business_id")
        success = await withdraw_business_balance(event.user_id, business_id)
        await event.show_snackbar("Доход снят" if success else "Не удалось снять доход")
        await _show_business_panel(event, business_id)

    elif cmd == "business_pay_tax":
        business_id = payload.get("business_id")
        success = await pay_business_tax(business_id)
        await event.show_snackbar("Налог оплачен" if success else "Недостаточно средств")
        await _show_business_panel(event, business_id)

    elif cmd == "business_pay_products":
        business_id = payload.get("business_id")
        success = await pay_business_products(business_id)
        await event.show_snackbar("Продукты оплачены" if success else "Недостаточно средств")
        await _show_business_panel(event, business_id)

    elif cmd == "business_list_auction":
        business_id = payload.get("business_id")
        success, msg = await list_business_for_auction(event.user_id, business_id)
        await event.show_snackbar(msg[:80])
        await _show_business_panel(event, business_id)

    elif cmd == "business_remove_auction":
        business_id = payload.get("business_id")
        success, msg = await remove_business_from_auction(event.user_id, business_id)
        await event.show_snackbar(msg[:80])
        await _show_business_panel(event, business_id)

    elif cmd == "business_sell_state":
        business_id = payload.get("business_id")
        success, msg = await sell_business_to_state(event.user_id, business_id)
        await event.show_snackbar(msg[:80])
        await show_business_menu_event(event)

    elif cmd == "business_set_commission":
        business_id = payload.get("business_id")
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'business_commission_select', ?)",
            event.user_id, json.dumps({"business_id": business_id})
        )
        await _edit_event(event, "Выберите новую комиссию:", get_bank_commission_keyboard())

    elif cmd == "business_bank_set_commission_value":
        rate = int(payload.get("rate"))
        state_row = await db.fetchone(
            "SELECT data FROM user_states WHERE user_id = ? AND state = 'business_commission_select'",
            event.user_id
        )
        if not state_row:
            await event.show_snackbar("Ошибка")
            return
        business_id = json.loads(state_row["data"])["business_id"]
        success = await set_bank_commission(business_id, rate / 100.0)
        await event.show_snackbar("Комиссия обновлена" if success else "Ошибка")
        await db.execute("DELETE FROM user_states WHERE user_id = ?", event.user_id)
        await _show_business_panel(event, business_id)

    elif cmd == "business_casino_stats":
        business_id = payload.get("business_id")
        await event.show_snackbar(" ")
        now = datetime.now(timezone.utc)
        hour_ago = now - timedelta(hours=1)
        stats = await db.fetchone(
            "SELECT COALESCE(SUM(bet_amount), 0) as total_bets, COALESCE(SUM(result_amount), 0) as total_wins "
            "FROM casino_bets WHERE created_at >= ?",
            hour_ago.isoformat()
        )
        total_bets = stats["total_bets"] if stats else 0
        total_wins = stats["total_wins"] if stats else 0
        net_loss = max(0, total_bets - total_wins)
        owner_income = int(net_loss * 0.5)
        text = (
            f"📊 Статистика казино за последний час:\n"
            f"Всего ставок: {total_bets} NK\n"
            f"Выплачено выигрышей: {total_wins} NK\n"
            f"Чистый проигрыш игроков: {net_loss} NK\n"
            f"Ваш доход (50%): {owner_income} NK"
        )
        await _edit_event(event, text, get_back_to_business_keyboard())

    elif cmd == "business_auto_stats":
        await event.show_snackbar(" ")
        total_vehicles = await db.fetchone("SELECT COUNT(*) as cnt FROM player_vehicles")
        total_models = await db.fetchone("SELECT COUNT(*) as cnt FROM vehicles")
        text = (
            f"📊 Статистика авторынка:\n"
            f"Всего автомобилей у игроков: {total_vehicles['cnt']}\n"
            f"Всего моделей в продаже: {total_models['cnt']}\n"
        )
        await _edit_event(event, text, get_back_to_business_keyboard())

    elif cmd == "business_estate_stats":
        await event.show_snackbar(" ")
        total_housing = await db.fetchone("SELECT COUNT(*) as cnt FROM player_housing")
        total_models = await db.fetchone("SELECT COUNT(*) as cnt FROM housing")
        text = (
            f"📊 Статистика рынка жилья:\n"
            f"Всего жилья у игроков: {total_housing['cnt']}\n"
            f"Всего объектов в продаже: {total_models['cnt']}\n"
        )
        await _edit_event(event, text, get_back_to_business_keyboard())

    elif cmd == "business_managers":
        business_id = payload.get("business_id")
        await event.show_snackbar(" ")
        await _edit_event(event, "Раздел менеджеров", get_managers_keyboard(business_id))

    elif cmd == "business_managers_list":
        business_id = payload.get("business_id")
        await event.show_snackbar(" ")
        managers = await get_managers_for_business(business_id)
        if not managers:
            await _edit_event(event, "Нет нанятых менеджеров.", get_managers_keyboard(business_id))
            return
        await _edit_event(event, "Менеджеры:", get_managers_list_keyboard(managers))

    elif cmd == "business_hire_manager":
        business_id = payload.get("business_id")
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'business_hire_manager_id', ?)",
            event.user_id, json.dumps({"business_id": business_id})
        )
        await _edit_event(event, "Введите ID игрока, которого хотите нанять менеджером:")

    elif cmd == "business_manager_fire":
        manager_id = int(payload.get("manager_id"))
        success = await fire_manager(manager_id)
        await event.show_snackbar("Менеджер уволен" if success else "Ошибка увольнения")

    elif cmd == "business_pay_all_salaries":
        business_id = payload.get("business_id")
        managers = await get_managers_for_business(business_id)
        for m in managers:
            await pay_manager_salary(m["id"])
        await event.show_snackbar("Зарплаты выплачены")

    elif cmd == "business_managers_reputation":
        await event.show_snackbar(" ")
        reps = await db.fetchall("SELECT * FROM manager_reputation")
        await _edit_event(event, "Репутации менеджеров:", get_managers_reputation_keyboard(reps))

    elif cmd == "business_complaint_manager":
        manager_id = int(payload.get("manager_id"))
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'business_complaint_reason', ?)",
            event.user_id, json.dumps({"manager_id": manager_id})
        )
        await _edit_event(event, "Выберите причину жалобы:", get_complaint_reason_keyboard())

    elif cmd == "business_complaint_reason":
        reason = payload.get("reason")
        state_row = await db.fetchone(
            "SELECT data FROM user_states WHERE user_id = ? AND state = 'business_complaint_reason'",
            event.user_id
        )
        if not state_row:
            await event.show_snackbar("Ошибка")
            return
        manager_id = json.loads(state_row["data"])["manager_id"]
        await complaint_on_manager(manager_id, reason)
        await event.show_snackbar("Жалоба отправлена")
        await db.execute("DELETE FROM user_states WHERE user_id = ?", event.user_id)

    elif cmd == "business_elect_director":
        firm = await get_business_by_id(MANAGER_FIRM_ID)
        if not firm or firm["owner_id"] != event.user_id:
            await event.show_snackbar("Вы не владелец Фирмы менеджеров")
            return
        await elect_director()
        await event.show_snackbar("Выборы запущены")

    elif cmd == "business_vote_director":
        row = await db.fetchone("SELECT data FROM user_states WHERE state = 'firm_election_candidates'")
        if not row:
            await event.show_snackbar("Голосование не активно")
            return
        candidates = json.loads(row["data"])
        if not candidates:
            await event.show_snackbar("Нет кандидатов")
            return
        kb = await get_candidates_keyboard(candidates)
        await _edit_event(event, "Выберите кандидата:", kb)

    elif cmd == "business_vote_candidate":
        candidate_id = int(payload.get("candidate_id"))
        success, msg = await vote_for_director(event.user_id, candidate_id)
        await event.show_snackbar(msg[:80])

    elif cmd == "business_noop":
        await event.show_snackbar(" ")


@bp.on.message()
async def handle_business_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state, data FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row:
        return
    if state_row["state"] == "business_hire_manager_id":
        text = message.text.strip()
        if not text.isdigit():
            await message.answer("ID должен быть числом.")
            return
        data = json.loads(state_row["data"])
        success, msg = await hire_manager(data["business_id"], int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)
    else:
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)