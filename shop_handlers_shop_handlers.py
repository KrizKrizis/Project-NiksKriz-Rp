# shop/handlers/shop.py
import json
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType, Keyboard, KeyboardButtonColor, Text
from db.database import db
from services.shop_service import (
    get_items_by_type, buy_item, sell_harvest_to_shop,
    sell_to_private_buyer, exchange_crypto_to_nk, list_on_exchange,
)
from services.business_service import buy_shop_business
from shop.keyboards.shop_keyboards import (
    get_shop_main_keyboard, get_electronics_keyboard, get_tools_keyboard,
    get_buyer_main_keyboard, get_exchange_keyboard, get_back_to_shop_keyboard,
    get_business_categories_keyboard, get_personal_business_list_keyboard,
)

logger = logging.getLogger(__name__)
bp = Blueprint("shop")


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
            logger.error(f"shop edit: {e}")


async def show_shop_menu_event(event: MessageEvent):
    await _edit_event(event, "🛒 Магазин", get_shop_main_keyboard())


async def show_shop_menu(message: Message):
    await message.answer("🛒 Магазин", keyboard=get_shop_main_keyboard())


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_shop_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd in ("open_shop", "shop_main"):
        await event.show_snackbar(" ")
        await show_shop_menu_event(event)

    elif cmd == "shop_electronics":
        await event.show_snackbar(" ")
        items = await get_items_by_type("videocard")
        if not items:
            await _edit_event(event, "В наличии нет видеокарт.", get_back_to_shop_keyboard())
            return
        await _edit_event(event, "Электроника:", get_electronics_keyboard(items))

    elif cmd == "shop_tools":
        await event.show_snackbar(" ")
        items = await get_items_by_type("tool")
        if not items:
            await _edit_event(event, "В наличии нет инструментов.", get_back_to_shop_keyboard())
            return
        await _edit_event(event, "Инструменты:", get_tools_keyboard(items))

    elif cmd == "shop_buy_item":
        item_id = payload.get("item_id")
        success, msg = await buy_item(event.user_id, item_id, 1)
        await event.show_snackbar(msg[:80])
        await show_shop_menu_event(event)

    elif cmd == "shop_buyer":
        await event.show_snackbar(" ")
        await _edit_event(event, "Скупщик", get_buyer_main_keyboard())

    elif cmd == "shop_sell_weekly":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'shop_select_item_weekly', '{}')",
            event.user_id
        )
        items = await get_items_by_type("harvest") or await get_items_by_type("resource")
        if not items:
            await _edit_event(event, "Нет предметов для продажи.")
            return
        kb = Keyboard(one_time=False, inline=True)
        for item in items:
            kb.add(Text(item["name"], payload={"cmd": "shop_weekly_select_item", "item_id": item["item_id"]}), color=KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text("🔙 Назад", payload={"cmd": "shop_buyer"}), color=KeyboardButtonColor.SECONDARY)
        await _edit_event(event, "Выберите предмет для продажи магазину:", kb.get_json())

    elif cmd == "shop_weekly_select_item":
        item_id = payload.get("item_id")
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'shop_weekly_quantity', ?)",
            event.user_id, json.dumps({"item_id": item_id})
        )
        await _edit_event(event, "Введите количество:")

    elif cmd == "shop_sell_private":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'shop_select_item_private', '{}')",
            event.user_id
        )
        items = await get_items_by_type("harvest") or await get_items_by_type("resource")
        if not items:
            await _edit_event(event, "Нет предметов для продажи.")
            return
        kb = Keyboard(one_time=False, inline=True)
        for item in items:
            kb.add(Text(item["name"], payload={"cmd": "shop_private_select_item", "item_id": item["item_id"]}), color=KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text("🔙 Назад", payload={"cmd": "shop_buyer"}), color=KeyboardButtonColor.SECONDARY)
        await _edit_event(event, "Выберите предмет для продажи частному лицу:", kb.get_json())

    elif cmd == "shop_private_select_item":
        item_id = payload.get("item_id")
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'shop_private_quantity', ?)",
            event.user_id, json.dumps({"item_id": item_id})
        )
        await _edit_event(event, "Введите количество:")

    elif cmd == "shop_exchange":
        await event.show_snackbar(" ")
        await _edit_event(event, "Биржа криптовалюты", get_exchange_keyboard())

    elif cmd == "exchange_instant":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'exchange_instant_amount', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите количество криптовалюты для мгновенного обмена:")

    elif cmd == "exchange_list":
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'exchange_list_amount', '{}')",
            event.user_id
        )
        await _edit_event(event, "Введите количество криптовалюты для выставления на биржу (24 часа):")

    elif cmd == "shop_businesses":
        await event.show_snackbar(" ")
        await _edit_event(event, "Выберите категорию бизнеса или аукцион:", get_business_categories_keyboard())

    elif cmd == "shop_business_category":
        category = payload.get("category")
        await event.show_snackbar(" ")
        businesses = await db.fetchall(
            "SELECT * FROM businesses WHERE type = 'shop' AND category = ? AND owner_id IS NULL",
            category
        )
        if not businesses:
            await _edit_event(event, "Нет доступных бизнесов в этой категории.", get_back_to_shop_keyboard())
            return
        await _edit_event(event, "Доступные бизнесы:", get_personal_business_list_keyboard(businesses))

    elif cmd == "shop_buy_business":
        business_id = payload.get("business_id")
        success, msg = await buy_shop_business(event.user_id, business_id)
        await event.show_snackbar(msg[:80])
        await show_shop_menu_event(event)

    elif cmd == "shop_open_auction":
        from auction.handlers.auction_handlers import show_auction_menu_event
        await event.show_snackbar(" ")
        await show_auction_menu_event(event)


@bp.on.message()
async def handle_shop_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state, data FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row:
        return
    state = state_row["state"]
    text = message.text.strip()

    if state == "shop_weekly_quantity":
        if not text.isdigit() or int(text) <= 0:
            await message.answer("Количество должно быть положительным числом.")
            return
        data = json.loads(state_row["data"])
        success, msg = await sell_harvest_to_shop(message.from_id, data.get("item_id"), int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "shop_private_quantity":
        if not text.isdigit() or int(text) <= 0:
            await message.answer("Количество должно быть положительным числом.")
            return
        data = json.loads(state_row["data"])
        success, msg = await sell_to_private_buyer(message.from_id, data.get("item_id"), int(text))
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "exchange_instant_amount":
        try:
            amount = float(text)
        except ValueError:
            await message.answer("Введите корректное число.")
            return
        success, msg = await exchange_crypto_to_nk(message.from_id, amount)
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    elif state == "exchange_list_amount":
        try:
            amount = float(text)
        except ValueError:
            await message.answer("Введите корректное число.")
            return
        success, msg = await list_on_exchange(message.from_id, amount)
        await message.answer(msg)
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)

    else:
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)