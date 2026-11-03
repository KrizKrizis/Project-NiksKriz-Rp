# business/keyboards/business.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor
from db.database import db

def get_business_main_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("📋 Мои бизнесы", payload={"cmd": "business_my"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_more_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_my_businesses_keyboard(businesses: list) -> str:
    keyboard = Keyboard(inline=True)
    for biz in businesses:
        keyboard.add(Callback(biz["name"], payload={"cmd": "business_panel", "business_id": biz["business_id"]}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "business_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_business_panel_keyboard(business_id: str, is_on_auction: bool, special_income_type: str = "none", commission_rate: float = 0.0) -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("💰 Снять доход", payload={"cmd": "business_withdraw", "business_id": business_id}), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Callback("🧾 Оплатить налог", payload={"cmd": "business_pay_tax", "business_id": business_id}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("📦 Оплатить продукты", payload={"cmd": "business_pay_products", "business_id": business_id}), color=KeyboardButtonColor.PRIMARY)
    if special_income_type == "bank_commission":
        keyboard.add(Callback(f"Комиссия: {commission_rate:.0%}", payload={"cmd": "business_noop"}), color=KeyboardButtonColor.SECONDARY)
        keyboard.add(Callback("Настроить комиссию", payload={"cmd": "business_set_commission", "business_id": business_id}), color=KeyboardButtonColor.PRIMARY)
    elif special_income_type == "casino_share":
        keyboard.add(Callback("📊 Статистика казино", payload={"cmd": "business_casino_stats", "business_id": business_id}), color=KeyboardButtonColor.PRIMARY)
    elif special_income_type == "auto_sale_percent":
        keyboard.add(Callback("📊 Продажи авто", payload={"cmd": "business_auto_stats", "business_id": business_id}), color=KeyboardButtonColor.PRIMARY)
    elif special_income_type == "estate_sale_percent":
        keyboard.add(Callback("📊 Продажи жилья", payload={"cmd": "business_estate_stats", "business_id": business_id}), color=KeyboardButtonColor.PRIMARY)
    elif special_income_type == "manager_firm":
        keyboard.add(Callback("👥 Менеджеры", payload={"cmd": "business_managers", "business_id": business_id}), color=KeyboardButtonColor.PRIMARY)
    if not is_on_auction:
        keyboard.add(Callback("📤 Выставить на аукцион", payload={"cmd": "business_list_auction", "business_id": business_id}), color=KeyboardButtonColor.PRIMARY)
    else:
        keyboard.add(Callback("📥 Снять с аукциона", payload={"cmd": "business_remove_auction", "business_id": business_id}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("💵 Продать государству", payload={"cmd": "business_sell_state", "business_id": business_id}), color=KeyboardButtonColor.NEGATIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "business_my"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_bank_commission_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    for rate in [0, 1, 2, 3, 4, 5]:
        keyboard.add(Callback(f"{rate}%", payload={"cmd": "business_bank_set_commission_value", "rate": rate}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "business_panel"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_managers_keyboard(business_id: str) -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Список менеджеров", payload={"cmd": "business_managers_list", "business_id": business_id}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Нанять игрока", payload={"cmd": "business_hire_manager", "business_id": business_id}), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Callback("Выплатить зарплату", payload={"cmd": "business_pay_all_salaries", "business_id": business_id}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Репутация менеджеров", payload={"cmd": "business_managers_reputation", "business_id": business_id}), color=KeyboardButtonColor.PRIMARY)
    if business_id == "1.4.15":
        keyboard.add(Callback("Выборы директора", payload={"cmd": "business_elect_director"}), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Callback("Голосовать", payload={"cmd": "business_vote_director"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "business_panel", "business_id": business_id}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_managers_list_keyboard(managers: list) -> str:
    keyboard = Keyboard(inline=True)
    for m in managers:
        label = f"{m['first_name']} {m['last_name']} (ЗП: {m['salary']})"
        keyboard.add(Callback(label, payload={"cmd": "business_manager_fire", "manager_id": m["id"]}), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Callback("Пожаловаться", payload={"cmd": "business_complaint_manager", "manager_id": m["id"]}), color=KeyboardButtonColor.NEGATIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "business_managers"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_managers_reputation_keyboard(managers_reputation: list) -> str:
    keyboard = Keyboard(inline=True)
    for r in managers_reputation:
        label = f"ID:{r['user_id']} | Репутация: {r['reputation']} | Репутация начальника: {r['boss_reputation']}"
        keyboard.add(Callback(label, payload={"cmd": "business_noop"}), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "business_managers"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_complaint_reason_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    reasons = ["Несправедливость", "Невыплата зарплаты", "Оскорбление", "Другое"]
    for reason in reasons:
        keyboard.add(Callback(reason, payload={"cmd": "business_complaint_reason", "reason": reason}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Отмена", payload={"cmd": "business_managers"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

async def get_candidates_keyboard(candidates: list) -> str:
    keyboard = Keyboard(inline=True)
    for candidate_id in candidates:
        user = await db.fetchone("SELECT first_name, last_name FROM users WHERE vk_id = ?", candidate_id)
        name = f"{user['first_name']} {user['last_name']}".strip() if user else str(candidate_id)
        keyboard.add(Callback(name, payload={"cmd": "business_vote_candidate", "candidate_id": candidate_id}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "business_managers"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_back_to_business_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔙 К бизнесам", payload={"cmd": "business_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()