from vkbottle import Keyboard, Callback, KeyboardButtonColor


def get_tester_menu_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("💰 Тестовый баланс", payload={"cmd": "test_balance"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("📈 Тестовый уровень", payload={"cmd": "test_level"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("📋 Логи ошибок", payload={"cmd": "test_logs"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🔄 Сбросить тестовые данные", payload={"cmd": "test_reset"}), color=KeyboardButtonColor.NEGATIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()