from vkbottle import Keyboard, Text, KeyboardButtonColor


def get_deputy_menu_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Text("👤 Игроки", payload={"cmd": "deputy_players"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("👥 Команда", payload={"cmd": "deputy_team"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("⚙️ Проект", payload={"cmd": "deputy_project"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("📊 Статистика проекта", payload={"cmd": "deputy_project_stats"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text("🔙 Назад", payload={"cmd": "back_to_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()