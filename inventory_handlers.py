# player/handlers/inventory.py
import logging
from vkbottle.bot import Blueprint, Message, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from player.keyboards.inventory_keyboards import get_inventory_keyboard

logger = logging.getLogger(__name__)
bp = Blueprint("player_inventory")


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
            logger.error(f"inventory edit: {e}")


async def _build_inventory_text(user_id: int) -> str:
    items = await db.fetchall(
        "SELECT i.name, inv.quantity FROM inventory inv "
        "JOIN items i ON inv.item_id = i.item_id WHERE inv.user_id = ? "
        "ORDER BY i.type, i.name",
        user_id
    )
    if not items:
        return "🎒 Ваш инвентарь пуст."
    lines = ["🎒 Инвентарь:"]
    for item in items:
        lines.append(f"• {item['name']} — {item['quantity']} шт.")
    return "\n".join(lines)


async def show_inventory_menu_event(event: MessageEvent):
    text = await _build_inventory_text(event.user_id)
    await _edit_event(event, text, get_inventory_keyboard())


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_inventory_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "open_inventory":
        await event.show_snackbar(" ")
        await show_inventory_menu_event(event)


@bp.on.message(payload={"cmd": "open_inventory"})
async def open_inventory_text(message: Message):
    text = await _build_inventory_text(message.from_id)
    await message.answer(text, keyboard=get_inventory_keyboard())