# casino/handlers/casino.py
import json
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType, Keyboard, KeyboardButtonColor, Text
from db.database import db
from services.casino_service import (
    buy_chips, sell_chips, play_dice, play_slots,
    play_russian_roulette, collect_russian_roulette_winnings,
)
from services.business_service import withdraw_business_balance, pay_business_tax
from casino.keyboards.casino_keyboards import (
    get_casino_main_keyboard, get_games_keyboard, get_dice_guess_keyboard,
    get_roulette_keyboard, get_back_to_casino_keyboard,
)

logger = logging.getLogger(__name__)
bp = Blueprint("casino")

CASINO_BUSINESS_ID = "2.4.1"  # Казино «Золотое» — из ids.py


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
            logger.error(f"casino edit: {e}")


async def _is_casino_available() -> bool:
    casino = await db.fetchone(
        "SELECT * FROM businesses WHERE business_id = ? AND hidden = 0",
        CASINO_BUSINESS_ID
    )
    return casino is not None


async def _is_casino_owner(user_id: int) -> bool:
    row = await db.fetchone(
        "SELECT id FROM businesses WHERE business_id = ? AND owner_id = ?",
        CASINO_BUSINESS_ID, user_id
    )
    return row is not None


async def show_casino_menu_event(event: MessageEvent):
    user = await db.fetchone("SELECT current_city FROM users WHERE vk_id = ?", event.user_id)
    if not user or user["current_city"] != "Мемград":
        await _edit_event(event, "Казино доступно только в Мемграде.", get_back_to_casino_keyboard())
        return
    if not await _is_casino_available():
        await _edit_event(event, "Казино закрыто.", get_back_to_casino_keyboard())
        return
    is_owner = await _is_casino_owner(event.user_id)
    await _edit_event(event, "🎰 Казино", get_casino_main_keyboard(is_owner))


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_casino_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd in ("open_casino", "casino_main"):
        await event.show_snackbar(" ")
        await show_casino_menu_event(event)

    elif cmd == "casino_buy_chips":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'casino_buy_chips_amount', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите сумму в NK для покупки фишек (1 фишка = 100 NK):")

    elif cmd == "casino_sell_chips":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'casino_sell_chips_amount', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите количество фишек для продажи (1 фишка = 90 NK):")

    elif cmd == "casino_games":
        await event.show_snackbar(" ")
        await _edit_event(event, "Выберите игру:", get_games_keyboard())

    elif cmd == "casino_dice_start":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'casino_dice_bet', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите ставку в фишках:")

    elif cmd == "casino_dice_guess":
        guess = payload.get("guess")
        state_row = await db.fetchone(
            "SELECT data FROM user_states WHERE user_id = ? AND state = 'casino_dice_bet'",
            event.user_id
        )
        if not state_row:
            await event.show_snackbar("Ошибка. Начните игру заново")
            await _edit_event(event, "Выберите игру:", get_games_keyboard())
            return
        bet = int(json.loads(state_row["data"]).get("bet", 0))
        success, msg, _ = await play_dice(event.user_id, bet, guess)
        await event.show_snackbar(msg[:80])
        await db.execute("DELETE FROM user_states WHERE user_id = ?", event.user_id)
        await show_casino_menu_event(event)

    elif cmd == "casino_dice_exact":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'casino_dice_exact_number', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите число от 2 до 12:")

    elif cmd == "casino_slots_start":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'casino_slots_bet', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите ставку в фишках:")

    elif cmd == "casino_roulette_start":
        await event.show_snackbar(" ")
        state_row = await db.fetchone(
            "SELECT data FROM user_states WHERE user_id = ? AND state = 'roulette'",
            event.user_id
        )
        if state_row:
            current_pot = json.loads(state_row["data"]).get("current_pot", 0)
            await _edit_event(event, f"У вас уже есть активная серия. Текущий банк: {current_pot}", get_roulette_keyboard(current_pot))
            return
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'casino_roulette_bet', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите ставку в фишках:")

    elif cmd == "casino_roulette_shot":
        state_row = await db.fetchone("SELECT state, data FROM user_states WHERE user_id = ?", event.user_id)
        if not state_row:
            await event.show_snackbar("Нет активной игры")
            return
        state = state_row["state"]
        if state == "roulette":
            bet = 0
        elif state == "casino_roulette_bet":
            bet = int(json.loads(state_row["data"]).get("bet", 0))
        else:
            await event.show_snackbar("Ошибка состояния")
            return
        success, msg, current_pot = await play_russian_roulette(event.user_id, bet)
        await event.show_snackbar(msg[:80])
        if current_pot > 0:
            await _edit_event(event, "Хотите продолжить?", get_roulette_keyboard(current_pot))
        else:
            await db.execute("DELETE FROM user_states WHERE user_id = ?", event.user_id)
            await show_casino_menu_event(event)

    elif cmd == "casino_roulette_collect":
        success, msg, _ = await collect_russian_roulette_winnings(event.user_id)
        await event.show_snackbar(msg[:80])
        await show_casino_menu_event(event)

    elif cmd == "casino_owner_panel":
        if not await _is_casino_owner(event.user_id):
            await event.show_snackbar("Вы не владелец казино")
            return
        casino = await db.fetchone("SELECT * FROM businesses WHERE business_id = ?", CASINO_BUSINESS_ID)
        text = (
            f"👑 Панель владельца казино\n"
            f"Баланс казино: {casino['business_balance']} NK\n"
            f"Налог: {casino['tax_amount']} NK (каждые 12 часов)\n"
            f"Продукты: {casino['product_cost']} NK (каждые 6 часов)\n"
        )
        kb = Keyboard(one_time=False, inline=True)
        kb.add(Text("💰 Снять доход", payload={"cmd": "casino_owner_withdraw"}), color=KeyboardButtonColor.POSITIVE)
        kb.add(Text("🧾 Оплатить налог", payload={"cmd": "casino_owner_pay_tax"}), color=KeyboardButtonColor.PRIMARY)
        kb.add(Text("📉 Продать лицензию", payload={"cmd": "casino_owner_sell"}), color=KeyboardButtonColor.NEGATIVE)
        kb.row()
        kb.add(Text("🔙 Назад", payload={"cmd": "casino_main"}), color=KeyboardButtonColor.SECONDARY)
        await _edit_event(event, text, kb.get_json())

    elif cmd == "casino_owner_withdraw":
        success = await withdraw_business_balance(event.user_id, CASINO_BUSINESS_ID)
        await event.show_snackbar("Доход снят" if success else "Не удалось снять доход")

    elif cmd == "casino_owner_pay_tax":
        success = await pay_business_tax(CASINO_BUSINESS_ID)
        await event.show_snackbar("Налог оплачен" if success else "Недостаточно средств")

    elif cmd == "casino_owner_sell":
        sell_price = int(2_000_000 * 0.6)
        await db.execute("UPDATE users SET balance = balance + ? WHERE vk_id = ?", sell_price, event.user_id)
        await db.execute(
            "UPDATE businesses SET owner_id = NULL, business_balance = 0, is_on_auction = 0 WHERE business_id = ?",
            CASINO_BUSINESS_ID
        )
        await event.show_snackbar(f"Лицензия продана за {sell_price} NK")
        await show_casino_menu_event(event)


@bp.on.message()
async def handle_casino_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state, data FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row:
        return
    state = state_row["state"]
    text = message.text.strip()

    if state == "casino_buy_chips_amount":
        if not text.isdigit() or int(text) <= 0:
            await message.answer("Введите корректную сумму.")
            return
        success, msg = await buy_chips(message.from_id, int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "casino_sell_chips_amount":
        if not text.isdigit() or int(text) <= 0:
            await message.answer("Введите корректное количество.")
            return
        success, msg = await sell_chips(message.from_id, int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "casino_dice_bet":
        if not text.isdigit() or int(text) <= 0:
            await message.answer("Ставка должна быть положительным числом.")
            return
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'casino_dice_bet', ?)",
            message.from_id, json.dumps({"bet": int(text)})
        )
        await message.answer("Выберите тип ставки:", keyboard=get_dice_guess_keyboard())

    elif state == "casino_dice_exact_number":
        if not text.isdigit() or int(text) < 2 or int(text) > 12:
            await message.answer("Введите число от 2 до 12.")
            return
        bet_state = await db.fetchone(
            "SELECT data FROM user_states WHERE user_id = ? AND state = 'casino_dice_bet'",
            message.from_id
        )
        if not bet_state:
            await message.answer("Ошибка. Ставка не найдена.")
            return
        bet = int(json.loads(bet_state["data"]).get("bet", 0))
        success, msg, _ = await play_dice(message.from_id, bet, text)
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "casino_slots_bet":
        if not text.isdigit() or int(text) <= 0:
            await message.answer("Ставка должна быть положительным числом.")
            return
        success, msg, _ = await play_slots(message.from_id, int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "casino_roulette_bet":
        if not text.isdigit() or int(text) <= 0:
            await message.answer("Ставка должна быть положительным числом.")
            return
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'casino_roulette_bet', ?)",
            message.from_id, json.dumps({"bet": int(text)})
        )
        success, msg, current_pot = await play_russian_roulette(message.from_id, int(text))
        await message.answer(msg)
        if current_pot > 0:
            await message.answer("Продолжайте или заберите выигрыш:", keyboard=get_roulette_keyboard(current_pot))
        else:
            await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    else:
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)