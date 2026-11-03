# admin/administration/handlers/complaints.py
import logging
from vkbottle.bot import Blueprint, MessageEvent
from vkbottle import GroupEventType
from utils.permissions import has_permission
from admin.complaint_management import (
    get_complaints, format_complaints, accept_complaint, reject_complaint,
)
from admin.administration.keyboards.complaints_keyboards import (
    get_complaints_list_keyboard, get_complaint_detail_keyboard,
)

logger = logging.getLogger(__name__)
bp = Blueprint("admin_complaints")


async def _edit_event(event: MessageEvent, text: str, keyboard: str = ""):
    try:
        await event.ctx_api.messages.edit(
            peer_id=event.peer_id,
            conversation_message_id=event.conversation_message_id,
            message=text, keyboard=keyboard
        )
    except Exception:
        try:
            await event.ctx_api.messages.send(
                peer_id=event.peer_id, message=text, keyboard=keyboard, random_id=0
            )
        except Exception as e:
            logger.error(f"complaints edit: {e}")


async def _show_complaints_list(event: MessageEvent):
    complaints = await get_complaints()
    text = await format_complaints(complaints)
    kb = get_complaints_list_keyboard(complaints)
    await _edit_event(event, text, kb)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_complaints_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "admin_complaints":
        if not await has_permission(event.user_id, "complaints.view"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        await _show_complaints_list(event)

    elif cmd == "admin_complaint_detail":
        if not await has_permission(event.user_id, "complaints.resolve"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        complaint_id = int(payload["id"])
        kb = get_complaint_detail_keyboard(complaint_id)
        await _edit_event(event, f"Жалоба #{complaint_id}", kb)

    elif cmd == "admin_complaint_accept":
        if not await has_permission(event.user_id, "complaints.resolve"):
            await event.show_snackbar(" ")
            return
        complaint_id = int(payload["id"])
        success, msg = await accept_complaint(event.user_id, complaint_id)
        await event.show_snackbar(msg[:80])
        await _show_complaints_list(event)

    elif cmd == "admin_complaint_reject":
        if not await has_permission(event.user_id, "complaints.resolve"):
            await event.show_snackbar(" ")
            return
        complaint_id = int(payload["id"])
        success, msg = await reject_complaint(event.user_id, complaint_id)
        await event.show_snackbar(msg[:80])
        await _show_complaints_list(event)