# transport/handlers/transport.py
import logging
from vkbottle.bot import Blueprint, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from services.transport_service import (
    get_available_vehicles, get_user_vehicles, get_active_vehicle,
    buy_vehicle, sell_vehicle, set_active_vehicle, refuel_vehicle,
)
from transport.keyboards.transport_keyboards import (
    get_transport_main_keyboard, get_transport_list_keyboard,
    get_my_vehicles_keyboard, get_vehicle_actions_keyboard,
)

logger = logging.getLogger(__name__)
bp = Blueprint("transport")


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
            logger.error(f"transport edit: {e}")


async def show_transport_menu_event(event: MessageEvent):
    await _edit_event(event, "🚗 Транспорт", get_transport_main_keyboard())


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_transport_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd in ("open_transport", "transport_main"):
        await event.show_snackbar(" ")
        await show_transport_menu_event(event)

    elif cmd == "transport_buy_list":
        await event.show_snackbar(" ")
        vehicles = await get_available_vehicles()
        if not vehicles:
            await _edit_event(event, "Нет доступных автомобилей.")
            return
        await _edit_event(event, "Доступные автомобили:", get_transport_list_keyboard(vehicles))

    elif cmd == "transport_buy":
        vehicle_id = payload.get("vehicle_id")
        success, msg = await buy_vehicle(event.user_id, vehicle_id)
        await event.show_snackbar(msg[:80])
        await show_transport_menu_event(event)

    elif cmd == "transport_my":
        await event.show_snackbar(" ")
        vehicles = await get_user_vehicles(event.user_id)
        if not vehicles:
            await _edit_event(event, "У вас нет автомобилей.", get_transport_main_keyboard())
            return
        await _edit_event(event, "Ваши автомобили:", get_my_vehicles_keyboard(vehicles))

    elif cmd == "transport_vehicle":
        vehicle_record_id = int(payload.get("vehicle_id"))
        vehicle = await db.fetchone(
            "SELECT * FROM player_vehicles WHERE id = ? AND user_id = ?",
            vehicle_record_id, event.user_id
        )
        if not vehicle:
            await event.show_snackbar("Автомобиль не найден")
            return
        await event.show_snackbar(" ")
        is_active = vehicle["active"] == 1
        await _edit_event(
            event, f"Действия с автомобилем ID {vehicle_record_id}:",
            get_vehicle_actions_keyboard(vehicle_record_id, is_active)
        )

    elif cmd == "transport_set_active":
        vehicle_record_id = int(payload.get("vehicle_id"))
        success, msg = await set_active_vehicle(event.user_id, vehicle_record_id)
        await event.show_snackbar(msg[:80])
        vehicles = await get_user_vehicles(event.user_id)
        await _edit_event(event, "Ваши автомобили:", get_my_vehicles_keyboard(vehicles))

    elif cmd == "transport_sell":
        vehicle_record_id = int(payload.get("vehicle_id"))
        success, msg = await sell_vehicle(event.user_id, vehicle_record_id)
        await event.show_snackbar(msg[:80])
        vehicles = await get_user_vehicles(event.user_id)
        if not vehicles:
            await _edit_event(event, "У вас нет автомобилей.", get_transport_main_keyboard())
            return
        await _edit_event(event, "Ваши автомобили:", get_my_vehicles_keyboard(vehicles))

    elif cmd == "transport_refuel":
        vehicle_record_id = int(payload.get("vehicle_id"))
        active = await get_active_vehicle(event.user_id)
        if not active or active["id"] != vehicle_record_id:
            await event.show_snackbar("Сначала сделайте авто активным")
            return
        success, msg = await refuel_vehicle(event.user_id, 10)
        await event.show_snackbar(msg[:80])