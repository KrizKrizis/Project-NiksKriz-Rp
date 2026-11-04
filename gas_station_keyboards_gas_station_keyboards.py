# gas_station/keyboards/gas_station.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_gas_station_main_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Заправить 10 литров", payload={"cmd": "gas_refuel_10"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Заправить полный бак", payload={"cmd": "gas_refuel_full"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_city_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_gas_station_back_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "gas_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()