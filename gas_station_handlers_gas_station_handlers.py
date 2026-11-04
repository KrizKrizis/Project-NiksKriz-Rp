# gas_station/handlers/gas_station.py
import logging
from vkbottle.bot import Blueprint, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from services.transport_service import get_active_vehicle, refuel_vehicle
from gas_station.keyboards.gas_station_keyboards import get_gas_station_main_keyboard

logger = logging.getLogger(__name__)
bp = Blueprint("gas_station")


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
            logger.error(f"gas_station edit: {e}")


async def show_gas_station_menu_event(event: MessageEvent):
    active = await get_active_vehicle(event.user_id)
    if not active:
        await _edit_event(event, "У вас нет активного транспорта. Сначала выберите транспорт.")
        return
    user = await db.fetchone("SELECT current_city, balance FROM users WHERE vk_id = ?", event.user_id)
    city = user["current_city"] if user else "Величие"
    fuel_price = 60 if city == "Величие" else 70
    text = (
        f"⛽ Заправка\n"
        f"Активный транспорт: {active['name']}\n"
        f"Топливо: {active['fuel_amount']:.1f} л / {active['tank_capacity']} л\n"
        f"Цена за литр: {fuel_price} NK\n\n"
        f"Выберите действие:"
    )
    await _edit_event(event, text, get_gas_station_main_keyboard())


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_gas_station_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd in ("open_gas_station", "gas_main"):
        await event.show_snackbar(" ")
        await show_gas_station_menu_event(event)

    elif cmd == "gas_refuel_10":
        success, msg = await refuel_vehicle(event.user_id, 10)
        await event.show_snackbar(msg[:80])
        await show_gas_station_menu_event(event)

    elif cmd == "gas_refuel_full":
        active = await get_active_vehicle(event.user_id)
        if not active:
            await event.show_snackbar("Нет активного транспорта")
            return
        needed = active["tank_capacity"] - active["fuel_amount"]
        if needed <= 0:
            await event.show_snackbar("Бак уже полон")
            return
        success, msg = await refuel_vehicle(event.user_id, needed)
        await event.show_snackbar(msg[:80])
        await show_gas_station_menu_event(event)