# services/auction_service.py
from datetime import datetime, timezone, timedelta
from db.database import db

MIN_BID_STEP = 15000
AUCTION_DURATION_MINUTES = 10
START_PRICE = 500000
CASINO_START_PRICE = 2000000


def _get_start_price(biz) -> int:
    if biz["type"] == "auction_casino":
        return CASINO_START_PRICE
    return START_PRICE


async def place_bid(user_id: int, business_id: str, amount: int) -> tuple:
    biz = await db.fetchone("SELECT * FROM businesses WHERE business_id = ?", business_id)
    if not biz or biz["owner_id"] is not None:
        return False, "Бизнес недоступен для ставок."
    if biz["type"] not in ("auction_standard", "auction_casino"):
        return False, "Этот бизнес не участвует в аукционе."

    current_bid = biz["current_bid_amount"] or _get_start_price(biz)
    if amount < current_bid + MIN_BID_STEP:
        return False, f"Минимальная ставка: {current_bid + MIN_BID_STEP} NK."

    user = await db.fetchone("SELECT bank_checking FROM users WHERE vk_id = ?", user_id)
    if not user or user["bank_checking"] < amount:
        return False, "Недостаточно средств на основном счёте."

    if biz["current_bid_user_id"]:
        await db.execute(
            "UPDATE users SET bank_checking = bank_checking + ? WHERE vk_id = ?",
            biz["current_bid_amount"], biz["current_bid_user_id"]
        )

    await db.execute("UPDATE users SET bank_checking = bank_checking - ? WHERE vk_id = ?", amount, user_id)
    await db.execute(
        "UPDATE businesses SET current_bid_user_id = ?, current_bid_amount = ?, last_bid_time = ? WHERE business_id = ?",
        user_id, amount, datetime.now(timezone.utc).isoformat(), business_id
    )
    await db.execute(
        "INSERT INTO auction_bids (business_id, user_id, amount) VALUES (?, ?, ?)",
        business_id, user_id, amount
    )
    return True, "Ставка принята."


async def finish_auction(business_id: str) -> tuple:
    biz = await db.fetchone("SELECT * FROM businesses WHERE business_id = ?", business_id)
    if not biz or biz["owner_id"] is not None:
        return False, "Бизнес уже имеет владельца."
    if biz["current_bid_user_id"] is None:
        return False, "На этот бизнес ещё нет ставок."
    last = datetime.fromisoformat(biz["last_bid_time"])
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - last < timedelta(minutes=AUCTION_DURATION_MINUTES):
        return False, "Аукцион ещё идёт."

    winner_id = biz["current_bid_user_id"]
    winning_bid = biz["current_bid_amount"]

    if biz["auction_owner_id"]:
        await db.execute(
            "UPDATE users SET bank_checking = bank_checking + ? WHERE vk_id = ?",
            winning_bid, biz["auction_owner_id"]
        )
    else:
        await db.execute(
            "UPDATE system_accounts SET balance = balance + ? WHERE account_name = 'commission'",
            winning_bid
        )

    await db.execute(
        "UPDATE businesses SET owner_id = ?, is_on_auction = 0, auction_start_time = NULL, "
        "auction_end_time = NULL, auction_owner_id = NULL, current_bid_user_id = NULL, "
        "current_bid_amount = NULL, last_bid_time = NULL WHERE business_id = ?",
        winner_id, business_id
    )
    await db.execute("DELETE FROM auction_bids WHERE business_id = ?", business_id)
    return True, f"Бизнес передан игроку {winner_id}."


async def check_and_finish_auctions() -> None:
    rows = await db.fetchall(
        "SELECT business_id FROM businesses WHERE owner_id IS NULL "
        "AND current_bid_user_id IS NOT NULL AND last_bid_time IS NOT NULL"
    )
    for row in rows:
        biz = await db.fetchone("SELECT * FROM businesses WHERE business_id = ?", row["business_id"])
        if not biz:
            continue
        last = datetime.fromisoformat(biz["last_bid_time"])
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - last >= timedelta(minutes=AUCTION_DURATION_MINUTES):
            await finish_auction(row["business_id"])


async def get_auction_businesses() -> list:
    rows = await db.fetchall(
        "SELECT b.*, u.first_name AS owner_first_name, u.last_name AS owner_last_name "
        "FROM businesses b LEFT JOIN users u ON b.owner_id = u.vk_id "
        "WHERE b.type IN ('auction_standard','auction_casino') ORDER BY b.business_id"
    )
    result = []
    for row in rows:
        biz = dict(row)
        if biz["owner_id"] is not None:
            biz["status_text"] = f"Владелец: {biz.get('owner_first_name','')} {biz.get('owner_last_name','')}".strip()
        elif biz["is_on_auction"] and biz["auction_owner_id"]:
            seller = await db.fetchone(
                "SELECT first_name, last_name FROM users WHERE vk_id = ?", biz["auction_owner_id"]
            )
            biz["status_text"] = f"Выставлен игроком: {seller['first_name']} {seller['last_name']}" if seller else "Выставлен игроком"
        else:
            biz["status_text"] = "Выставлено государством"
        result.append(biz)
    return result