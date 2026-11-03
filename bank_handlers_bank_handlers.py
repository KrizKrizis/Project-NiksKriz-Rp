# bank/handlers/bank.py
import json
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from services.bank_service import (
    transfer_between_users, transfer_between_own_accounts, apply_savings_interest,
)
from bank.keyboards.bank_keyboards import (
    get_bank_main_keyboard, get_bank_selection_keyboard, get_balance_keyboard,
    get_transfer_menu_keyboard, get_account_selection_keyboard,
    get_savings_keyboard, get_tax_keyboard,
)
from utils.images import get_attachment

logger = logging.getLogger(__name__)
bp = Blueprint("bank")


async def _edit_event(event: MessageEvent, text: str, keyboard: str, image_key: str = None):
    kwargs = {
        "peer_id": event.peer_id,
        "conversation_message_id": event.conversation_message_id,
        "message": text,
        "keyboard": keyboard,
    }
    if image_key:
        try:
            attach = await get_attachment(image_key)
            if attach:
                kwargs["attachment"] = attach
        except Exception:
            pass
    try:
        await event.ctx_api.messages.edit(**kwargs)
    except Exception:
        try:
            send_kwargs = {"peer_id": event.peer_id, "message": text, "keyboard": keyboard, "random_id": 0}
            if "attachment" in kwargs:
                send_kwargs["attachment"] = kwargs["attachment"]
            await event.ctx_api.messages.send(**send_kwargs)
        except Exception as e:
            logger.error(f"bank edit: {e}")


async def show_bank_menu_event(event: MessageEvent):
    user = await db.fetchone("SELECT bank_name FROM users WHERE vk_id = ?", event.user_id)
    has_bank = bool(user and user["bank_name"])
    await apply_savings_interest(event.user_id)

    image_key = None
    if has_bank:
        bank_to_id = {"NK Bank": "2.5.1", "Zero Bank": "2.4.9", "Fallen Bank": "2.4.10"}
        image_key = bank_to_id.get(user["bank_name"])

    await _edit_event(event, "🏦 Банк", get_bank_main_keyboard(has_bank), image_key)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_bank_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd in ("open_bank", "bank_main"):
        await event.show_snackbar(" ")
        await show_bank_menu_event(event)

    elif cmd == "bank_select":
        await event.show_snackbar(" ")
        await _edit_event(event, "Выберите банк из списка:", get_bank_selection_keyboard())

    elif cmd == "bank_choose":
        bank_name = payload.get("bank")
        if bank_name in ["NK Bank", "Zero Bank", "Fallen Bank"]:
            await db.execute(
                "UPDATE users SET bank_name = ? WHERE vk_id = ?", bank_name, event.user_id
            )
            await event.show_snackbar(f"Выбран {bank_name}")
            await show_bank_menu_event(event)

    elif cmd == "bank_balance":
        await event.show_snackbar(" ")
        await apply_savings_interest(event.user_id)
        user = await db.fetchone(
            "SELECT balance, bank_checking, bank_savings, tax_account, bank_name "
            "FROM users WHERE vk_id = ?",
            event.user_id
        )
        text = (
            f"💰 Баланс\n"
            f"💵 Наличные: {user['balance']} NK\n"
            f"🏦 Банк: {user['bank_name']}\n"
            f"💳 Основной счёт: {user['bank_checking']} NK\n"
            f"📈 Накопительный: {user['bank_savings']} NK (лимит 750 000)\n"
            f"🧾 Налоговый: {user['tax_account']} NK"
        )
        await _edit_event(event, text, get_balance_keyboard())

    elif cmd == "bank_transfer_menu":
        await event.show_snackbar(" ")
        await _edit_event(event, "Переводы:", get_transfer_menu_keyboard())

    elif cmd == "bank_transfer_user":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'awaiting_receiver_id', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите ID игрока, которому хотите перевести средства:", "")

    elif cmd == "bank_transfer_own":
        await event.show_snackbar(" ")
        await _edit_event(event, "Выберите счёт, с которого хотите перевести:", get_account_selection_keyboard())

    elif cmd == "bank_select_account":
        account = payload.get("account")
        state_row = await db.fetchone(
            "SELECT state, data FROM user_states WHERE user_id = ?", event.user_id
        )

        if state_row is None:
            await db.execute(
                "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'awaiting_to_account', ?)",
                event.user_id, json.dumps({"from_account": account})
            )
            await _edit_event(event, "Теперь выберите счёт назначения:", get_account_selection_keyboard())
        else:
            if state_row["state"] == "awaiting_to_account":
                data = json.loads(state_row["data"])
                from_acc = data.get("from_account")
                await db.execute(
                    "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'awaiting_amount_own', ?)",
                    event.user_id, json.dumps({"from_account": from_acc, "to_account": account})
                )
                await _edit_event(event, "Введите сумму для перевода:", "")
            else:
                await db.execute("DELETE FROM user_states WHERE user_id = ?", event.user_id)
                await event.show_snackbar("Ошибка. Начните заново")

    elif cmd == "bank_savings":
        await event.show_snackbar(" ")
        await apply_savings_interest(event.user_id)
        user = await db.fetchone("SELECT bank_savings FROM users WHERE vk_id = ?", event.user_id)
        text = f"📈 Накопительный счёт: {user['bank_savings']} NK\nПроценты начисляются раз в час (1%)."
        await _edit_event(event, text, get_savings_keyboard())

    elif cmd == "bank_tax":
        await event.show_snackbar(" ")
        user = await db.fetchone("SELECT tax_account FROM users WHERE vk_id = ?", event.user_id)
        text = f"🧾 Налоговый счёт: {user['tax_account']} NK"
        await _edit_event(event, text, get_tax_keyboard())


@bp.on.message()
async def handle_bank_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state, data FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row:
        return
    state = state_row["state"]
    data = json.loads(state_row["data"]) if state_row["data"] else {}
    text = message.text.strip()

    if state == "awaiting_receiver_id":
        if not text.isdigit():
            await message.answer("ID должен быть числом.")
            return
        receiver_id = int(text)
        user_exists = await db.fetchone("SELECT vk_id FROM users WHERE vk_id = ?", receiver_id)
        if not user_exists:
            await message.answer("Игрок с таким ID не найден.")
            return
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'awaiting_amount_user', ?)",
            message.from_id, json.dumps({"receiver_id": receiver_id})
        )
        await message.answer("Введите сумму для перевода:")

    elif state == "awaiting_amount_user":
        if not text.isdigit() or int(text) <= 0:
            await message.answer("Сумма должна быть положительным числом.")
            return
        success, msg = await transfer_between_users(message.from_id, data.get("receiver_id"), int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "awaiting_amount_own":
        if not text.isdigit() or int(text) <= 0:
            await message.answer("Сумма должна быть положительным числом.")
            return
        success, msg = await transfer_between_own_accounts(
            message.from_id, data.get("from_account"), data.get("to_account"), int(text)
        )
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "awaiting_to_account":
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    else:
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)