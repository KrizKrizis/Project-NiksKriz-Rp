# auction/handlers/auction.py
import json
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from services.auction_service import place_bid, get_auction_businesses
from auction.keyboards.auction_keyboards import get_auction_list_keyboard, get_auction_info_keyboard

logger = logging.getLogger(__name__)
bp = Blueprint("auction")


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
            logger.error(f"auction edit: {e}")


async def show_auction_menu_event(event: MessageEvent):
    businesses = await get_auction_businesses()
    if not businesses:
        await _edit_event(event, "На аукционе нет бизнесов.")
        return
    await _edit_event(event, "Аукционные бизнесы:", get_auction_list_keyboard(businesses))


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_auction_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd in ("open_auction", "auction_list"):
        await event.show_snackbar(" ")
        await show_auction_menu_event(event)

    elif cmd == "auction_info":
        business_id = payload.get("business_id")
        biz = await db.fetchone("SELECT * FROM businesses WHERE business_id = ?", business_id)
        if not biz:
            await event.show_snackbar("Бизнес не найден")
            return
        current_bid = biz["current_bid_amount"] or (2000000 if biz["type"] == "auction_casino" else 500000)
        text = f"Бизнес: {biz['name']}\nТекущая ставка: {current_bid} NK\n"
        await _edit_event(event, text, get_auction_info_keyboard(business_id))

    elif cmd == "auction_bid":
        business_id = payload.get("business_id")
        await event.show_snackbar(" ")
        await db.execute(
            "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'auction_bid_amount', ?)",
            event.user_id, json.dumps({"business_id": business_id})
        )
        await _edit_event(event, "Введите сумму ставки:")

    elif cmd == "auction_noop":
        await event.show_snackbar(" ")


@bp.on.message()
async def handle_auction_text(message: Message):
    if message.payload or not message.text:
        return
    state_row = await db.fetchone("SELECT state, data FROM user_states WHERE user_id = ?", message.from_id)
    if not state_row or state_row["state"] != "auction_bid_amount":
        return
    text = message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        await message.answer("Сумма ставки должна быть числом.")
        return
    data = json.loads(state_row["data"])
    success, msg = await place_bid(message.from_id, data.get("business_id"), int(text))
    await message.answer(msg)
    await db.execute("DELETE FROM user_states WHERE user_id = ?", message.from_id)