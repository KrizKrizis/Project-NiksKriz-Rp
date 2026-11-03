from vkbottle import Keyboard, Callback, KeyboardButtonColor


def get_administration_main_keyboard(admin_id: int, permissions: dict) -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("👤 Игроки", payload={"cmd": "admin_players"}), color=KeyboardButtonColor.PRIMARY)
    if permissions.get("complaints.view", False):
        keyboard.add(Callback("📋 Жалобы", payload={"cmd": "admin_complaints"}), color=KeyboardButtonColor.PRIMARY)
    if permissions.get("team.view", False):
        keyboard.add(Callback("👥 Команда", payload={"cmd": "admin_team"}), color=KeyboardButtonColor.PRIMARY)
    if permissions.get("team.manage", False):
        keyboard.add(Callback("📊 Статистика", payload={"cmd": "admin_statistics"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Выйти", payload={"cmd": "back_to_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()