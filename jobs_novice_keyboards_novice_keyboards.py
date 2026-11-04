# jobs/novice/keyboards/jobs.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_novice_jobs_keyboard(available_job_ids: list) -> str:
    keyboard = Keyboard(inline=True)
    job_names = {"novice_1": "🏭 Завод", "novice_2": "🌾 Ферма", "novice_3": "⛏ Шахта", "novice_4": "🧱 Каменщик"}
    for job_id in available_job_ids:
        keyboard.add(Callback(job_names.get(job_id, job_id), payload={"cmd": "novice_job_info", "job_id": job_id}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "jobs_category_back", "category": "novice"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_job_info_keyboard(job_id: str) -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("▶️ Начать", payload={"cmd": "start_work_novice", "job_id": job_id}), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "jobs_category_back", "category": "novice"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_active_work_keyboard() -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🔄 Обновить", payload={"cmd": "refresh_work_novice"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Callback("❌ Отменить", payload={"cmd": "cancel_work_novice"}), color=KeyboardButtonColor.NEGATIVE)
    return keyboard.get_json()