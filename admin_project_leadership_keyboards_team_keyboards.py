# admin/project_leadership/keyboards/team_keyboards.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_team_management_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Назначить роль", payload={"cmd": "team_assign_role"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Снять роль", payload={"cmd": "team_remove_role"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Повысить/Понизить", payload={"cmd": "team_promote"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Выдать выговор", payload={"cmd": "team_warning"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "founder_team"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_team_rewards_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Начислить админ-койны", payload={"cmd": "team_rewards"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "founder_team"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()