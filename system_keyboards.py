# admin/project_leadership/keyboards/system_keyboards.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_system_menu_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔄 Сбросить кеш ролей", payload={"cmd": "system_reload_cache"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("📦 Создать бэкап", payload={"cmd": "system_backup"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("📋 Логи", payload={"cmd": "system_logs"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("💬 Управление чатами", payload={"cmd": "system_chats"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("⏰ Планировщик", payload={"cmd": "system_scheduler"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🚀 Перезагрузить конфигурацию", payload={"cmd": "system_reload_config"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "founder_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_chats_menu_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    modes = {2: "Хелперы", 3: "Администрация", 4: "Статистика", 5: "Общая команда", 6: "Тестеры", 7: "Полный лог"}
    for mode, desc in modes.items():
        keyboard.add(Callback(f"Режим {mode}: {desc}", payload={"cmd": "system_chat_set", "mode": mode}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "system_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()