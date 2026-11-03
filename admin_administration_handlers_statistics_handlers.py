# admin/administration/handlers/statistics.py
import logging
from vkbottle.bot import Blueprint, MessageEvent
from vkbottle import GroupEventType
from utils.permissions import has_permission
from admin.team_management import get_team_statistics

logger = logging.getLogger(__name__)
bp = Blueprint("admin_statistics")


async def _edit_event(event: MessageEvent, text: str):
    try:
        await event.ctx_api.messages.edit(
            peer_id=event.peer_id,
            conversation_message_id=event.conversation_message_id,
            message=text, keyboard=""
        )
    except Exception:
        try:
            await event.ctx_api.messages.send(
                peer_id=event.peer_id, message=text, keyboard="", random_id=0
            )
        except Exception as e:
            logger.error(f"statistics edit: {e}")


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_statistics_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "admin_statistics":
        if not await has_permission(event.user_id, "team.manage"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        stats = await get_team_statistics()
        await _edit_event(event, stats)