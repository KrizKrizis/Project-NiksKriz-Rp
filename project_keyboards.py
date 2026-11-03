# admin/project_leadership/keyboards/project_keyboards.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_project_settings_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Цены бизнесов", payload={"cmd": "project_setting_category", "category": "business_prices"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Цены жилья", payload={"cmd": "project_setting_category", "category": "housing_prices"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Цены транспорта", payload={"cmd": "project_setting_category", "category": "vehicle_prices"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Комиссии банков", payload={"cmd": "project_setting_category", "category": "bank_commission"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Зарплаты работ", payload={"cmd": "project_setting_category", "category": "work_salaries"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Налоговые ставки", payload={"cmd": "project_setting_category", "category": "tax_rates"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Лимиты", payload={"cmd": "project_setting_category", "category": "limits"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Проценты спец. доходов", payload={"cmd": "project_setting_category", "category": "special_income_percents"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "founder_project"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()