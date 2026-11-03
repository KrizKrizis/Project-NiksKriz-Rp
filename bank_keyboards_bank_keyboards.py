# bank/keyboards/bank.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor


def get_bank_main_keyboard(has_bank: bool) -> str:
    keyboard = Keyboard(inline=True)
    if not has_bank:
        keyboard.add(Callback("🏦 Выбрать банк", payload={"cmd": "bank_select"}), color=KeyboardButtonColor.PRIMARY)
    else:
        keyboard.add(Callback("💰 Баланс", payload={"cmd": "bank_balance"}), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Callback("↔️ Переводы", payload={"cmd": "bank_transfer_menu"}), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Callback("📈 Накопительный", payload={"cmd": "bank_savings"}), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Callback("🧾 Налоговый", payload={"cmd": "bank_tax"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


def get_bank_selection_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("NK Bank", payload={"cmd": "bank_choose", "bank": "NK Bank"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Zero Bank", payload={"cmd": "bank_choose", "bank": "Zero Bank"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Fallen Bank", payload={"cmd": "bank_choose", "bank": "Fallen Bank"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "bank_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


def get_balance_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "bank_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


def get_transfer_menu_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("👤 Другому игроку", payload={"cmd": "bank_transfer_user"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🔄 Между своими счетами", payload={"cmd": "bank_transfer_own"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "bank_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


def get_account_selection_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Наличные", payload={"cmd": "bank_select_account", "account": "balance"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Основной счёт", payload={"cmd": "bank_select_account", "account": "bank_checking"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Накопительный", payload={"cmd": "bank_select_account", "account": "bank_savings"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Налоговый", payload={"cmd": "bank_select_account", "account": "tax_account"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "bank_transfer_own"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


def get_savings_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "bank_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


def get_tax_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "bank_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()