# lottery/keyboards/lottery.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_lottery_main_keyboard(can_buy: bool) -> str:
    keyboard = Keyboard(inline=True)
    if can_buy:
        keyboard.add(Callback("Купить билет", payload={"cmd": "lottery_buy_ticket"}), color=KeyboardButtonColor.POSITIVE)
    else:
        keyboard.add(Callback("Купить билет", payload={"cmd": "lottery_noop"}), color=KeyboardButtonColor.NEGATIVE)
    keyboard.add(Callback("Мои билеты", payload={"cmd": "lottery_my_tickets"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_city_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_lottery_result_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔙 В лотерею", payload={"cmd": "lottery_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()