# nkvito/handlers/nkvito.py
import json
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from services.nkvito_service import (
    get_active_listings, get_user_listings, get_user_inventory_items,
    create_listing, buy_listing, cancel_listing, check_expired_listings,
)
from nkvito.keyboards.nkvito_keyboards import (
    get_nkvito_main_keyboard, get_listings_keyboard, get_inventory_items_keyboard,
    get_duration_keyboard, get_my_listings_keyboard,
)

logger = logging.getLogger(__name__)
bp = Blueprint("nkvito")


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
            logger.error(f"nkvito edit: {e}")


async def show_nkvito_menu_event(event: MessageEvent):
    await check_expired_listings()
    await _edit_event(event, "🤝 NKVito — торговая площадка", get_nkvito_main_keyboard())


async def _show_listings_page(event: MessageEvent, page: int):
    listings = await get_active_listings(page)
    next_page = await get_active_listings(page + 1)
    has_next = len(next_page) > 0
    if not listings:
        await _edit_event(event, "Нет активных лотов.", get_nkvito_main_keyboard())
        return
    kb = get_listings_keyboard(listings, page, has_next)
    await _edit_event(event, "Активные лоты:", kb)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_nkvito_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd in ("open_nkvito", "nkvito_menu"):
        await event.show_snackbar(" ")
        await show_nkvito_menu_event(event)

    elif cmd == "nkvito_listings":
        await event.show_snackbar(" ")
        await _show_listings_page(event, 1)

    elif cmd == "nkvito_page":
        await event.show_snackbar(" ")
        await _show_listings_page(event, int(payload.get("page", 1)))

    elif cmd == "nkvito_create":
        await event.show_snackbar(" ")
        items = await get_user_inventory_items(event.user_id)
        if not items:
            await _edit_event(event, "Ваш инвентарь пуст.", get_nkvito_main_keyboard())
            return
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'nkvito_select_item', '{}')",
            event.user_id
        )
        await _edit_event(event, "Выберите предмет для продажи:", get_inventory_items_keyboard(items))

    elif cmd == "nkvito_select_item":
        item_id = payload.get("item_id")
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'nkvito_enter_price', ?)",
            event.user_id, json.dumps({"item_id": item_id})
        )
        await _edit_event(event, "Введите цену (в NK):")

    elif cmd == "nkvito_duration":
        days = int(payload.get("days"))
        state_row = await db.fetchone(
            "SELECT data FROM user_states WHERE user_id = ? AND state = 'nkvito_enter_duration'",
            event.user_id
        )
        if not state_row:
            await event.show_snackbar("Ошибка. Начните заново")
            await show_nkvito_menu_event(event)
            return
        data = json.loads(state_row["data"])
        success, msg = await create_listing(event.user_id, data.get("item_id"), int(data.get("price")), days)
        await event.show_snackbar(msg[:80])
        await db.execute("DELETE FROM user_states WHERE user_id = ?", event.user_id)
        await show_nkvito_menu_event(event)

    elif cmd == "nkvito_my":
        await event.show_snackbar(" ")
        listings = await get_user_listings(event.user_id)
        if not listings:
            await _edit_event(event, "У вас нет активных лотов.", get_nkvito_main_keyboard())
            return
        await _edit_event(event, "Ваши лоты (нажмите, чтобы снять):", get_my_listings_keyboard(listings))

    elif cmd == "nkvito_cancel":
        listing_id = int(payload.get("listing_id"))
        success, msg = await cancel_listing(listing_id, event.user_id)
        await event.show_snackbar(msg[:80])
        listings = await get_user_listings(event.user_id)
        if listings:
            await _edit_event(event, "Ваши лоты:", get_my_listings_keyboard(listings))
        else:
            await _edit_event(event, "У вас нет активных лотов.", get_nkvito_main_keyboard())

    elif cmd == "nkvito_buy":
        listing_id = int(payload.get("listing_id"))
        success, msg = await buy_listing(listing_id, event.user_id)
        await event.show_snackbar(msg[:80])
        if success:
            await show_nkvito_menu_event(event)


@bp.on.message()
async def handle_nkvito_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state, data FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row:
        return
    state = state_row["state"]
    text = message.text.strip()

    if state == "nkvito_enter_price":
        if not text.isdigit() or int(text) <= 0:
            await message.answer("Цена должна быть положительным числом.")
            return
        data = json.loads(state_row["data"])
        data["price"] = int(text)
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'nkvito_enter_duration', ?)",
            message.from_id, json.dumps(data)
        )
        await message.answer("Выберите срок размещения:", keyboard=get_duration_keyboard())

    else:
        await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)