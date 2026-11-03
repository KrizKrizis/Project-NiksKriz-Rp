# services/nkvito_service.py
import json
from datetime import datetime, timezone, timedelta
from db.database import db

LISTING_FEES = {1: 1500, 2: 3000, 3: 5000, 4: 7500, 5: 10000}
PAGE_SIZE = 10


async def get_active_listings(page: int = 1) -> list:
    await check_expired_listings()
    offset = (page - 1) * PAGE_SIZE
    return await db.fetchall(
        "SELECT l.id, l.seller_id, l.item_id, l.price, l.expires_at, i.name AS item_name, "
        "u.game_id AS seller_game_id FROM nkvito_listings l "
        "JOIN items i ON l.item_id = i.item_id "
        "JOIN users u ON l.seller_id = u.vk_id "
        "WHERE l.status = 'active' ORDER BY l.created_at DESC LIMIT ? OFFSET ?",
        PAGE_SIZE, offset
    )


async def get_user_listings(user_id: int) -> list:
    return await db.fetchall(
        "SELECT l.id, l.item_id, l.price, l.expires_at, i.name AS item_name "
        "FROM nkvito_listings l JOIN items i ON l.item_id = i.item_id "
        "WHERE l.seller_id = ? AND l.status = 'active' ORDER BY l.created_at DESC",
        user_id
    )


async def get_user_inventory_items(user_id: int) -> list:
    return await db.fetchall(
        "SELECT inv.item_id, i.name, inv.quantity FROM inventory inv "
        "JOIN items i ON inv.item_id = i.item_id WHERE inv.user_id = ? ORDER BY i.name",
        user_id
    )


async def _add_to_inventory(user_id: int, item_id: str, quantity: int = 1) -> None:
    existing = await db.fetchone(
        "SELECT id, quantity FROM inventory WHERE user_id = ? AND item_id = ?",
        user_id, item_id
    )
    if existing:
        await db.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", quantity, existing["id"])
    else:
        await db.execute(
            "INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)",
            user_id, item_id, quantity
        )


async def create_listing(seller_id: int, item_id: str, price: int, duration_days: int) -> tuple:
    if duration_days not in LISTING_FEES:
        return False, "Неверный срок размещения."
    item = await db.fetchone(
        "SELECT id, quantity FROM inventory WHERE user_id = ? AND item_id = ?",
        seller_id, item_id
    )
    if not item or item["quantity"] < 1:
        return False, "Предмет отсутствует в инвентаре."
    user = await db.fetchone("SELECT bank_checking FROM users WHERE vk_id = ?", seller_id)
    fee = LISTING_FEES[duration_days]
    if not user or user["bank_checking"] < fee:
        return False, f"Недостаточно средств для оплаты ({fee} NK)."
    await db.execute("UPDATE users SET bank_checking = bank_checking - ? WHERE vk_id = ?", fee, seller_id)
    await db.execute(
        "UPDATE system_accounts SET balance = balance + ? WHERE account_name = 'commission'", fee
    )
    await db.execute("UPDATE inventory SET quantity = quantity - 1 WHERE id = ?", item["id"])
    await db.execute("DELETE FROM inventory WHERE id = ? AND quantity <= 0", item["id"])
    now = datetime.now(timezone.utc)
    await db.execute(
        "INSERT INTO nkvito_listings (seller_id, item_id, price, listing_duration_days, created_at, expires_at, status) "
        "VALUES (?, ?, ?, ?, ?, ?, 'active')",
        seller_id, item_id, price, duration_days, now.isoformat(),
        (now + timedelta(days=duration_days)).isoformat()
    )
    return True, "Лот создан."


async def buy_listing(listing_id: int, buyer_id: int) -> tuple:
    listing = await db.fetchone("SELECT * FROM nkvito_listings WHERE id = ?", listing_id)
    if not listing or listing["status"] != "active":
        return False, "Лот недоступен."
    if listing["seller_id"] == buyer_id:
        return False, "Нельзя купить свой лот."
    if datetime.now(timezone.utc) > datetime.fromisoformat(listing["expires_at"]):
        await cancel_listing(listing_id, listing["seller_id"])
        return False, "Срок лота истёк."
    buyer = await db.fetchone("SELECT bank_checking FROM users WHERE vk_id = ?", buyer_id)
    if not buyer or buyer["bank_checking"] < listing["price"]:
        return False, "Недостаточно средств на основном счёте."

    await db.execute(
        "UPDATE users SET bank_checking = bank_checking - ? WHERE vk_id = ?",
        listing["price"], buyer_id
    )
    await db.execute(
        "UPDATE users SET bank_checking = bank_checking + ? WHERE vk_id = ?",
        listing["price"], listing["seller_id"]
    )
    await _add_to_inventory(buyer_id, listing["item_id"], 1)
    await db.execute("UPDATE nkvito_listings SET status = 'sold' WHERE id = ?", listing_id)
    await db.execute(
        "INSERT INTO transactions (sender_id, receiver_id, amount, currency, transaction_type) "
        "VALUES (?, ?, ?, 'NK', 'nkvito_purchase')",
        buyer_id, listing["seller_id"], listing["price"]
    )
    return True, f"Вы купили лот за {listing['price']} NK."


async def cancel_listing(listing_id: int, user_id: int) -> tuple:
    listing = await db.fetchone("SELECT * FROM nkvito_listings WHERE id = ?", listing_id)
    if not listing or listing["status"] != "active":
        return False, "Лот не найден или неактивен."
    if listing["seller_id"] != user_id:
        if datetime.now(timezone.utc) < datetime.fromisoformat(listing["expires_at"]):
            return False, "Недостаточно прав."
    await _add_to_inventory(listing["seller_id"], listing["item_id"], 1)
    new_status = "cancelled" if listing["seller_id"] == user_id else "expired"
    await db.execute("UPDATE nkvito_listings SET status = ? WHERE id = ?", new_status, listing_id)
    return True, "Лот отменён, предмет возвращён."


async def check_expired_listings() -> None:
    now = datetime.now(timezone.utc).isoformat()
    expired = await db.fetchall(
        "SELECT id, seller_id, item_id FROM nkvito_listings WHERE status = 'active' AND expires_at < ?",
        now
    )
    for lot in expired:
        await _add_to_inventory(lot["seller_id"], lot["item_id"], 1)
        await db.execute("UPDATE nkvito_listings SET status = 'expired' WHERE id = ?", lot["id"])