from vkbottle import Keyboard, Callback, KeyboardButtonColor


def get_spec_admin_main_keyboard(user_id: int, permissions: dict) -> str:
    keyboard = Keyboard(inline=True)
    if permissions.get("players.view", False):
        keyboard.add(Callback("👤 Игроки", payload={"cmd": "spec_players"}), color=KeyboardButtonColor.PRIMARY)
    if permissions.get("team.view", False):
        keyboard.add(Callback("👥 Команда", payload={"cmd": "spec_team"}), color=KeyboardButtonColor.PRIMARY)
    if permissions.get("project.manage", False):
        keyboard.add(Callback("⚙️ Проект", payload={"cmd": "spec_project"}), color=KeyboardButtonColor.PRIMARY)
    if permissions.get("test_panel", False):
        keyboard.add(Callback("🛠 Тест-панель", payload={"cmd": "spec_test_panel"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Выйти", payload={"cmd": "back_to_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()