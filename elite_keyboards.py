# jobs/elite/keyboards/jobs.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_elite_jobs_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🚀 Работа на Марсе", payload={"cmd": "elite_job_info", "job_id": "elite_1"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "jobs_category_back", "category": "elite"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_job_info_keyboard(job_id: str) -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("▶️ Начать", payload={"cmd": "start_work", "job_id": job_id}), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "jobs_category_back", "category": "elite"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_active_work_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔄 Обновить", payload={"cmd": "refresh_work"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("❌ Отменить", payload={"cmd": "cancel_work"}), color=KeyboardButtonColor.NEGATIVE)
    return keyboard.get_json()