# services/business_service.py
import random
import json
from datetime import datetime, timezone, timedelta
from db.database import db

DEFAULT_MANAGER_SALARY = 1000
MANAGER_TAX_RATE = 0.10
DIRECTOR_ELECTION_INTERVAL_DAYS = 7
DIRECTOR_MIN_REPUTATION = 80
DIRECTOR_REMOVE_THRESHOLD = 50


async def get_business_by_id(business_id: str) -> dict:
    return await db.fetchone("SELECT * FROM businesses WHERE business_id = ?", business_id)


async def get_user_businesses(user_id: int) -> list:
    return await db.fetchall("SELECT * FROM businesses WHERE owner_id = ?", user_id)


async def get_business_count(user_id: int) -> int:
    row = await db.fetchone("SELECT COUNT(*) as cnt FROM businesses WHERE owner_id = ?", user_id)
    return row["cnt"] if row else 0


async def get_admin_category(user_id: int) -> int:
    from utils.permissions import get_admin_info
    info = await get_admin_info(user_id)
    return info["category"] if info else 0


async def buy_shop_business(user_id: int, business_id: str) -> tuple:
    biz = await get_business_by_id(business_id)
    if not biz or biz["type"] != "shop":
        return False, "Бизнес не найден или не является магазинным."
    if biz["owner_id"] is not None:
        return False, "Бизнес уже имеет владельца."

    businesses = await get_user_businesses(user_id)
    admin_cat = await get_admin_category(user_id)

    if admin_cat == 4:
        if len(businesses) >= 3:
            return False, "Лимит: не более 3 бизнесов."
    else:
        shop_count = sum(1 for b in businesses if b["type"] == "shop")
        if shop_count >= 1:
            return False, "У вас уже есть магазинный бизнес."

    user = await db.fetchone("SELECT bank_checking FROM users WHERE vk_id = ?", user_id)
    if not user or user["bank_checking"] < biz["shop_price"]:
        return False, "Недостаточно средств на основном счёте."

    await db.execute(
        "UPDATE users SET bank_checking = bank_checking - ? WHERE vk_id = ?",
        biz["shop_price"], user_id
    )
    await db.execute(
        "UPDATE businesses SET owner_id = ? WHERE business_id = ?",
        user_id, business_id
    )
    await db.execute(
        "UPDATE system_accounts SET balance = balance + ? WHERE account_name = 'commission'",
        biz["shop_price"]
    )
    return True, f"Вы купили {biz['name']}."


async def sell_business_to_state(user_id: int, business_id: str) -> tuple:
    biz = await get_business_by_id(business_id)
    if not biz or biz["owner_id"] != user_id:
        return False, "Бизнес не найден или не принадлежит вам."

    if biz["type"] == "shop":
        base_price = biz["shop_price"]
    elif biz["type"] == "auction_casino":
        base_price = 2_000_000
    else:
        base_price = 500_000

    sell_price = int(base_price * 0.6)

    commission_acc = await db.fetchone(
        "SELECT balance FROM system_accounts WHERE account_name = 'commission'"
    )
    if not commission_acc or commission_acc["balance"] < sell_price:
        return False, "Недостаточно средств на комиссионном счёте."

    await db.execute(
        "UPDATE system_accounts SET balance = balance - ? WHERE account_name = 'commission'",
        sell_price
    )
    await db.execute(
        "UPDATE users SET bank_checking = bank_checking + ? WHERE vk_id = ?",
        sell_price, user_id
    )
    await db.execute(
        "UPDATE businesses SET owner_id = NULL, business_balance = 0 WHERE business_id = ?",
        business_id
    )
    await db.execute("DELETE FROM business_managers WHERE business_id = ?", business_id)
    return True, f"Бизнес продан за {sell_price} NK."


async def list_business_for_auction(user_id: int, business_id: str) -> tuple:
    biz = await get_business_by_id(business_id)
    if not biz or biz["owner_id"] != user_id:
        return False, "Бизнес не найден или не принадлежит вам."
    if biz["type"] == "shop":
        return False, "Магазинные бизнесы нельзя выставить на аукцион."
    if biz["is_on_auction"]:
        return False, "Бизнес уже выставлен на аукцион."
    user = await db.fetchone("SELECT bank_checking FROM users WHERE vk_id = ?", user_id)
    if not user or user["bank_checking"] < 50000:
        return False, "Недостаточно средств для налога (50000 NK)."
    await db.execute(
        "UPDATE users SET bank_checking = bank_checking - ? WHERE vk_id = ?", 50000, user_id
    )
    await db.execute(
        "UPDATE system_accounts SET balance = balance + ? WHERE account_name = 'commission'", 50000
    )
    start_price = 2_000_000 if biz["type"] == "auction_casino" else 500_000
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "UPDATE businesses SET owner_id = NULL, is_on_auction = 1, auction_start_time = ?, "
        "auction_end_time = NULL, auction_owner_id = ?, current_bid_user_id = NULL, "
        "current_bid_amount = ?, last_bid_time = NULL WHERE business_id = ?",
        now, user_id, start_price, business_id
    )
    await db.execute("DELETE FROM auction_bids WHERE business_id = ?", business_id)
    return True, "Бизнес выставлен на аукцион."


async def remove_business_from_auction(user_id: int, business_id: str) -> tuple:
    biz = await get_business_by_id(business_id)
    if not biz or not biz["is_on_auction"] or biz["auction_owner_id"] != user_id:
        return False, "Бизнес не находится на аукционе."
    if biz["current_bid_user_id"] is not None:
        return False, "Нельзя снять бизнес, пока есть ставки."
    await db.execute(
        "UPDATE businesses SET owner_id = ?, is_on_auction = 0, auction_start_time = NULL, "
        "auction_end_time = NULL, auction_owner_id = NULL, current_bid_user_id = NULL, "
        "current_bid_amount = NULL, last_bid_time = NULL WHERE business_id = ?",
        user_id, business_id
    )
    await db.execute("DELETE FROM auction_bids WHERE business_id = ?", business_id)
    return True, "Бизнес снят с аукциона."


async def collect_business_income(business_id: str) -> None:
    biz = await get_business_by_id(business_id)
    if not biz or biz["owner_id"] is None:
        return
    income = random.randint(biz["income_min"], biz["income_max"])
    if await db.fetchone(
        "SELECT * FROM business_managers WHERE business_id = ? AND manager_type = 'player' AND status = 'active'",
        business_id
    ):
        income = int(income * 1.1)
    await db.execute(
        "UPDATE businesses SET business_balance = business_balance + ? WHERE business_id = ?",
        income, business_id
    )


async def pay_business_products(business_id: str) -> bool:
    biz = await get_business_by_id(business_id)
    if not biz or biz["product_cost"] <= 0:
        return True
    if biz["business_balance"] < biz["product_cost"]:
        return False
    await db.execute(
        "UPDATE businesses SET business_balance = business_balance - ? WHERE business_id = ?",
        biz["product_cost"], business_id
    )
    return True


async def pay_business_tax(business_id: str) -> bool:
    biz = await get_business_by_id(business_id)
    if not biz or biz["tax_amount"] <= 0:
        return True
    if biz["business_balance"] < biz["tax_amount"]:
        return False
    await db.execute(
        "UPDATE businesses SET business_balance = business_balance - ? WHERE business_id = ?",
        biz["tax_amount"], business_id
    )
    await db.execute(
        "UPDATE system_accounts SET balance = balance + ? WHERE account_name = 'commission'",
        biz["tax_amount"]
    )
    return True


async def withdraw_business_balance(user_id: int, business_id: str) -> bool:
    biz = await get_business_by_id(business_id)
    if not biz or biz["owner_id"] != user_id:
        return False
    amount = biz["business_balance"]
    if amount <= 0:
        return False
    await db.execute("UPDATE businesses SET business_balance = 0 WHERE business_id = ?", business_id)
    await db.execute(
        "UPDATE users SET bank_checking = bank_checking + ? WHERE vk_id = ?", amount, user_id
    )
    return True


async def set_bank_commission(business_id: str, commission: float) -> bool:
    if not 0 <= commission <= 0.05:
        return False
    biz = await get_business_by_id(business_id)
    if not biz or biz["special_income_type"] != "bank_commission":
        return False
    await db.execute(
        "UPDATE businesses SET commission_rate = ? WHERE business_id = ?", commission, business_id
    )
    return True


async def hire_manager(business_id: str, manager_user_id: int, salary: int = DEFAULT_MANAGER_SALARY) -> tuple:
    biz = await get_business_by_id(business_id)
    if not biz:
        return False, "Бизнес не найден."
    if biz["owner_id"] is None:
        return False, "У бизнеса нет владельца."
    if biz["type"] not in ("auction_standard", "auction_casino"):
        return False, "Менеджеры доступны только для аукционных бизнесов."
    if await db.fetchone(
        "SELECT id FROM business_managers WHERE business_id = ? AND manager_user_id = ? AND status = 'active'",
        business_id, manager_user_id
    ):
        return False, "Игрок уже нанят менеджером в этом бизнесе."
    await db.execute(
        "INSERT INTO business_managers (business_id, manager_type, manager_user_id, salary, status) "
        "VALUES (?, 'player', ?, ?, 'active')",
        business_id, manager_user_id, salary
    )
    if not await db.fetchone("SELECT user_id FROM manager_reputation WHERE user_id = ?", manager_user_id):
        await db.execute(
            "INSERT INTO manager_reputation (user_id, reputation, boss_reputation) VALUES (?, 50, 50)",
            manager_user_id
        )
    return True, "Менеджер нанят."


async def fire_manager(manager_id: int) -> bool:
    if not await db.fetchone("SELECT id FROM business_managers WHERE id = ?", manager_id):
        return False
    await db.execute("UPDATE business_managers SET status = 'fired' WHERE id = ?", manager_id)
    return True


async def get_managers_for_business(business_id: str) -> list:
    return await db.fetchall(
        "SELECT bm.*, u.first_name, u.last_name FROM business_managers bm "
        "JOIN users u ON bm.manager_user_id = u.vk_id "
        "WHERE bm.business_id = ? AND bm.status = 'active'",
        business_id
    )


async def update_manager_reputation(manager_user_id: int, delta: int) -> None:
    await db.execute(
        "UPDATE manager_reputation SET reputation = MIN(100, MAX(0, reputation + ?)) WHERE user_id = ?",
        delta, manager_user_id
    )


async def update_boss_reputation(boss_user_id: int, delta: int) -> None:
    await db.execute(
        "UPDATE manager_reputation SET boss_reputation = MIN(100, MAX(0, boss_reputation + ?)) WHERE user_id = ?",
        delta, boss_user_id
    )


async def pay_manager_salary(manager_id: int) -> tuple:
    manager = await db.fetchone(
        "SELECT * FROM business_managers WHERE id = ? AND status = 'active'", manager_id
    )
    if not manager:
        return False, "Менеджер не найден."
    biz = await get_business_by_id(manager["business_id"])
    if not biz or biz["business_balance"] < manager["salary"]:
        return False, "Недостаточно средств на счету бизнеса."
    await db.execute(
        "UPDATE businesses SET business_balance = business_balance - ? WHERE business_id = ?",
        manager["salary"], manager["business_id"]
    )
    await db.execute(
        "UPDATE users SET balance = balance + ? WHERE vk_id = ?",
        manager["salary"], manager["manager_user_id"]
    )
    firm = await db.fetchone(
        "SELECT * FROM businesses WHERE special_income_type = 'manager_firm' AND owner_id IS NOT NULL"
    )
    if firm:
        await db.execute(
            "UPDATE businesses SET business_balance = business_balance + ? WHERE business_id = ?",
            int(manager["salary"] * MANAGER_TAX_RATE), firm["business_id"]
        )
    return True, f"Зарплата {manager['salary']} NK выплачена."


async def process_all_manager_salaries() -> None:
    for m in await db.fetchall("SELECT id FROM business_managers WHERE status = 'active'"):
        await pay_manager_salary(m["id"])


async def get_manager_firm() -> dict:
    return await db.fetchone("SELECT * FROM businesses WHERE special_income_type = 'manager_firm'")


async def get_director_id() -> int:
    row = await db.fetchone("SELECT user_id FROM user_states WHERE state = 'firm_director'")
    return row["user_id"] if row else None


async def elect_director() -> None:
    firm = await get_manager_firm()
    if not firm:
        return
    candidates = await db.fetchall(
        "SELECT user_id, reputation FROM manager_reputation WHERE reputation >= ? "
        "ORDER BY reputation DESC LIMIT 3",
        DIRECTOR_MIN_REPUTATION
    )
    if not candidates:
        return
    await db.execute(
        "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (0, 'firm_election_candidates', ?)",
        json.dumps([c["user_id"] for c in candidates])
    )
    await db.execute("DELETE FROM director_elections")


async def vote_for_director(voter_id: int, candidate_id: int) -> tuple:
    if not await db.fetchone(
        "SELECT id FROM business_managers WHERE manager_user_id = ? AND status = 'active'", voter_id
    ):
        return False, "Голосовать могут только менеджеры."
    candidates_row = await db.fetchone(
        "SELECT data FROM user_states WHERE state = 'firm_election_candidates'"
    )
    if not candidates_row:
        return False, "Голосование не активно."
    if candidate_id not in json.loads(candidates_row["data"]):
        return False, "Кандидат не найден."
    if candidate_id == voter_id:
        return False, "Нельзя голосовать за себя."
    await db.execute(
        "INSERT OR REPLACE INTO director_elections (candidate_id, voter_id, voted_at) "
        "VALUES (?, ?, datetime('now'))",
        candidate_id, voter_id
    )
    return True, "Голос принят."


async def finish_election() -> None:
    candidates_row = await db.fetchone(
        "SELECT data FROM user_states WHERE state = 'firm_election_candidates'"
    )
    if not candidates_row:
        return
    votes = await db.fetchall(
        "SELECT candidate_id, COUNT(*) as cnt FROM director_elections "
        "GROUP BY candidate_id ORDER BY cnt DESC"
    )
    if not votes:
        return
    await db.execute(
        "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'firm_director', ?)",
        votes[0]["candidate_id"], json.dumps({"appointed_at": datetime.now(timezone.utc).isoformat()})
    )
    await db.execute("DELETE FROM director_elections")
    await db.execute("DELETE FROM user_states WHERE state = 'firm_election_candidates'")


async def maybe_elect_director() -> None:
    await finish_election()
    row = await db.fetchone("SELECT data FROM user_states WHERE state = 'firm_director'")
    if not row or not row["data"]:
        await elect_director()
        return
    try:
        appointed_at = json.loads(row["data"]).get("appointed_at")
        if not appointed_at:
            await elect_director()
            return
        dt = datetime.fromisoformat(appointed_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - dt >= timedelta(days=DIRECTOR_ELECTION_INTERVAL_DAYS):
            await elect_director()
    except Exception:
        await elect_director()


async def remove_director_if_bad() -> None:
    director_id = await get_director_id()
    if not director_id:
        return
    rep = await db.fetchone(
        "SELECT reputation FROM manager_reputation WHERE user_id = ?", director_id
    )
    if rep and rep["reputation"] < DIRECTOR_REMOVE_THRESHOLD:
        await db.execute("DELETE FROM user_states WHERE state = 'firm_director'")
        await update_manager_reputation(director_id, -rep["reputation"])
        await elect_director()


async def complaint_on_manager(manager_id: int, reason: str) -> None:
    await db.execute(
        "INSERT INTO admin_log (admin_id, action, details) VALUES (?, 'complaint', ?)",
        manager_id, reason
    )


async def collect_all_auction_incomes() -> None:
    for b in await db.fetchall(
        "SELECT business_id FROM businesses WHERE type IN ('auction_standard','auction_casino') AND owner_id IS NOT NULL"
    ):
        await collect_business_income(b["business_id"])


async def collect_all_shop_incomes() -> None:
    for b in await db.fetchall(
        "SELECT business_id FROM businesses WHERE type = 'shop' AND owner_id IS NOT NULL"
    ):
        await collect_business_income(b["business_id"])


async def pay_all_products() -> None:
    for b in await db.fetchall(
        "SELECT business_id FROM businesses WHERE product_cost > 0 AND owner_id IS NOT NULL"
    ):
        await pay_business_products(b["business_id"])


async def pay_all_taxes() -> None:
    for b in await db.fetchall(
        "SELECT business_id FROM businesses WHERE tax_amount > 0 AND owner_id IS NOT NULL"
    ):
        await pay_business_tax(b["business_id"])


async def manager_salaries_job() -> None:
    await process_all_manager_salaries()


async def director_election_job() -> None:
    await maybe_elect_director()
    await remove_director_if_bad()