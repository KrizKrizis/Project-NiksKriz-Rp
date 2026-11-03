# casino/keyboards/casino.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_casino_main_keyboard(is_owner: bool) -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("💰 Купить фишки", payload={"cmd": "casino_buy_chips"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Callback("💸 Продать фишки", payload={"cmd": "casino_sell_chips"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🎮 Игры", payload={"cmd": "casino_games"}), color=KeyboardButtonColor.PRIMARY)
    if is_owner:
        keyboard.add(Callback("👑 Панель владельца", payload={"cmd": "casino_owner_panel"}), color=KeyboardButtonColor.NEGATIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_city_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_games_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🎲 Кости", payload={"cmd": "casino_dice_start"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🎰 Слоты", payload={"cmd": "casino_slots_start"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🔫 Русская рулетка", payload={"cmd": "casino_roulette_start"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "casino_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_dice_guess_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Чёт", payload={"cmd": "casino_dice_guess", "guess": "чёт"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Нечет", payload={"cmd": "casino_dice_guess", "guess": "нечет"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Точное число (2-12)", payload={"cmd": "casino_dice_exact"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "casino_games"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_roulette_keyboard(current_pot: int) -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔫 Выстрел", payload={"cmd": "casino_roulette_shot"}), color=KeyboardButtonColor.NEGATIVE)
    if current_pot > 0:
        keyboard.add(Callback(f"💰 Забрать {current_pot}", payload={"cmd": "casino_roulette_collect"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Выйти", payload={"cmd": "casino_games"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_back_to_casino_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔙 В казино", payload={"cmd": "casino_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()