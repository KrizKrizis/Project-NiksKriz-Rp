# craft/handlers/craft.py
import logging
from datetime import datetime, timezone
from vkbottle.bot import Blueprint, MessageEvent
from vkbottle import GroupEventType
from db.database import db
from services.craft_service import (
    get_all_recipes, get_recipe_by_id, get_recipe_ingredients,
    start_craft, finish_craft, cancel_craft, get_active_craft,
)
from craft.keyboards.craft_keyboards import (
    get_craft_recipes_keyboard, get_recipe_info_keyboard, get_active_craft_keyboard,
)

logger = logging.getLogger(__name__)
bp = Blueprint("craft")


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
            logger.error(f"craft edit: {e}")


async def _show_active_craft_event(event: MessageEvent):
    active = await get_active_craft(event.user_id)
    if not active:
        await _show_recipes_event(event)
        return
    now = datetime.now(timezone.utc)
    end_time = datetime.fromisoformat(active["end_time"])
    remaining = end_time - now
    if remaining.total_seconds() < 0:
        success, msg = await finish_craft(event.user_id)
        await event.show_snackbar(msg[:80])
        await _show_recipes_event(event)
        return
    recipe = await get_recipe_by_id(active["recipe_id"])
    total_seconds = int(remaining.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    text = f"Крафт: {recipe['name'] if recipe else '?'}\nОсталось: {minutes:02d}:{seconds:02d}"
    await _edit_event(event, text, get_active_craft_keyboard())


async def _show_recipes_event(event: MessageEvent):
    active = await get_active_craft(event.user_id)
    if active:
        await _show_active_craft_event(event)
        return
    recipes = await get_all_recipes()
    if not recipes:
        await _edit_event(event, "Нет доступных рецептов.")
        return
    await _edit_event(event, "Рецепты крафта:", get_craft_recipes_keyboard(recipes))


async def show_craft_menu_event(event: MessageEvent):
    await _show_recipes_event(event)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_craft_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd in ("open_craft", "craft_recipes"):
        await event.show_snackbar(" ")
        await _show_recipes_event(event)

    elif cmd == "craft_recipe_info":
        await event.show_snackbar(" ")
        recipe_id = payload.get("recipe_id")
        recipe = await get_recipe_by_id(recipe_id)
        if not recipe:
            await _show_recipes_event(event)
            return
        ingredients = await get_recipe_ingredients(recipe_id)
        ing_lines = []
        for ing in ingredients:
            item = await db.fetchone("SELECT name FROM items WHERE item_id = ?", ing["item_id"])
            name = item["name"] if item else ing["item_id"]
            if ing["is_tool"]:
                ing_lines.append(f"• {name} (инструмент, не расходуется)")
            else:
                ing_lines.append(f"• {name} x{ing['quantity']}")
        text = (
            f"{recipe['name']}\n"
            f"Длительность: {recipe['duration_minutes']} мин\n"
            f"Шанс успеха: {int(recipe['success_chance']*100)}%\n\n"
            f"Ингредиенты:\n" + "\n".join(ing_lines)
        )
        await _edit_event(event, text, get_recipe_info_keyboard(recipe_id))

    elif cmd == "start_craft":
        recipe_id = payload.get("recipe_id")
        success, msg = await start_craft(event.user_id, recipe_id)
        await event.show_snackbar(msg[:80])
        await _show_active_craft_event(event)

    elif cmd == "refresh_craft":
        await event.show_snackbar(" ")
        await _show_active_craft_event(event)

    elif cmd == "cancel_craft":
        await cancel_craft(event.user_id)
        await event.show_snackbar("Крафт отменён")
        await _show_recipes_event(event)