from vkbottle import Keyboard, Callback, KeyboardButtonColor


def get_helpers_main_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("👥 Игроки", payload={"cmd": "helpers_players"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("📬 Обращения", payload={"cmd": "helpers_requests"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("📊 Моя статистика", payload={"cmd": "helpers_stats"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Выйти", payload={"cmd": "back_to_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


def get_helpers_players_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "helpers_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()