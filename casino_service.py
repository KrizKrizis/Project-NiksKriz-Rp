# services/casino_service.py
import random
import json
from datetime import datetime, timezone
from db.database import db


async def buy_chips(user_id: int, amount_nk: int) -> tuple:
    user = await db.fetchone("SELECT balance FROM users WHERE vk_id = ?", user_id)
    if not user or user["balance"] < amount_nk:
        return False, "Недостаточно наличных."
    chips = amount_nk // 100
    if chips < 1:
        return False, "Минимальная покупка 100 NK."
    await db.execute(
        "UPDATE users SET balance = balance - ?, casino_chips = casino_chips + ? WHERE vk_id = ?",
        amount_nk, chips, user_id
    )
    return True, f"Вы купили {chips} фишек."


async def sell_chips(user_id: int, chips: int) -> tuple:
    user = await db.fetchone("SELECT casino_chips FROM users WHERE vk_id = ?", user_id)
    if not user or user["casino_chips"] < chips:
        return False, "Недостаточно фишек."
    money = chips * 90
    await db.execute(
        "UPDATE users SET casino_chips = casino_chips - ?, balance = balance + ? WHERE vk_id = ?",
        chips, money, user_id
    )
    return True, f"Вы продали {chips} фишек за {money} NK."


async def play_dice(user_id: int, bet: int, guess: str) -> tuple:
    user = await db.fetchone("SELECT casino_chips FROM users WHERE vk_id = ?", user_id)
    if not user or user["casino_chips"] < bet:
        return False, "Недостаточно фишек.", 0
    total = random.randint(1, 6) + random.randint(1, 6)
    win = 0
    if guess.isdigit() and int(guess) == total:
        win = bet * 4
    elif guess in ("чёт", "чет") and total % 2 == 0:
        win = int(bet * 1.5)
    elif guess in ("нечет", "нечёт") and total % 2 != 0:
        win = int(bet * 1.5)
    await db.execute("UPDATE users SET casino_chips = casino_chips - ? WHERE vk_id = ?", bet, user_id)
    if win > 0:
        await db.execute("UPDATE users SET casino_chips = casino_chips + ? WHERE vk_id = ?", win, user_id)
        await db.execute(
            "INSERT INTO casino_bets (user_id, game_type, bet_amount, result_amount) VALUES (?, 'dice', ?, ?)",
            user_id, bet, win
        )
        return True, f"Выпало {total}. Выигрыш {win} фишек!", win
    await db.execute(
        "INSERT INTO casino_bets (user_id, game_type, bet_amount, result_amount) VALUES (?, 'dice', ?, 0)",
        user_id, bet
    )
    return True, f"Выпало {total}. Проигрыш.", 0


async def play_slots(user_id: int, bet: int) -> tuple:
    user = await db.fetchone("SELECT casino_chips FROM users WHERE vk_id = ?", user_id)
    if not user or user["casino_chips"] < bet:
        return False, "Недостаточно фишек.", 0
    symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "J"]
    r1, r2, r3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)
    win = 0
    if r1 == r2 == r3:
        win = bet * 100 if r1 == "💎" else bet * 10
    elif "J" in [r1, r2, r3] and (r1 == r2 or r2 == r3 or r1 == r3):
        win = bet * 5
    await db.execute("UPDATE users SET casino_chips = casino_chips - ? WHERE vk_id = ?", bet, user_id)
    if win > 0:
        await db.execute("UPDATE users SET casino_chips = casino_chips + ? WHERE vk_id = ?", win, user_id)
        await db.execute(
            "INSERT INTO casino_bets (user_id, game_type, bet_amount, result_amount) VALUES (?, 'slots', ?, ?)",
            user_id, bet, win
        )
        return True, f"Результат: {r1} {r2} {r3}. Выигрыш {win} фишек!", win
    await db.execute(
        "INSERT INTO casino_bets (user_id, game_type, bet_amount, result_amount) VALUES (?, 'slots', ?, 0)",
        user_id, bet
    )
    return True, f"Результат: {r1} {r2} {r3}. Проигрыш.", 0


async def play_russian_roulette(user_id: int, bet: int) -> tuple:
    user = await db.fetchone("SELECT casino_chips FROM users WHERE vk_id = ?", user_id)
    if not user or user["casino_chips"] < bet:
        return False, "Недостаточно фишек.", 0

    state_row = await db.fetchone(
        "SELECT data FROM user_states WHERE user_id = ? AND state = 'roulette'", user_id
    )
    current_pot = json.loads(state_row["data"]).get("current_pot", 0) if state_row else 0

    if bet > 0:
        await db.execute("UPDATE users SET casino_chips = casino_chips - ? WHERE vk_id = ?", bet, user_id)

    if random.randint(1, 6) == 1:
        await db.execute("DELETE FROM user_states WHERE user_id = ? AND state = 'roulette'", user_id)
        await db.execute(
            "INSERT INTO casino_bets (user_id, game_type, bet_amount, result_amount) VALUES (?, 'roulette', ?, 0)",
            user_id, bet
        )
        return True, "🔫 Выстрел! Вы проиграли серию.", 0

    new_pot = current_pot + bet
    await db.execute(
        "INSERT OR REPLACE INTO user_states (user_id, state, data) VALUES (?, 'roulette', ?)",
        user_id, json.dumps({"current_pot": new_pot})
    )
    return True, f"😅 Вы выжили. Текущий банк: {new_pot} фишек.", new_pot


async def collect_russian_roulette_winnings(user_id: int) -> tuple:
    state_row = await db.fetchone(
        "SELECT data FROM user_states WHERE user_id = ? AND state = 'roulette'", user_id
    )
    if not state_row:
        return False, "Нет активной серии.", 0
    amount = json.loads(state_row["data"]).get("current_pot", 0)
    if amount <= 0:
        return False, "Нет выигрыша для снятия.", 0
    await db.execute("UPDATE users SET casino_chips = casino_chips + ? WHERE vk_id = ?", amount, user_id)
    await db.execute("DELETE FROM user_states WHERE user_id = ? AND state = 'roulette'", user_id)
    await db.execute(
        "INSERT INTO casino_bets (user_id, game_type, bet_amount, result_amount) VALUES (?, 'roulette', 0, ?)",
        user_id, amount
    )
    return True, f"Вы забрали {amount} фишек.", amount


async def get_casino_owner_income(business_id: str) -> int:
    now = datetime.now(timezone.utc)
    hour_start = now.replace(minute=0, second=0, microsecond=0)
    row = await db.fetchone(
        "SELECT COALESCE(SUM(bet_amount - result_amount), 0) as net_loss FROM casino_bets WHERE created_at >= ?",
        hour_start.strftime("%Y-%m-%d %H:%M:%S")
    )
    net_loss = max(0, row["net_loss"] if row else 0)
    return int(net_loss * 0.5)


async def distribute_casino_income() -> None:
    casino = await db.fetchone("SELECT * FROM businesses WHERE type = 'auction_casino' AND hidden = 0")
    if not casino:
        return
    income = await get_casino_owner_income(casino["business_id"])
    if income <= 0:
        return
    if casino["owner_id"]:
        await db.execute("UPDATE users SET balance = balance + ? WHERE vk_id = ?", income, casino["owner_id"])
    else:
        await db.execute(
            "UPDATE system_accounts SET balance = balance + ? WHERE account_name = 'commission'", income
        )