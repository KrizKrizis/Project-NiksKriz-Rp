# nkvito/keyboards/nkvito.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_nkvito_main_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🛍 Список лотов", payload={"cmd": "nkvito_listings"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("➕ Создать лот", payload={"cmd": "nkvito_create"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Callback("📋 Мои лоты", payload={"cmd": "nkvito_my"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_more_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_listings_keyboard(listings: list, page: int, has_next: bool) -> str:
    keyboard = Keyboard(inline=True)
    for lot in listings:
        label = f"{lot['item_name']} - {lot['price']} NK (Продавец: {lot['seller_game_id']})"
        keyboard.add(Callback(label, payload={"cmd": "nkvito_buy", "listing_id": lot["id"]}), color=KeyboardButtonColor.PRIMARY)
    nav_row = []
    if page > 1:
        nav_row.append(Callback("⬅️ Назад", payload={"cmd": "nkvito_page", "page": page - 1}))
    if has_next:
        nav_row.append(Callback("➡️ Вперёд", payload={"cmd": "nkvito_page", "page": page + 1}))
    if nav_row:
        keyboard.row()
        for btn in nav_row:
            keyboard.add(btn, color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    keyboard.add(Callback("🔙 К меню", payload={"cmd": "nkvito_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_inventory_items_keyboard(items: list) -> str:
    keyboard = Keyboard(inline=True)
    for item in items:
        label = f"{item['name']} (x{item['quantity']})"
        keyboard.add(Callback(label, payload={"cmd": "nkvito_select_item", "item_id": item["item_id"]}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Отмена", payload={"cmd": "nkvito_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_duration_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    durations = [("1 день (1500 NK)", 1), ("2 дня (3000 NK)", 2), ("3 дня (5000 NK)", 3), ("4 дня (7500 NK)", 4), ("5 дней (10000 NK)", 5)]
    for label, days in durations:
        keyboard.add(Callback(label, payload={"cmd": "nkvito_duration", "days": days}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Отмена", payload={"cmd": "nkvito_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_my_listings_keyboard(listings: list) -> str:
    keyboard = Keyboard(inline=True)
    for lot in listings:
        label = f"{lot['item_name']} - {lot['price']} NK"
        keyboard.add(Callback(label, payload={"cmd": "nkvito_cancel", "listing_id": lot["id"]}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "nkvito_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()