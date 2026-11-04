# jobs/millionaire/keyboards/jobs.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_millionaire_jobs_keyboard(jobs: list) -> str:
    keyboard = Keyboard(inline=True)
    for job in jobs:
        keyboard.add(Callback(job["name"], payload={"cmd": "millionaire_job_info", "job_id": job["job_id"]}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "jobs_category_back", "category": "millionaire"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_job_info_keyboard(job_id: str) -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("▶️ Начать", payload={"cmd": "start_work_millionaire", "job_id": job_id}), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "jobs_category_back", "category": "millionaire"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_active_work_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔄 Обновить", payload={"cmd": "refresh_work_millionaire"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("❌ Отменить", payload={"cmd": "cancel_work_millionaire"}), color=KeyboardButtonColor.NEGATIVE)
    return keyboard.get_json()