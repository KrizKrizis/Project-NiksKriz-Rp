from vkbottle import Keyboard, Callback, KeyboardButtonColor


def get_admin_players_keyboard(page: int, total_pages: int, permissions: dict) -> str:
    keyboard = Keyboard(inline=True)
    left_color = KeyboardButtonColor.SECONDARY if page <= 1 else KeyboardButtonColor.PRIMARY
    right_color = KeyboardButtonColor.SECONDARY if page >= total_pages else KeyboardButtonColor.POSITIVE
    keyboard.add(Callback("⬅️", payload={"cmd": "admin_players_page", "page": page - 1 if page > 1 else 1}), color=left_color)
    keyboard.add(Callback("📊 Статистика", payload={"cmd": "admin_player_stats_request"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("➡️", payload={"cmd": "admin_players_page", "page": page + 1 if page < total_pages else page}), color=right_color)
    keyboard.row()
    if permissions.get("players.view_extended", False):
        keyboard.add(Callback("📋 Логи", payload={"cmd": "admin_player_logs_request"}), color=KeyboardButtonColor.PRIMARY)
    if any(permissions.get(k, False) for k in ["players.freeze", "players.target_block", "players.full_ban"]):
        keyboard.add(Callback("⚙️ Управление", payload={"cmd": "admin_player_manage_request"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🔍 Поиск", payload={"cmd": "admin_player_search_request"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "admin_main_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


def get_admin_player_manage_keyboard(target_id: int, permissions: dict) -> str:
    keyboard = Keyboard(inline=True)
    if permissions.get("players.freeze", False):
        keyboard.add(Callback("Заморозить", payload={"cmd": "admin_manage_freeze", "target_id": target_id}), color=KeyboardButtonColor.PRIMARY)
    if permissions.get("players.target_block", False):
        keyboard.add(Callback("Точечная блокировка", payload={"cmd": "admin_manage_target_block", "target_id": target_id}), color=KeyboardButtonColor.PRIMARY)
    if permissions.get("players.full_ban", False):
        keyboard.add(Callback("Полный бан", payload={"cmd": "admin_manage_full_ban", "target_id": target_id}), color=KeyboardButtonColor.NEGATIVE)
    if permissions.get("players.unblock", False):
        keyboard.add(Callback("Разблокировать", payload={"cmd": "admin_manage_unblock", "target_id": target_id}), color=KeyboardButtonColor.PRIMARY)
    if permissions.get("players.give_money", False):
        keyboard.add(Callback("Выдать деньги", payload={"cmd": "admin_manage_give_money", "target_id": target_id}), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Callback("Изъять деньги", payload={"cmd": "admin_manage_take_money", "target_id": target_id}), color=KeyboardButtonColor.PRIMARY)
    if permissions.get("players.give_item", False):
        keyboard.add(Callback("Выдать предмет", payload={"cmd": "admin_manage_give_item", "target_id": target_id}), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Callback("Изъять предмет", payload={"cmd": "admin_manage_take_item", "target_id": target_id}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "admin_players"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()