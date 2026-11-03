# admin/project_leadership/keyboards/leadership_menu.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_founder_main_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("👤 Игрок / Проект", payload={"cmd": "founder_players"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("👥 Команда проекта", payload={"cmd": "founder_team"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("💼 Бизнес основателя", payload={"cmd": "founder_business_accounts"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🚪 Выход", payload={"cmd": "admin_logout"}), color=KeyboardButtonColor.NEGATIVE)
    return keyboard.get_json()

def get_players_menu_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("⬅️", payload={"cmd": "players_page", "page": 1}), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Callback("📊 Статистика", payload={"cmd": "player_stats_request"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("➡️", payload={"cmd": "players_page", "page": 1}), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    keyboard.add(Callback("📋 Логи", payload={"cmd": "player_logs_request"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🔍 Поиск", payload={"cmd": "player_search_request"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("⚙️ Управление", payload={"cmd": "player_manage_request"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "founder_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_project_menu_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("📦 Бэкап", payload={"cmd": "system_backup"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("📋 Логи", payload={"cmd": "system_logs"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🎁 Промокоды", payload={"cmd": "project_promocodes"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("⚙️ Настройка", payload={"cmd": "project_settings"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("💬 Чаты", payload={"cmd": "system_chats"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("📊 Статистика проекта", payload={"cmd": "project_statistics"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "founder_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_team_menu_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("⚙️ Управление", payload={"cmd": "team_management"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🎁 Вознаграждения", payload={"cmd": "team_rewards"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("📊 Статистика", payload={"cmd": "team_statistics"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "founder_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_business_accounts_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    accounts = [("1", "emission"), ("2", "commission"), ("3", "lottery"), ("4", "investment"), ("5", "giveaways"), ("6", "salary")]
    for num, cmd in accounts:
        keyboard.add(Callback(num, payload={"cmd": f"business_account_{cmd}"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "founder_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()