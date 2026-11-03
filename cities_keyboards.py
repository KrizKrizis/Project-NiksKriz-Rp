# city/keyboards/cities.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor


def get_city_menu_keyboard(current_city: str, has_active_vehicle: bool) -> str:
    keyboard = Keyboard(inline=True)

    if current_city == "Величие":
        keyboard.add(Callback("🏠 Имущество", payload={"cmd": "open_housing"}), color=KeyboardButtonColor.PRIMARY)
    elif current_city == "Звездограцк":
        keyboard.add(Callback("🚀 Инвестиции", payload={"cmd": "open_investments"}), color=KeyboardButtonColor.PRIMARY)
    elif current_city == "Мемград":
        keyboard.add(Callback("🎰 Казино", payload={"cmd": "open_casino"}), color=KeyboardButtonColor.PRIMARY)

    if has_active_vehicle:
        keyboard.add(Callback("🚗 Транспорт", payload={"cmd": "open_transport"}), color=KeyboardButtonColor.PRIMARY)
    else:
        keyboard.add(Callback("🚌 Автобус", payload={"cmd": "open_bus_routes"}), color=KeyboardButtonColor.PRIMARY)

    keyboard.row()
    keyboard.add(Callback("🛒 Магазин", payload={"cmd": "open_shop"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("⛽ Заправка", payload={"cmd": "open_gas_station"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("📦 Ещё", payload={"cmd": "open_more"}), color=KeyboardButtonColor.PRIMARY)

    keyboard.row()
    keyboard.add(Callback("🔙 В главное меню", payload={"cmd": "back_to_main"}), color=KeyboardButtonColor.SECONDARY)

    return keyboard.get_json()


def get_more_menu_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🎒 Инвентарь", payload={"cmd": "open_inventory"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🔨 Крафт", payload={"cmd": "open_craft"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🎫 Лотерея", payload={"cmd": "open_lottery"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🤝 NKVito", payload={"cmd": "open_nkvito"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад в город", payload={"cmd": "back_to_city_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


def get_bus_routes_keyboard(current_city: str) -> str:
    keyboard = Keyboard(inline=True)
    all_cities = ["Звездограцк", "Мемград", "Величие"]
    other_cities = [c for c in all_cities if c != current_city]

    for city in other_cities:
        keyboard.add(Callback(f"🚌 {city}", payload={"cmd": "travel_bus", "city": city}), color=KeyboardButtonColor.PRIMARY)

    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_city_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


def get_travel_result_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔙 В город", payload={"cmd": "back_to_city_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()