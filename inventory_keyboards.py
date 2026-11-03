# player/keyboards/inventory.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_inventory_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_city_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()