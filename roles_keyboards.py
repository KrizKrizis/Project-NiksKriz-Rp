# admin/project_leadership/keyboards/roles_keyboards.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_roles_menu_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Назначить роль", payload={"cmd": "team_assign_role"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Снять роль", payload={"cmd": "team_remove_role"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "founder_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()