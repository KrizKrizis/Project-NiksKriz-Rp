# city/handlers/cities.py
import asyncio
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from city.keyboards.cities_keyboards import (
    get_city_menu_keyboard, get_more_menu_keyboard, get_bus_routes_keyboard,
    get_travel_result_keyboard,
)
from utils.images import get_attachment

logger = logging.getLogger(__name__)
bp = Blueprint("city")

BUS_TICKET_PRICE = 250
TRAVEL_DELAY_SECONDS = 5


async def _get_user_city(user_id: int) -> str:
    row = await db.fetchone("SELECT current_city FROM users WHERE vk_id = ?", user_id)
    return row["current_city"] if row else "Величие"


async def _has_active_vehicle(user_id: int) -> bool:
    row = await db.fetchone("SELECT id FROM player_vehicles WHERE user_id = ? AND active = 1", user_id)
    return row is not None


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
            logger.error(f"city edit: {e}")


async def show_city_menu_event(event: MessageEvent):
    city = await _get_user_city(event.user_id)
    has_vehicle = await _has_active_vehicle(event.user_id)
    text = f"📍 Текущий город: {city}\n\nЧто вы хотите сделать?"
    kb = get_city_menu_keyboard(city, has_vehicle)
    city_to_id = {"Величие": "5.1.1", "Звездограцк": "5.1.2", "Мемград": "5.1.3"}
    await _edit_event(event, text, kb, city_to_id.get(city))


async def show_more_menu_event(event: MessageEvent):
    await _edit_event(event, "Дополнительно:", get_more_menu_keyboard())


async def show_more_menu(message: Message):
    """Текстовая версия для craft и других модулей."""
    await message.answer("Дополнительно:", keyboard=get_more_menu_keyboard())


async def show_city_menu(message: Message):
    city = await _get_user_city(message.from_id)
    has_vehicle = await _has_active_vehicle(message.from_id)
    text = f"📍 Текущий город: {city}\n\nЧто вы хотите сделать?"
    await message.answer(text, keyboard=get_city_menu_keyboard(city, has_vehicle))


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_city_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd in ("open_city", "back_to_city_menu"):
        await event.show_snackbar(" ")
        await show_city_menu_event(event)

    elif cmd == "open_more":
        await event.show_snackbar(" ")
        await show_more_menu_event(event)

    elif cmd == "open_bus_routes":
        await event.show_snackbar(" ")
        current_city = await _get_user_city(event.user_id)
        kb = get_bus_routes_keyboard(current_city)
        await _edit_event(event, "🚌 Выберите город, в который хотите отправиться:", kb)

    elif cmd == "travel_bus":
        target_city = payload.get("city")
        user = await db.fetchone("SELECT balance FROM users WHERE vk_id = ?", event.user_id)
        if not user or user["balance"] < BUS_TICKET_PRICE:
            await event.show_snackbar("Недостаточно средств на билет")
            return
        await event.show_snackbar(" ")
        await db.execute(
            "UPDATE users SET balance = balance - ? WHERE vk_id = ?",
            BUS_TICKET_PRICE, event.user_id
        )
        try:
            await event.ctx_api.messages.edit(
                peer_id=event.peer_id,
                conversation_message_id=event.conversation_message_id,
                message=f"🚌 Вы сели на автобус до города {target_city}. В пути... (Списано {BUS_TICKET_PRICE} NK)",
                keyboard=""
            )
        except Exception:
            pass
        await asyncio.sleep(TRAVEL_DELAY_SECONDS)
        await db.execute(
            "UPDATE users SET current_city = ? WHERE vk_id = ?",
            target_city, event.user_id
        )
        try:
            await event.ctx_api.messages.edit(
                peer_id=event.peer_id,
                conversation_message_id=event.conversation_message_id,
                message=f"✅ Вы прибыли в город {target_city}.",
                keyboard=get_travel_result_keyboard()
            )
        except Exception as e:
            logger.error(f"Ошибка при редактировании результата поездки: {e}")

    elif cmd == "open_inventory":
        from player.handlers.inventory_handlers import show_inventory_menu_event
        await event.show_snackbar(" ")
        await show_inventory_menu_event(event)

    elif cmd == "open_craft":
        from craft.handlers.craft_handlers import show_craft_menu_event
        await event.show_snackbar(" ")
        await show_craft_menu_event(event)

    elif cmd == "open_lottery":
        from lottery.handlers.lottery_handlers import show_lottery_menu_event
        await event.show_snackbar(" ")
        await show_lottery_menu_event(event)

    elif cmd == "open_nkvito":
        from nkvito.handlers.nkvito_handlers import show_nkvito_menu_event
        await event.show_snackbar(" ")
        await show_nkvito_menu_event(event)

    elif cmd == "open_housing":
        from housing.handlers.housing_handlers import show_housing_menu_event
        await event.show_snackbar(" ")
        await show_housing_menu_event(event)

    elif cmd == "open_transport":
        from transport.handlers.transport_handlers import show_transport_menu_event
        await event.show_snackbar(" ")
        await show_transport_menu_event(event)

    elif cmd == "open_shop":
        from shop.handlers.shop_handlers import show_shop_menu_event
        await event.show_snackbar(" ")
        await show_shop_menu_event(event)

    elif cmd == "open_gas_station":
        from gas_station.handlers.gas_station_handlers import show_gas_station_menu_event
        await event.show_snackbar(" ")
        await show_gas_station_menu_event(event)

    elif cmd == "open_investments":
        from mars.handlers.mars_handlers import show_investments_menu_event
        await event.show_snackbar(" ")
        await show_investments_menu_event(event)

    elif cmd == "open_casino":
        from casino.handlers.casino_handlers import show_casino_menu_event
        await event.show_snackbar(" ")
        await show_casino_menu_event(event)

    elif cmd == "back_to_main":
        from player.handlers.main_menu_handlers import show_main_menu_event
        await show_main_menu_event(event)


@bp.on.message(payload={"cmd": "back_to_city_menu"})
async def back_to_city_menu_text(message: Message):
    await show_city_menu(message)