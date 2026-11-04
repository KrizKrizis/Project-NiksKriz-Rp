# services/housing_service.py
import random
from datetime import datetime, timezone, timedelta
from db.database import db

VIDEOCARD_SLOTS = {
    "3.1.1": 5, "3.1.2": 10, "3.1.3": 20,
    "3.1.4": 30, "3.1.5": 50, "3.1.6": 100,
}

PLANT_TYPE_TO_HARVEST = {
    "огурцы": "1.6.1",
    "помидоры": "1.6.2",
    "морковь": "1.6.3",
    "земляника": "1.6.4",
    "ежевика": "1.6.5",
    "дыня": "1.6.6",
    "арбуз": "1.6.7",
    "яблоко": "1.6.8",
    "вишня": "1.6.9",
    "груша": "1.6.10",
    "мандарин": "1.6.11",
    "картошка": "1.6.12",
}

SEED_ID_TO_PLANT_TYPE = {
    "1.1.16": "огурцы",
    "1.1.17": "помидоры",
    "1.1.18": "морковь",
    "1.1.19": "земляника",
    "1.1.20": "ежевика",
    "1.1.21": "дыня",
    "1.1.22": "арбуз",
    "1.1.23": "яблоко",
    "1.1.24": "вишня",
    "1.1.25": "груша",
    "1.1.26": "мандарин",
    "1.1.27": "картошка",
}


def _parse_dt(dt_str):
    if not dt_str:
        return None
    dt = datetime.fromisoformat(dt_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


async def get_config_value(key: str, default=None):
    row = await db.fetchone("SELECT value FROM config WHERE key = ?", key)
    return row["value"] if row else default


async def get_available_housing() -> list:
    return await db.fetchall("SELECT * FROM housing")


async def get_user_housing(user_id: int) -> dict:
    return await db.fetchone(
        "SELECT ph.*, h.name, h.type, h.price, h.parking_spots FROM player_housing ph "
        "JOIN housing h ON ph.housing_id = h.housing_id WHERE ph.user_id = ?",
        user_id
    )


async def buy_housing(user_id: int, housing_id: str) -> tuple:
    if await get_user_housing(user_id):
        return False, "У вас уже есть жильё."
    housing = await db.fetchone("SELECT * FROM housing WHERE housing_id = ?", housing_id)
    if not housing:
        return False, "Жильё не найдено."
    user = await db.fetchone("SELECT balance FROM users WHERE vk_id = ?", user_id)
    if not user or user["balance"] < housing["price"]:
        return False, "Недостаточно наличных."
    await db.execute("UPDATE users SET balance = balance - ? WHERE vk_id = ?", housing["price"], user_id)
    await db.execute(
        "INSERT INTO player_housing (user_id, housing_id, has_crypto_farm) VALUES (?, ?, 0)",
        user_id, housing_id
    )
    return True, f"Вы купили {housing['name']}."


async def sell_housing(user_id: int) -> tuple:
    housing = await get_user_housing(user_id)
    if not housing:
        return False, "У вас нет жилья."
    sell_price = int(housing["price"] * 0.6)
    await db.execute("UPDATE users SET balance = balance + ? WHERE vk_id = ?", sell_price, user_id)
    await db.execute("DELETE FROM player_housing WHERE user_id = ?", user_id)
    await db.execute("DELETE FROM garden_plots WHERE user_id = ?", user_id)
    await db.execute("DELETE FROM garden_plants WHERE user_id = ?", user_id)
    await db.execute("DELETE FROM crypto_farm WHERE user_id = ?", user_id)
    return True, f"Жильё продано за {sell_price} NK."


async def buy_crypto_farm(user_id: int) -> tuple:
    housing = await get_user_housing(user_id)
    if not housing:
        return False, "Сначала купите жильё."
    if housing["has_crypto_farm"]:
        return False, "Криптоферма уже установлена."
    cost = int(await get_config_value("crypto_farm_base_cost", 150000))
    user = await db.fetchone("SELECT balance FROM users WHERE vk_id = ?", user_id)
    if not user or user["balance"] < cost:
        return False, "Недостаточно наличных."
    await db.execute("UPDATE users SET balance = balance - ? WHERE vk_id = ?", cost, user_id)
    await db.execute(
        "UPDATE player_housing SET has_crypto_farm = 1, crypto_farm_installed_at = ? WHERE user_id = ?",
        datetime.now(timezone.utc).isoformat(), user_id
    )
    return True, "Криптоферма установлена."


async def sell_crypto_farm(user_id: int) -> tuple:
    housing = await get_user_housing(user_id)
    if not housing or not housing["has_crypto_farm"]:
        return False, "Криптоферма не установлена."
    sell_price = int(await get_config_value("crypto_farm_sell_price", 50000))
    await db.execute("UPDATE users SET balance = balance + ? WHERE vk_id = ?", sell_price, user_id)
    await db.execute(
        "UPDATE player_housing SET has_crypto_farm = 0, crypto_farm_installed_at = NULL WHERE user_id = ?",
        user_id
    )
    await db.execute("DELETE FROM crypto_farm WHERE user_id = ?", user_id)
    return True, f"Криптоферма продана за {sell_price} NK."


async def get_videocard_slots(user_id: int) -> int:
    housing = await get_user_housing(user_id)
    if not housing:
        return 0
    return VIDEOCARD_SLOTS.get(housing["housing_id"], 0)


async def install_videocard(user_id: int, item_id: str) -> tuple:
    housing = await get_user_housing(user_id)
    if not housing or not housing["has_crypto_farm"]:
        return False, "Криптоферма не установлена."
    inv = await db.fetchone(
        "SELECT id FROM inventory WHERE user_id = ? AND item_id = ? AND quantity > 0",
        user_id, item_id
    )
    if not inv:
        return False, "Видеокарта отсутствует в инвентаре."
    slots = await get_videocard_slots(user_id)
    current_count = await db.fetchone(
        "SELECT COUNT(*) as cnt FROM crypto_farm WHERE user_id = ?", user_id
    )
    if current_count["cnt"] >= slots:
        return False, "Нет свободных слотов для видеокарты."
    await db.execute("UPDATE inventory SET quantity = quantity - 1 WHERE id = ?", inv["id"])
    await db.execute("DELETE FROM inventory WHERE id = ? AND quantity <= 0", inv["id"])
    await db.execute(
        "INSERT INTO crypto_farm (user_id, videocard_id, installed_at) VALUES (?, ?, ?)",
        user_id, item_id, datetime.now(timezone.utc).isoformat()
    )
    return True, "Видеокарта установлена."


async def remove_videocard(user_id: int, videocard_id: str) -> tuple:
    farm_row = await db.fetchone(
        "SELECT id FROM crypto_farm WHERE user_id = ? AND videocard_id = ?", user_id, videocard_id
    )
    if not farm_row:
        return False, "Видеокарта не найдена в ферме."
    await db.execute("DELETE FROM crypto_farm WHERE id = ?", farm_row["id"])
    await add_item_to_inventory(user_id, videocard_id, 1)
    return True, "Видеокарта снята и возвращена в инвентарь."


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


async def get_garden_plots(user_id: int) -> list:
    return await db.fetchall("SELECT * FROM garden_plots WHERE user_id = ?", user_id)


async def buy_garden_plot(user_id: int, plot_number: int) -> tuple:
    housing = await get_user_housing(user_id)
    if not housing or housing["type"] != "house":
        return False, "Участки доступны только для домов."
    if plot_number == 1:
        cost = int(await get_config_value("garden_plot_1_cost", 500000))
    elif plot_number == 2:
        cost = int(await get_config_value("garden_plot_2_cost", 800000))
    else:
        return False, "Неверный номер участка."
    if await db.fetchone(
        "SELECT id FROM garden_plots WHERE user_id = ? AND plot_number = ?", user_id, plot_number
    ):
        return False, "Этот участок уже куплен."
    user = await db.fetchone("SELECT balance FROM users WHERE vk_id = ?", user_id)
    if not user or user["balance"] < cost:
        return False, "Недостаточно наличных."
    await db.execute("UPDATE users SET balance = balance - ? WHERE vk_id = ?", cost, user_id)
    await db.execute(
        "INSERT INTO garden_plots (user_id, plot_number, capacity) VALUES (?, ?, 25)",
        user_id, plot_number
    )
    return True, "Участок куплен."


async def plant_seed(user_id: int, plot_number: int, slot_number: int, seed_item_id: str) -> tuple:
    seed = await db.fetchone(
        "SELECT id, quantity FROM inventory WHERE user_id = ? AND item_id = ?", user_id, seed_item_id
    )
    if not seed or seed["quantity"] < 1:
        return False, "Нет семян."
    if await db.fetchone(
        "SELECT id FROM garden_plants WHERE user_id = ? AND plot_number = ? AND slot_number = ?",
        user_id, plot_number, slot_number
    ):
        return False, "Лунка занята."
    plant_type = SEED_ID_TO_PLANT_TYPE.get(seed_item_id)
    if not plant_type:
        item = await db.fetchone("SELECT name FROM items WHERE item_id = ?", seed_item_id)
        if not item:
            return False, "Предмет не найден."
        plant_type = item["name"].lower().replace("семена ", "")
    plant_info = await get_plant_info(plant_type)
    if not plant_info:
        return False, "Неизвестное растение."
    now = datetime.now(timezone.utc)
    water_by = now + timedelta(hours=plant_info["water_interval_hours"])
    if plant_info["type"] == "annual":
        harvest_at = now + timedelta(hours=plant_info["grow_hours"])
        is_tree = 0
    else:
        harvest_at = now + timedelta(hours=plant_info["fruit_interval_hours"])
        is_tree = 1
    await db.execute("UPDATE inventory SET quantity = quantity - 1 WHERE id = ?", seed["id"])
    await db.execute("DELETE FROM inventory WHERE id = ? AND quantity <= 0", seed["id"])
    await db.execute(
        "INSERT INTO garden_plants (user_id, plot_number, slot_number, plant_type, seed_item_id, "
        "planted_at, water_required_by, harvest_ready_at, can_harvest, is_tree) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)",
        user_id, plot_number, slot_number, plant_type, seed_item_id,
        now.isoformat(), water_by.isoformat(), harvest_at.isoformat(), is_tree
    )
    return True, f"Посажено: {plant_type}."


async def get_plant_info(plant_type: str) -> dict:
    plants = {
        "огурцы": {"type": "annual", "water_interval_hours": 1, "grow_hours": 3, "fruit_interval_hours": 6},
        "помидоры": {"type": "annual", "water_interval_hours": 1, "grow_hours": 3, "fruit_interval_hours": 6},
        "морковь": {"type": "annual", "water_interval_hours": 1, "grow_hours": 3, "fruit_interval_hours": 6},
        "земляника": {"type": "annual", "water_interval_hours": 1, "grow_hours": 3, "fruit_interval_hours": 6},
        "ежевика": {"type": "annual", "water_interval_hours": 1, "grow_hours": 3, "fruit_interval_hours": 6},
        "дыня": {"type": "annual", "water_interval_hours": 1, "grow_hours": 3, "fruit_interval_hours": 6},
        "арбуз": {"type": "annual", "water_interval_hours": 1, "grow_hours": 3, "fruit_interval_hours": 6},
        "картошка": {"type": "annual", "water_interval_hours": 1, "grow_hours": 3, "fruit_interval_hours": 6},
        "яблоко": {"type": "tree", "water_interval_hours": 2, "grow_hours": 0, "fruit_interval_hours": 6},
        "вишня": {"type": "tree", "water_interval_hours": 2, "grow_hours": 0, "fruit_interval_hours": 6},
        "груша": {"type": "tree", "water_interval_hours": 2, "grow_hours": 0, "fruit_interval_hours": 6},
        "мандарин": {"type": "tree", "water_interval_hours": 2, "grow_hours": 0, "fruit_interval_hours": 6},
    }
    return plants.get(plant_type)


async def water_plant(user_id: int, plant_id: int) -> tuple:
    plant = await db.fetchone(
        "SELECT * FROM garden_plants WHERE id = ? AND user_id = ?", plant_id, user_id
    )
    if not plant:
        return False, "Растение не найдено."
    now = datetime.now(timezone.utc)
    water_by = _parse_dt(plant["water_required_by"])
    if water_by and water_by > now:
        return False, "Поливать ещё рано."
    plant_info = await get_plant_info(plant["plant_type"])
    if not plant_info:
        return False, "Неизвестное растение."
    new_water_by = now + timedelta(hours=plant_info["water_interval_hours"])
    await db.execute(
        "UPDATE garden_plants SET water_required_by = ? WHERE id = ?",
        new_water_by.isoformat(), plant_id
    )
    return True, "Растение полито."


async def harvest_plant(user_id: int, plant_id: int) -> tuple:
    plant = await db.fetchone(
        "SELECT * FROM garden_plants WHERE id = ? AND user_id = ?", plant_id, user_id
    )
    if not plant:
        return False, "Растение не найдено."
    if plant["can_harvest"] == 0:
        return False, "Урожай ещё не созрел."
    plant_info = await get_plant_info(plant["plant_type"])
    if not plant_info:
        return False, "Неизвестное растение."
    if plant_info["type"] == "annual":
        amount = random.randint(
            int(await get_config_value("annual_yield_min", 10)),
            int(await get_config_value("annual_yield_max", 50))
        )
        await add_harvest_item(user_id, plant["plant_type"], amount)
        await db.execute("DELETE FROM garden_plants WHERE id = ?", plant_id)
        return True, f"Собрано {amount} единиц урожая."
    amount = random.randint(
        int(await get_config_value("tree_yield_min", 25)),
        int(await get_config_value("tree_yield_max", 75))
    )
    await add_harvest_item(user_id, plant["plant_type"], amount)
    now = datetime.now(timezone.utc)
    await db.execute(
        "UPDATE garden_plants SET harvest_ready_at = ? WHERE id = ?",
        (now + timedelta(hours=plant_info["fruit_interval_hours"])).isoformat(), plant_id
    )
    return True, f"Собрано {amount} единиц урожая."


async def add_harvest_item(user_id: int, plant_type: str, quantity: int) -> None:
    item_id = PLANT_TYPE_TO_HARVEST.get(plant_type)
    if not item_id:
        return
    await add_item_to_inventory(user_id, item_id, quantity)


async def chop_tree(user_id: int, plant_id: int) -> tuple:
    plant = await db.fetchone(
        "SELECT * FROM garden_plants WHERE id = ? AND user_id = ?", plant_id, user_id
    )
    if not plant or not plant["is_tree"]:
        return False, "Это не дерево."
    axe = await db.fetchone(
        "SELECT id, durability FROM inventory WHERE user_id = ? AND item_id = '1.1.28'", user_id
    )
    if not axe:
        return False, "Нужен топор для вырубки дерева."
    wood_amount = random.randint(2, 4)
    await add_item_to_inventory(user_id, "1.1.12", wood_amount)
    new_durability = (axe["durability"] or 100) - 1
    if new_durability <= 0:
        await db.execute("DELETE FROM inventory WHERE id = ?", axe["id"])
    else:
        await db.execute("UPDATE inventory SET durability = ? WHERE id = ?", new_durability, axe["id"])
    await db.execute("DELETE FROM garden_plants WHERE id = ?", plant_id)
    return True, f"Дерево вырублено, получено {wood_amount} дерева."