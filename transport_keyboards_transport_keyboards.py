# transport/keyboards/transport.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_transport_main_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🚗 Мои машины", payload={"cmd": "transport_my"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🛒 Купить машину", payload={"cmd": "transport_buy_list"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_city_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_transport_list_keyboard(vehicles: list) -> str:
    keyboard = Keyboard(inline=True)
    for v in vehicles:
        label = f"{v['name']} - {v['price']} NK"
        keyboard.add(Callback(label, payload={"cmd": "transport_buy", "vehicle_id": v["vehicle_id"]}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "transport_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_my_vehicles_keyboard(vehicles: list) -> str:
    keyboard = Keyboard(inline=True)
    for v in vehicles:
        status = "🟢" if v["active"] else "⚪"
        label = f"{status} {v['name']} (топливо: {v['fuel_amount']:.0f}л)"
        keyboard.add(Callback(label, payload={"cmd": "transport_vehicle", "vehicle_id": v["id"]}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "transport_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_vehicle_actions_keyboard(vehicle_id: int, is_active: bool) -> str:
    keyboard = Keyboard(inline=True)
    if not is_active:
        keyboard.add(Callback("Сделать активной", payload={"cmd": "transport_set_active", "vehicle_id": vehicle_id}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("⛽ Заправить", payload={"cmd": "transport_refuel", "vehicle_id": vehicle_id}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("💰 Продать", payload={"cmd": "transport_sell", "vehicle_id": vehicle_id}), color=KeyboardButtonColor.NEGATIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "transport_my"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()