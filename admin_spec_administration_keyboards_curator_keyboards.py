from vkbottle import Keyboard, Text, KeyboardButtonColor


def get_curator_menu_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Text("👤 Игроки", payload={"cmd": "curator_players"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("👥 Команда", payload={"cmd": "curator_team"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("📊 Статистика", payload={"cmd": "curator_statistics"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("📋 Аудит", payload={"cmd": "curator_audit"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text("🔙 Назад", payload={"cmd": "back_to_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()