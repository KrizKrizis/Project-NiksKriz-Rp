# services/shop_service.py
# Бизнес-логика магазина: покупка предметов, скупщик, криптобиржа.
import json
import logging
import random
from datetime import datetime, timezone, timedelta

from db.database import db

logger = logging.getLogger(__name__)

# Типы предметов магазина (соответствуют типу 'resource' из db/ids.py)
SHOP_TYPE_ALIASES = {
    "videocard": ("videocard",),
    "tool": ("tool",),
    "harvest": ("harvest",),
    "resource": ("resource",),
}


async def get_config_value(key: str, default=None):
    row = await db.fetchone("SELECT value FROM config WHERE key = ?", key)
    if not row:
        return default
    return row["value"]


async def get_items_by_type(item_type: str) -> list:
    """Возвращает предметы из каталога items по типу."""
    types = SHOP_TYPE_ALIASES.get(item_type, (item_type,))
    placeholders = ",".join("?" for _ in types)
    rows = await db.fetchall(
        f"SELECT item_id, name, type, base_price, stackable FROM items WHERE type IN ({placeholders})",
        *types
    )
    return [dict(r) for r in rows]


async def buy_item(user_id: int, item_id: str, quantity: int = 1) -> tuple:
    """Покупка предмета в магазине за наличные (balance)."""
    item = await db.fetchone("SELECT * FROM items WHERE item_id = ?", item_id)
    if not item:
        return False, "Предмет не найден."
    cost = int(item["base_price"]) * quantity

    user = await db.fetchone("SELECT balance FROM users WHERE vk_id = ?", user_id)
    if not user or user["balance"] < cost:
        return False, "Недостаточно наличных."

    await db.execute("UPDATE users SET balance = balance - ? WHERE vk_id = ?", cost, user_id)

    existing = await db.fetchone(
        "SELECT id FROM inventory WHERE user_id = ? AND item_id = ?", user_id, item_id
    )
    if existing and item["stackable"]:
        await db.execute(
            "UPDATE inventory SET quantity = quantity + ? WHERE id = ?", quantity, existing["id"]
        )
    else:
        for _ in range(quantity):
            await db.execute(
                "INSERT INTO inventory (user_id, item_id, quantity, durability) VALUES (?, ?, 1, 100)",
                user_id, item_id
            )

    await db.execute(
        "INSERT INTO transactions (sender_id, receiver_id, amount, currency, transaction_type, details) "
        "VALUES (?, NULL, ?, 'NK', 'shop_purchase', ?)",
        user_id, cost, json.dumps({"item_id": item_id, "quantity": quantity}, ensure_ascii=False)
    )
    return True, f"Куплено: {item['name']} x{quantity} за {cost} NK."


async def _count_user_item(user_id: int, item_id: str) -> int:
    rows = await db.fetchall(
        "SELECT COALESCE(SUM(quantity), 0) as total FROM inventory WHERE user_id = ? AND item_id = ?",
        user_id, item_id
    )
    return rows[0]["total"] if rows else 0


async def _remove_from_inventory(user_id: int, item_id: str, quantity: int) -> bool:
    rows = await db.fetchall(
        "SELECT id, quantity FROM inventory WHERE user_id = ? AND item_id = ? ORDER BY id",
        user_id, item_id
    )
    available = sum(r["quantity"] for r in rows)
    if available < quantity:
        return False
    remaining = quantity
    for r in rows:
        take = min(r["quantity"], remaining)
        await db.execute(
            "UPDATE inventory SET quantity = quantity - ? WHERE id = ?", take, r["id"]
        )
        await db.execute("DELETE FROM inventory WHERE id = ? AND quantity <= 0", r["id"])
        remaining -= take
        if remaining <= 0:
            break
    return True


async def sell_harvest_to_shop(user_id: int, item_id: str, quantity: int) -> tuple:
    """Продажа урожая/ресурса магазину по недельному множителю скупщика."""
    if quantity <= 0:
        return False, "Количество должно быть больше нуля."
    item = await db.fetchone("SELECT * FROM items WHERE item_id = ?", item_id)
    if not item:
        return False, "Предмет не найден."
    if item["type"] not in ("harvest", "resource"):
        return False, "Этот предмет нельзя продать скупщику."

    have = await _count_user_item(user_id, item_id)
    if have < quantity:
        return False, f"У вас есть только {have} шт."

    multiplier = float(await get_config_value("weekly_shop_purchase_multiplier", 5))
    income = int(int(item["base_price"]) * quantity / max(multiplier, 1))

    if not await _remove_from_inventory(user_id, item_id, quantity):
        return False, "Не удалось списать предметы."

    await db.execute("UPDATE users SET balance = balance + ? WHERE vk_id = ?", income, user_id)
    await db.execute(
        "INSERT INTO transactions (sender_id, receiver_id, amount, currency, transaction_type, details) "
        "VALUES (NULL, ?, ?, 'NK', 'shop_sell', ?)",
        user_id, income, json.dumps({"item_id": item_id, "quantity": quantity}, ensure_ascii=False)
    )
    return True, f"Продано {quantity} шт. за {income} NK."


async def sell_to_private_buyer(user_id: int, item_id: str, quantity: int) -> tuple:
    """Продажа частному лицу — по базовой цене без множителя скупщика."""
    if quantity <= 0:
        return False, "Количество должно быть больше нуля."
    item = await db.fetchone("SELECT * FROM items WHERE item_id = ?", item_id)
    if not item:
        return False, "Предмет не найден."
    if item["type"] not in ("harvest", "resource"):
        return False, "Этот предмет нельзя продать частному лицу."

    have = await _count_user_item(user_id, item_id)
    if have < quantity:
        return False, f"У вас есть только {have} шт."

    variation = float(await get_config_value("exchange_rate_variation_percent", 2)) / 100
    price_factor = 1 + random.uniform(-variation, variation)
    income = max(1, int(int(item["base_price"]) * quantity * price_factor))

    if not await _remove_from_inventory(user_id, item_id, quantity):
        return False, "Не удалось списать предметы."

    await db.execute("UPDATE users SET balance = balance + ? WHERE vk_id = ?", income, user_id)
    await db.execute(
        "INSERT INTO transactions (sender_id, receiver_id, amount, currency, transaction_type, details) "
        "VALUES (NULL, ?, ?, 'NK', 'private_sale', ?)",
        user_id, income, json.dumps({"item_id": item_id, "quantity": quantity}, ensure_ascii=False)
    )
    return True, f"Частный покупатель заплатил {income} NK за {quantity} шт."


async def exchange_crypto_to_nk(user_id: int, amount: float) -> tuple:
    """Мгновенный обмен криптовалюты на NK по курсу из config."""
    if amount <= 0:
        return False, "Сумма должна быть больше нуля."
    user = await db.fetchone("SELECT crypto_balance FROM users WHERE vk_id = ?", user_id)
    if not user or user["crypto_balance"] < amount:
        return False, "Недостаточно криптовалюты."

    rate = float(await get_config_value("crypto_to_nk_rate", 10))
    variation = float(await get_config_value("exchange_rate_variation_percent", 2)) / 100
    effective_rate = rate * (1 + random.uniform(-variation, variation))
    nk_amount = int(amount * effective_rate)

    await db.execute("UPDATE users SET crypto_balance = crypto_balance - ? WHERE vk_id = ?", amount, user_id)
    await db.execute("UPDATE users SET balance = balance + ? WHERE vk_id = ?", nk_amount, user_id)
    await db.execute(
        "INSERT INTO transactions (sender_id, receiver_id, amount, currency, transaction_type, details) "
        "VALUES (?, NULL, ?, 'NK', 'crypto_instant_exchange', ?)",
        user_id, nk_amount, json.dumps({"crypto": amount, "rate": round(effective_rate, 3)}, ensure_ascii=False)
    )
    return True, f"Обменяно {amount:.2f} крипты на {nk_amount} NK (курс {effective_rate:.2f})."


async def list_on_exchange(user_id: int, amount: float) -> tuple:
    """Выставить криптовалюту на биржу — продажа через 24 часа по среднему курсу."""
    if amount <= 0:
        return False, "Сумма должна быть больше нуля."
    user = await db.fetchone("SELECT crypto_balance FROM users WHERE vk_id = ?", user_id)
    if not user or user["crypto_balance"] < amount:
        return False, "Недостаточно криптовалюты."

    await db.execute("UPDATE users SET crypto_balance = crypto_balance - ? WHERE vk_id = ?", amount, user_id)
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    await db.execute(
        "INSERT INTO exchange_orders (user_id, amount, status, created_at, expires_at) "
        "VALUES (?, ?, 'pending', ?, ?)",
        user_id, amount, datetime.now(timezone.utc).isoformat(), expires_at
    )
    return True, f"Ордер на {amount:.2f} крипты выставлен. Исполнение через 24 часа."


async def process_exchange_pending():
    """Scheduler-задача: исполнить ордера биржи, у которых истёк срок (24 часа)."""
    try:
        now = datetime.now(timezone.utc).isoformat()
        orders = await db.fetchall(
            "SELECT * FROM exchange_orders WHERE status = 'pending' AND expires_at <= ?", now
        )
        if not orders:
            return
        rate = float(await get_config_value("crypto_to_nk_rate", 10))
        variation = float(await get_config_value("exchange_rate_variation_percent", 2)) / 100
        for order in orders:
            effective_rate = rate * (1 + random.uniform(-variation, variation))
            nk_amount = int(order["amount"] * effective_rate)
            await db.execute("UPDATE users SET balance = balance + ? WHERE vk_id = ?", nk_amount, order["user_id"])
            await db.execute(
                "UPDATE exchange_orders SET status = 'completed', completed_at = ? WHERE id = ?",
                now, order["id"]
            )
            await db.execute(
                "INSERT INTO transactions (receiver_id, amount, currency, transaction_type, details) "
                "VALUES (?, ?, 'NK', 'crypto_exchange_order', ?)",
                order["user_id"], nk_amount,
                json.dumps({"order_id": order["id"], "crypto": order["amount"],
                            "rate": round(effective_rate, 3)}, ensure_ascii=False)
            )
            try:
                await bot.send_message(  # noqa: F821 (builtins.bot)
                    order["user_id"],
                    f"🏦 Биржа: ваш ордер #{order['id']} исполнен. Получено {nk_amount} NK."
                )
            except Exception as e:
                logger.warning(f"exchange notify user {order['user_id']}: {e}")
        logger.info(f"exchange_pending_job: исполнено ордеров: {len(orders)}")
    except Exception as e:
        logger.error(f"process_exchange_pending: {e}", exc_info=True)
