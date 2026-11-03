# services/craft_service.py
import random
from datetime import datetime, timezone, timedelta
from db.database import db


def _parse_dt(dt_str):
    if not dt_str:
        return None
    dt = datetime.fromisoformat(dt_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


async def get_all_recipes() -> list:
    return await db.fetchall("SELECT * FROM craft_recipes")


async def get_recipe_by_id(recipe_id: str) -> dict:
    return await db.fetchone("SELECT * FROM craft_recipes WHERE recipe_id = ?", recipe_id)


async def get_recipe_ingredients(recipe_id: str) -> list:
    return await db.fetchall(
        "SELECT item_id, quantity, is_tool FROM craft_ingredients WHERE recipe_id = ?", recipe_id
    )


async def has_enough_items(user_id: int, ingredients: list) -> bool:
    for ing in ingredients:
        row = await db.fetchone(
            "SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?",
            user_id, ing["item_id"]
        )
        if not row:
            return False
        if not ing["is_tool"] and row["quantity"] < ing["quantity"]:
            return False
        if ing["is_tool"] and row["quantity"] < 1:
            return False
    return True


async def consume_ingredients(user_id: int, ingredients: list) -> None:
    for ing in ingredients:
        if ing["is_tool"]:
            continue
        await db.execute(
            "UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?",
            ing["quantity"], user_id, ing["item_id"]
        )
        await db.execute(
            "DELETE FROM inventory WHERE user_id = ? AND item_id = ? AND quantity <= 0",
            user_id, ing["item_id"]
        )


async def add_item_to_inventory(user_id: int, item_id: str, quantity: int = 1) -> None:
    existing = await db.fetchone(
        "SELECT id, quantity FROM inventory WHERE user_id = ? AND item_id = ?", user_id, item_id
    )
    if existing:
        await db.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", quantity, existing["id"])
    else:
        await db.execute(
            "INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)",
            user_id, item_id, quantity
        )


async def start_craft(user_id: int, recipe_id: str) -> tuple:
    if await db.fetchone("SELECT id FROM active_crafts WHERE user_id = ? AND status = 'active'", user_id):
        return False, "У вас уже есть активный крафт."
    recipe = await get_recipe_by_id(recipe_id)
    if not recipe:
        return False, "Рецепт не найден."
    ingredients = await get_recipe_ingredients(recipe_id)
    if not await has_enough_items(user_id, ingredients):
        return False, "Недостаточно ингредиентов."
    await consume_ingredients(user_id, ingredients)
    now = datetime.now(timezone.utc)
    await db.execute(
        "INSERT INTO active_crafts (user_id, recipe_id, start_time, end_time, status) "
        "VALUES (?, ?, ?, ?, 'active')",
        user_id, recipe_id, now.isoformat(),
        (now + timedelta(minutes=recipe["duration_minutes"])).isoformat()
    )
    return True, "Крафт начат."


async def finish_craft(user_id: int) -> tuple:
    active = await db.fetchone(
        "SELECT id, recipe_id, end_time FROM active_crafts WHERE user_id = ? AND status = 'active'",
        user_id
    )
    if not active:
        return False, "Нет активного крафта."
    end_time = _parse_dt(active["end_time"])
    if datetime.now(timezone.utc) < end_time:
        return False, "Крафт ещё не завершён."
    recipe = await get_recipe_by_id(active["recipe_id"])
    if not recipe:
        return False, "Рецепт не найден."
    success = random.random() < recipe["success_chance"]
    if success:
        result_item_id = recipe["result_item_id"]
        # Спец-кейс: рецепт из «Неизвестного семечка» → случайное семя
        if result_item_id == "random_seed" or active["recipe_id"] == "r_1.1.9":
            seeds = await db.fetchall("SELECT item_id FROM items WHERE type = 'seed' AND item_id != '1.1.9'")
            if seeds:
                result_item_id = random.choice(seeds)["item_id"]
            else:
                result_item_id = "1.1.16"
        await add_item_to_inventory(user_id, result_item_id, recipe["result_quantity"] or 1)
        item = await db.fetchone("SELECT name FROM items WHERE item_id = ?", result_item_id)
        name = item["name"] if item else result_item_id
        message = f"Крафт успешен! Получен предмет: {name}."
    else:
        message = "Крафт провалился. Ингредиенты потеряны."
    await db.execute("UPDATE active_crafts SET status = 'finished' WHERE id = ?", active["id"])
    return True, message


async def cancel_craft(user_id: int) -> bool:
    active = await db.fetchone("SELECT id FROM active_crafts WHERE user_id = ? AND status = 'active'", user_id)
    if not active:
        return False
    await db.execute("UPDATE active_crafts SET status = 'cancelled' WHERE id = ?", active["id"])
    return True


async def get_active_craft(user_id: int) -> dict:
    return await db.fetchone(
        "SELECT * FROM active_crafts WHERE user_id = ? AND status = 'active'", user_id
    )