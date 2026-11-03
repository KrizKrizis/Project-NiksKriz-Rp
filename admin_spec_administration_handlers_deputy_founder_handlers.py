# admin/spec_administration/handlers/deputy_founder.py
import logging
from vkbottle.bot import Blueprint, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from utils.permissions import has_permission, get_admin_info
from admin.player_management import get_player_page, get_total_pages
from admin.administration.keyboards.players_keyboards import get_admin_players_keyboard
from admin.administration.keyboards.team_keyboards import get_team_management_keyboard
from admin.team_management import get_team_list, format_team_list
from admin.project_management import list_project_settings, get_project_settings_keyboard

logger = logging.getLogger(__name__)
bp = Blueprint("deputy")


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
            logger.error(f"deputy edit: {e}")


async def _get_permissions(user_id: int) -> dict:
    info = await get_admin_info(user_id)
    return info.get("permissions", {}) if info else {}


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_deputy_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "deputy_players":
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

    elif cmd == "deputy_team":
        if not await has_permission(event.user_id, "team.view"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        team = await get_team_list()
        text = await format_team_list(team)
        kb = get_team_management_keyboard(await _get_permissions(event.user_id))
        await _edit_event(event, text, kb)

    elif cmd == "deputy_project":
        if not await has_permission(event.user_id, "project.manage"):
            await event.show_snackbar(" ")
            return
        await event.show_snackbar(" ")
        text = await list_project_settings()
        kb = await get_project_settings_keyboard()
        await _edit_event(event, text, kb)

    elif cmd == "deputy_project_stats":
        await event.show_snackbar(" ")
        users_count = await db.fetchone("SELECT COUNT(*) as cnt FROM users")
        businesses_count = await db.fetchone("SELECT COUNT(*) as cnt FROM businesses WHERE owner_id IS NOT NULL")
        text = f"📊 Статистика проекта:\nИгроков: {users_count['cnt']}\nБизнесов владеют: {businesses_count['cnt']}"
        await _edit_event(event, text)