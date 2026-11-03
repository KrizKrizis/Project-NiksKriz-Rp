# jobs/permanent/handlers/jobs.py
import logging
from datetime import datetime, timezone
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType, Keyboard, Callback, KeyboardButtonColor
from db.database import db
from services.work_service import start_work, finish_work, get_job_info

logger = logging.getLogger(__name__)
bp = Blueprint("permanent_jobs")


async def get_permanent_jobs_keyboard(user_id: int):
    jobs = await db.fetchall("SELECT job_id, name FROM jobs WHERE category = 'permanent'")
    keyboard = Keyboard(inline=True)
    for job in jobs:
        keyboard.add(Callback(job["name"], payload={"cmd": "permanent_job_info", "job_id": job["job_id"]}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "open_jobs"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


async def show_permanent_jobs_event(event: MessageEvent):
    user = await db.fetchone("SELECT current_work FROM users WHERE vk_id = ?", event.user_id)
    if user and user["current_work"]:
        await show_active_work_event(event)
        return
    kb = await get_permanent_jobs_keyboard(event.user_id)
    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        message="Постоянные работы:",
        keyboard=kb
    )


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_permanent_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "permanent_job_info":
        job_id = payload.get("job_id")
        job = await get_job_info(job_id)
        if not job:
            return
        duration = job["duration_seconds"] // 60 if job["duration_seconds"] >= 60 else job["duration_seconds"]
        unit = "мин" if job["duration_seconds"] >= 60 else "сек"
        text = f"{job['name']}\nДлительность: {duration} {unit}\nЗарплата: {job['base_reward_min']}-{job['base_reward_max']} NK"
        kb = Keyboard(inline=True)
        kb.add(Callback("▶️ Начать", payload={"cmd": "start_work_permanent", "job_id": job_id}), color=KeyboardButtonColor.POSITIVE)
        kb.row()
        kb.add(Callback("🔙 Назад", payload={"cmd": "jobs_category", "category": "permanent"}), color=KeyboardButtonColor.SECONDARY)
        await event.ctx_api.messages.edit(peer_id=event.peer_id, conversation_message_id=event.conversation_message_id, message=text, keyboard=kb.get_json())

    elif cmd == "start_work_permanent":
        job_id = payload.get("job_id")
        success, msg = await start_work(event.user_id, job_id)
        await event.show_snackbar(msg)
        if success:
            await show_active_work_event(event)
        else:
            await show_permanent_jobs_event(event)

    elif cmd == "refresh_work_permanent":
        await event.show_snackbar(" ")
        await show_active_work_event(event)

    elif cmd == "cancel_work_permanent":
        await event.show_snackbar("Отменено")
        await db.execute("UPDATE users SET current_work = NULL, work_start_time = NULL, work_end_time = NULL, work_reward = NULL, work_drop_data = NULL WHERE vk_id = ?", event.user_id)
        await show_permanent_jobs_event(event)

    elif cmd == "jobs_category_back":
        await event.show_snackbar(" ")
        from jobs.menu import show_categories_event
        await show_categories_event(event)


async def show_active_work_event(event: MessageEvent):
    user = await db.fetchone("SELECT current_work, work_end_time FROM users WHERE vk_id = ?", event.user_id)
    if not user or not user["current_work"]:
        await show_permanent_jobs_event(event)
        return
    job = await get_job_info(user["current_work"])
    end_time = datetime.fromisoformat(user["work_end_time"])
    now = datetime.now(timezone.utc)
    remaining = end_time - now
    if remaining.total_seconds() < 0:
        success, msg = await finish_work(event.user_id)
        await event.ctx_api.messages.edit(peer_id=event.peer_id, conversation_message_id=event.conversation_message_id, message=msg, keyboard=await get_permanent_jobs_keyboard(event.user_id))
        return
    total_seconds = int(remaining.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    time_left = f"{minutes:02d}:{seconds:02d}"
    text = f"Работа: {job['name']}\nОсталось: {time_left}"
    kb = Keyboard(inline=True)
    kb.add(Callback("🔄 Обновить", payload={"cmd": "refresh_work_permanent"}), color=KeyboardButtonColor.PRIMARY)
    kb.add(Callback("❌ Отменить", payload={"cmd": "cancel_work_permanent"}), color=KeyboardButtonColor.NEGATIVE)
    await event.ctx_api.messages.edit(peer_id=event.peer_id, conversation_message_id=event.conversation_message_id, message=text, keyboard=kb.get_json())