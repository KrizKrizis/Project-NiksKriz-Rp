# admin/administration/handlers/administration.py
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType
from utils.permissions import get_admin_info
from admin.administration.keyboards.administration_menu_keyboards import get_administration_main_keyboard

logger = logging.getLogger(__name__)
bp = Blueprint("administration")


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
            logger.error(f"admin menu edit: {e}")


async def show_administration_menu_event(event: MessageEvent):
    admin_info = await get_admin_info(event.user_id)
    if not admin_info or admin_info["category"] != 2:
        await event.show_snackbar(" ")
        return
    kb = get_administration_main_keyboard(event.user_id, admin_info.get("permissions", {}))
    await _edit_event(event, "🛡 Меню администрации", kb)


async def show_administration_menu(message: Message, edit: bool = False):
    admin_info = await get_admin_info(message.from_id)
    if not admin_info or admin_info["category"] != 2:
        return
    keyboard = get_administration_main_keyboard(message.from_id, admin_info.get("permissions", {}))
    if edit:
        try:
            await message.edit("🛡 Меню администрации", keyboard=keyboard)
        except Exception:
            await message.answer("🛡 Меню администрации", keyboard=keyboard)
    else:
        await message.answer("🛡 Меню администрации", keyboard=keyboard)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_administration_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "admin_main_menu":
        await event.show_snackbar(" ")
        await show_administration_menu_event(event)