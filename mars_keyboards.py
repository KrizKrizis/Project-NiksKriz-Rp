# mars/keyboards/mars.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_investments_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🚀 Инвестировать", payload={"cmd": "invest_start"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Callback("📊 Прогресс", payload={"cmd": "invest_progress"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_city_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_invest_back_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔙 В инвестиции", payload={"cmd": "invest_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()