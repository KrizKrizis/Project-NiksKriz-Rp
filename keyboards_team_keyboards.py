from vkbottle import Keyboard, Callback, KeyboardButtonColor


def get_team_management_keyboard(permissions: dict) -> str:
    keyboard = Keyboard(inline=True)
    if permissions.get("team.manage", False):
        keyboard.add(Callback("Назначить роль", payload={"cmd": "admin_team_assign"}), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Callback("Снять роль", payload={"cmd": "admin_team_remove"}), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Callback("Повысить/Понизить", payload={"cmd": "admin_team_promote"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "admin_team"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


def get_role_selection_keyboard(target_id: int, action: str) -> str:
    keyboard = Keyboard(inline=True)
    roles = [
        ("Хелпер", 1, "1.1"),
        ("Администратор", 2, "2.1"),
        ("Старший администратор", 2, "2.2"),
        ("ЗГА", 2, "2.3"),
        ("ГА", 2, "2.4"),
    ]
    cmd = "admin_team_assign_confirm" if action == "assign" else "admin_team_promote_confirm"
    for name, cat, pos in roles:
        keyboard.add(Callback(name, payload={"cmd": cmd, "target_id": target_id, "category": cat, "position": pos}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Отмена", payload={"cmd": "admin_team"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()