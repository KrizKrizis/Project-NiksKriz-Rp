# admin/project_leadership/handlers/roles.py
import logging
from vkbottle.bot import Blueprint, Message
from admin.team_management import assign_role, remove_role

logger = logging.getLogger(__name__)
bp = Blueprint("founder_roles")

@bp.on.message(payload={"cmd": "roles_menu"})
async def roles_menu(message: Message):
    from admin.project_leadership.handlers.team_handlers import team_management
    await team_management(message)