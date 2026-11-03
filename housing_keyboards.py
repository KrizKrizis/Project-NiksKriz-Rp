# housing/keyboards/housing.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_housing_main_keyboard(user_housing: dict) -> str:
    keyboard = Keyboard(inline=True)
    if user_housing:
        keyboard.add(Callback("🏠 Мой дом", payload={"cmd": "housing_my"}), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Callback("🔧 Криптоферма", payload={"cmd": "housing_crypto_farm"}), color=KeyboardButtonColor.PRIMARY)
        if user_housing["type"] == "house":
            keyboard.add(Callback("🌱 Садоводство", payload={"cmd": "housing_garden"}), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Callback("💰 Продать", payload={"cmd": "housing_sell"}), color=KeyboardButtonColor.NEGATIVE)
    else:
        keyboard.add(Callback("🛒 Купить жильё", payload={"cmd": "housing_buy_list"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_city_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_housing_list_keyboard(housing_list: list) -> str:
    keyboard = Keyboard(inline=True)
    for h in housing_list:
        label = f"{h['name']} - {h['price']} NK ({h['parking_spots']} мест)"
        keyboard.add(Callback(label, payload={"cmd": "housing_buy", "housing_id": h["housing_id"]}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "housing_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_housing_my_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "housing_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_crypto_farm_keyboard(has_farm: bool) -> str:
    keyboard = Keyboard(inline=True)
    if not has_farm:
        keyboard.add(Callback("Установить криптоферму (150 000 NK)", payload={"cmd": "housing_buy_farm"}), color=KeyboardButtonColor.POSITIVE)
    else:
        keyboard.add(Callback("Продать криптоферму (50 000 NK)", payload={"cmd": "housing_sell_farm"}), color=KeyboardButtonColor.NEGATIVE)
        keyboard.add(Callback("Установить видеокарту", payload={"cmd": "housing_install_videocard"}), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Callback("Снять видеокарту", payload={"cmd": "housing_remove_videocard"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "housing_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_garden_main_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Купить участок 1 (500 000 NK)", payload={"cmd": "garden_buy_plot", "plot": 1}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Купить участок 2 (800 000 NK)", payload={"cmd": "garden_buy_plot", "plot": 2}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "housing_main"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_garden_plots_keyboard(plots: list) -> str:
    keyboard = Keyboard(inline=True)
    for plot in plots:
        keyboard.add(Callback(f"Участок {plot['plot_number']}", payload={"cmd": "garden_plot", "plot_number": plot["plot_number"]}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "housing_garden"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_garden_plot_actions_keyboard(plot_number: int) -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Посадить", payload={"cmd": "garden_plant", "plot": plot_number}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Полить", payload={"cmd": "garden_water", "plot": plot_number}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("Собрать", payload={"cmd": "garden_harvest", "plot": plot_number}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "housing_garden"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()