# player/keyboards/main_menu.py
from typing import Optional
from vkbottle import Keyboard, Callback, KeyboardButtonColor


def get_start_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Продолжить", payload={"cmd": "intro_next_1"}), color=KeyboardButtonColor.POSITIVE)
    return keyboard.get_json()


def get_terms_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Согласиться", payload={"cmd": "intro_accept"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Callback("Отказаться", payload={"cmd": "intro_decline"}), color=KeyboardButtonColor.NEGATIVE)
    return keyboard.get_json()


def get_choose_name_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Взять из ВК", payload={"cmd": "choose_name_vk"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Ввести своё", payload={"cmd": "choose_name_custom"}), color=KeyboardButtonColor.PRIMARY)
    return keyboard.get_json()


def get_tips_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("В меню", payload={"cmd": "intro_finish"}), color=KeyboardButtonColor.POSITIVE)
    return keyboard.get_json()


def get_main_menu_keyboard(admin_category: Optional[int] = None) -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔄 Обновить", payload={"cmd": "refresh_profile"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Callback("💼 Работа", payload={"cmd": "open_jobs"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🏙 Город", payload={"cmd": "open_city"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🏦 Банк", payload={"cmd": "open_bank"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("📈 Опыт", payload={"cmd": "open_experience"}), color=KeyboardButtonColor.PRIMARY)
    if admin_category:
        admin_button_text = {1: "🛠 Мод-Пан", 2: "🛡 Адм-Пан", 3: "👑 Спец-Пан", 4: "⚙️ Тех-Пан"}.get(admin_category, "🛠 Адм-Пан")
        keyboard.add(Callback(admin_button_text, payload={"cmd": "open_admin_panel"}), color=KeyboardButtonColor.NEGATIVE)
    return keyboard.get_json()


def get_experience_keyboard(can_claim: bool) -> str:
    keyboard = Keyboard(inline=True)
    if can_claim:
        keyboard.add(Callback("Получить опыт", payload={"cmd": "claim_exp"}), color=KeyboardButtonColor.POSITIVE)
    else:
        keyboard.add(Callback("Получить опыт (недоступно)", payload={"cmd": "noop"}), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()