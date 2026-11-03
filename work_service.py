# services/work_service.py
import random
import json
from datetime import datetime, timezone, timedelta
from db.database import db


async def get_job_info(job_id: str) -> dict:
    return await db.fetchone("SELECT * FROM jobs WHERE job_id = ?", job_id)


async def get_job_bonuses(job_id: str) -> list:
    return await db.fetchall(
        "SELECT item_id, chance, check_interval_minutes FROM work_bonuses WHERE job_id = ?",
        job_id
    )


async def start_work(user_id: int, job_id: str) -> tuple:
    job = await get_job_info(job_id)
    if not job:
        return False, "Работа не найдена."

    user = await db.fetchone("SELECT current_work, level FROM users WHERE vk_id = ?", user_id)
    if not user:
        return False, "Игрок не найден."
    if user["current_work"]:
        return False, "Вы уже работаете. Сначала завершите текущую работу."
    if user["level"] < job["level_required"]:
        return False, f"Требуется уровень {job['level_required']}."

    if job["business_id"]:
        biz = await db.fetchone(
            "SELECT owner_id FROM businesses WHERE business_id = ? AND owner_id = ?",
            job["business_id"], user_id
        )
        if biz:
            return False, "Вы владеете этим бизнесом. Работа здесь запрещена."

    reward = random.randint(job["base_reward_min"], job["base_reward_max"])

    drop_data = {}
    bonuses = await get_job_bonuses(job_id)
    for bonus in bonuses:
        if bonus["check_interval_minutes"] == 0 and random.random() < bonus["chance"]:
            qty = random.randint(2, 10) if bonus["item_id"] == "1.1.15" else 1
            drop_data[bonus["item_id"]] = drop_data.get(bonus["item_id"], 0) + qty

    now = datetime.now(timezone.utc)
    end_time = now + timedelta(seconds=job["duration_seconds"])

    await db.execute(
        "UPDATE users SET current_work = ?, work_start_time = ?, work_end_time = ?, "
        "work_reward = ?, work_drop_data = ? WHERE vk_id = ?",
        job_id, now.isoformat(), end_time.isoformat(), reward, json.dumps(drop_data), user_id
    )
    return True, "Работа начата."


async def finish_work(user_id: int) -> tuple:
    user = await db.fetchone(
        "SELECT current_work, work_end_time, work_reward, work_drop_data FROM users WHERE vk_id = ?",
        user_id
    )
    if not user or not user["current_work"]:
        return False, "Нет активной работы."

    if user["work_end_time"]:
        end_time = datetime.fromisoformat(user["work_end_time"])
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) < end_time:
            remaining = end_time - datetime.now(timezone.utc)
            minutes, seconds = divmod(int(remaining.total_seconds()), 60)
            return False, f"Работа ещё не завершена. Осталось: {minutes:02d}:{seconds:02d}."

    reward = user["work_reward"] or 0
    drop_data_str = user["work_drop_data"]

    await db.execute("UPDATE users SET balance = balance + ? WHERE vk_id = ?", reward, user_id)
    await db.execute(
        "INSERT INTO transactions (sender_id, receiver_id, amount, currency, transaction_type) "
        "VALUES (NULL, ?, ?, 'NK', 'salary')",
        user_id, reward
    )

    if drop_data_str:
        drop_data = json.loads(drop_data_str)
        for item_id, qty in drop_data.items():
            existing = await db.fetchone(
                "SELECT id, quantity FROM inventory WHERE user_id = ? AND item_id = ?",
                user_id, item_id
            )
            if existing:
                await db.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", qty, existing["id"])
            else:
                await db.execute(
                    "INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)",
                    user_id, item_id, qty
                )

    await db.execute(
        "UPDATE users SET current_work = NULL, work_start_time = NULL, work_end_time = NULL, "
        "work_reward = NULL, work_drop_data = NULL WHERE vk_id = ?",
        user_id
    )

    parts = [f"Вы заработали {reward} NK"]
    if drop_data_str:
        for item_id, qty in json.loads(drop_data_str).items():
            item = await db.fetchone("SELECT name FROM items WHERE item_id = ?", item_id)
            if item:
                parts.append(f"{item['name']} x{qty}")

    return True, "Работа завершена.\n" + "\n".join(parts)