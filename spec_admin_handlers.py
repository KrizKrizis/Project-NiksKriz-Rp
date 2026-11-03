# admin/spec_administration/handlers/spec_admin.py
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType
from utils.permissions import get_admin_info
from admin.spec_administration.keyboards.curator_keyboards import get_curator_menu_keyboard
from admin.spec_administration.keyboards.tester_keyboards import get_tester_menu_keyboard
from admin.spec_administration.keyboards.deputy_keyboards import get_deputy_menu_keyboard

logger = logging.getLogger(__name__)
bp = Blueprint("spec_admin")


async def _edit_event(event: MessageEvent, text: str, keyboard: str):
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
            logger.error(f"spec edit: {e}")


def _menu_for_position(position: str):
    if position == "3.1":
        return "👤 Меню куратора", get_curator_menu_keyboard()
    if position == "3.2":
        return "🛠 Тест-панель", get_tester_menu_keyboard()
    if position == "3.3":
        return "👑 Меню заместителя основателя", get_deputy_menu_keyboard()
    return None, None


async def show_spec_admin_menu_event(event: MessageEvent):
    info = await get_admin_info(event.user_id)
    if not info or info["category"] != 3:
        await event.show_snackbar(" ")
        return
    text, kb = _menu_for_position(info["position"])
    if not kb:
        return
    await _edit_event(event, text, kb)


async def show_spec_admin_menu(message: Message, edit: bool = False):
    info = await get_admin_info(message.from_id)
    if not info or info["category"] != 3:
        return
    text, kb = _menu_for_position(info["position"])
    if not kb:
        return
    if edit:
        try:
            await message.edit(text, keyboard=kb)
        except Exception:
            await message.answer(text, keyboard=kb)
    else:
        await message.answer(text, keyboard=kb)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_spec_admin_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "spec_main_menu":
        await event.show_snackbar(" ")
        await show_spec_admin_menu_event(event)