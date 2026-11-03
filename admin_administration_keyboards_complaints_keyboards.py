# admin/administration/keyboards/complaints_keyboards.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor


def get_complaints_list_keyboard(complaints: list) -> str:
    keyboard = Keyboard(inline=True)
    for c in complaints[:10]:
        details = c["details"] or ""
        label = f"#{c['id']}: {details[:30]}"
        keyboard.add(Callback(label, payload={"cmd": "admin_complaint_detail", "id": c["id"]}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "admin_main_menu"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


def get_complaint_detail_keyboard(complaint_id: int) -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("✅ Принять", payload={"cmd": "admin_complaint_accept", "id": complaint_id}), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Callback("❌ Отклонить", payload={"cmd": "admin_complaint_reject", "id": complaint_id}), color=KeyboardButtonColor.NEGATIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "admin_complaints"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()