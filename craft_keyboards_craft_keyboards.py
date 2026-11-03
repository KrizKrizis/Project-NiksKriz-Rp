# craft/keyboards/craft.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_craft_recipes_keyboard(recipes: list) -> str:
    keyboard = Keyboard(inline=True)
    for recipe in recipes:
        keyboard.add(Callback(recipe["name"], payload={"cmd": "craft_recipe_info", "recipe_id": recipe["recipe_id"]}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "back_to_more_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_recipe_info_keyboard(recipe_id: str) -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔨 Скрафтить", payload={"cmd": "start_craft", "recipe_id": recipe_id}), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "craft_recipes"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_active_craft_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔄 Обновить", payload={"cmd": "refresh_craft"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("❌ Отменить", payload={"cmd": "cancel_craft"}), color=KeyboardButtonColor.NEGATIVE)
    return keyboard.get_json()