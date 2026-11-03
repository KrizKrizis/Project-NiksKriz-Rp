# admin/spec_administration/handlers/curator.py
import logging
from vkbottle.bot import Blueprint, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from utils.permissions import has_permission, get_admin_info
from admin.player_management import get_player_page, get_total_pages
from admin.team_management import get_team_list, format_team_list, get_team_statistics
from admin.administration.keyboards.players_keyboards import get_admin_players_keyboard
from admin.administration.keyboards.team_keyboards import get_team_management_keyboard

logger = logging.getLogger(__name__)
bp = Blueprint("curator")


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
            logger.error(f"curator edit: {e}")


async def _get_permissions(user_id: int) -> dict:
    info = await get_admin_info(user_id)
    return info.get("permissions", {}) if info else {}


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_curator_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "curator_players":
        permissions = await _get_permissions(event.user_id)
        if not permissions.get("players.view", False):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        page = 1
        players = await get_player_page(page)
        total_pages = await get_total_pages()
        lines = [f"Страница {page}"]
        for p in players:
            status = "🔴" if p["is_blocked"] else "🟢"
            lines.append(f"{status} {p['game_id']} | {p['first_name']} {p['last_name']} | LVL {p['level']}")
        kb = get_admin_players_keyboard(page, total_pages, permissions)
        await _edit_event(event, "\n".join(lines), kb)

    elif cmd == "curator_team":
        if not await has_permission(event.user_id, "team.view"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        team = await get_team_list()
        text = await format_team_list(team)
        kb = get_team_management_keyboard(await _get_permissions(event.user_id))
        await _edit_event(event, text, kb)

    elif cmd == "curator_statistics":
        if not await has_permission(event.user_id, "team.manage"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        stats = await get_team_statistics()
        await _edit_event(event, stats)

    elif cmd == "curator_audit":
        if not await has_permission(event.user_id, "team.manage"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        logs = await db.fetchall("SELECT * FROM admin_log ORDER BY id DESC LIMIT 30")
        lines = ["📋 Аудит действий:"]
        for l in logs:
            lines.append(f"  • {l['admin_id']}: {l['action']} ({l['timestamp']})")
        await _edit_event(event, "\n".join(lines))