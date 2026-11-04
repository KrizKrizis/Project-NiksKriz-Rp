# shop/keyboards/shop.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_shop_main_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🛒 Электроника", payload={"cmd": "shop_electronics"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🛠 Инструменты", payload={"cmd": "shop_tools"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("💰 Скупщик", payload={"cmd": "shop_buyer"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🏢 Бизнесы", payload={"cmd": "shop_businesses"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_city_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_electronics_keyboard(items: list) -> str:
    keyboard = Keyboard(inline=True)
    for item in items:
        keyboard.add(Callback(f"{item['name']} - {item['base_price']} NK", payload={"cmd": "shop_buy_item", "item_id": item["item_id"]}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "shop_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_tools_keyboard(items: list) -> str:
    keyboard = Keyboard(inline=True)
    for item in items:
        keyboard.add(Callback(f"{item['name']} - {item['base_price']} NK", payload={"cmd": "shop_buy_item", "item_id": item["item_id"]}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "shop_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_buyer_main_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Продать магазину", payload={"cmd": "shop_sell_weekly"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Продать частному лицу", payload={"cmd": "shop_sell_private"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("🏦 Биржа", payload={"cmd": "shop_exchange"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "shop_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_exchange_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Обменять", payload={"cmd": "exchange_instant"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Выставить", payload={"cmd": "exchange_list"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "shop_buyer"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_back_to_shop_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔙 В магазин", payload={"cmd": "shop_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_business_categories_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Новичок", payload={"cmd": "shop_business_category", "category": "novice"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Бывалый", payload={"cmd": "shop_business_category", "category": "experienced"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Миллионер", payload={"cmd": "shop_business_category", "category": "millionaire"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🏛 Аукцион", payload={"cmd": "shop_open_auction"}), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "shop_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_personal_business_list_keyboard(businesses: list) -> str:
    keyboard = Keyboard(inline=True)
    for biz in businesses:
        keyboard.add(Callback(biz["name"], payload={"cmd": "shop_buy_business", "business_id": biz["business_id"]}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "shop_businesses"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()