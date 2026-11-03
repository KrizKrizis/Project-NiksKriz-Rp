# housing/handlers/housing.py
import logging
from vkbottle.bot import Blueprint, MessageEvent
from vkbottle import GroupEventType, Keyboard, KeyboardButtonColor, Text
from db.database import db
from services.housing_service import (
    get_available_housing, get_user_housing, buy_housing, sell_housing,
    buy_crypto_farm, sell_crypto_farm, install_videocard, remove_videocard,
    get_garden_plots, buy_garden_plot, plant_seed, water_plant, harvest_plant, chop_tree,
)
from housing.keyboards.housing_keyboards import (
    get_housing_main_keyboard, get_housing_list_keyboard, get_housing_my_keyboard,
    get_crypto_farm_keyboard, get_garden_main_keyboard, get_garden_plots_keyboard,
    get_garden_plot_actions_keyboard,
)

logger = logging.getLogger(__name__)
bp = Blueprint("housing")


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
            logger.error(f"housing edit: {e}")


async def show_housing_menu_event(event: MessageEvent):
    user_housing = await get_user_housing(event.user_id)
    await _edit_event(event, "🏠 Жильё", get_housing_main_keyboard(user_housing))


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_housing_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd in ("open_housing", "housing_main"):
        await event.show_snackbar(" ")
        await show_housing_menu_event(event)

    elif cmd == "housing_buy_list":
        await event.show_snackbar(" ")
        housing_list = await get_available_housing()
        if not housing_list:
            await _edit_event(event, "Нет доступного жилья.")
            return
        await _edit_event(event, "Доступное жильё:", get_housing_list_keyboard(housing_list))

    elif cmd == "housing_buy":
        housing_id = payload.get("housing_id")
        success, msg = await buy_housing(event.user_id, housing_id)
        await event.show_snackbar(msg[:80])
        await show_housing_menu_event(event)

    elif cmd == "housing_my":
        await event.show_snackbar(" ")
        user_housing = await get_user_housing(event.user_id)
        if not user_housing:
            await _edit_event(event, "У вас нет жилья.", get_housing_main_keyboard(None))
            return
        text = (
            f"🏠 Ваше жильё: {user_housing['name']}\n"
            f"Тип: {user_housing['type']}\n"
            f"Парковочные места: {user_housing['parking_spots']}\n"
            f"Криптоферма: {'установлена' if user_housing['has_crypto_farm'] else 'не установлена'}"
        )
        await _edit_event(event, text, get_housing_my_keyboard())

    elif cmd == "housing_sell":
        success, msg = await sell_housing(event.user_id)
        await event.show_snackbar(msg[:80])
        await show_housing_menu_event(event)

    elif cmd == "housing_crypto_farm":
        await event.show_snackbar(" ")
        user_housing = await get_user_housing(event.user_id)
        if not user_housing:
            await _edit_event(event, "Сначала купите жильё.", get_housing_main_keyboard(None))
            return
        await _edit_event(event, "Криптоферма", get_crypto_farm_keyboard(user_housing["has_crypto_farm"]))

    elif cmd == "housing_buy_farm":
        success, msg = await buy_crypto_farm(event.user_id)
        await event.show_snackbar(msg[:80])
        user_housing = await get_user_housing(event.user_id)
        await _edit_event(event, "Криптоферма", get_crypto_farm_keyboard(user_housing["has_crypto_farm"] if user_housing else False))

    elif cmd == "housing_sell_farm":
        success, msg = await sell_crypto_farm(event.user_id)
        await event.show_snackbar(msg[:80])
        await show_housing_menu_event(event)

    elif cmd == "housing_install_videocard":
        await event.show_snackbar(" ")
        videocards = await db.fetchall(
            "SELECT inv.item_id, i.name FROM inventory inv JOIN items i ON inv.item_id = i.item_id WHERE inv.user_id = ? AND i.type = 'videocard'",
            event.user_id
        )
        if not videocards:
            await _edit_event(event, "У вас нет видеокарт.", get_crypto_farm_keyboard(True))
            return
        kb = Keyboard(inline=True)
        for vc in videocards:
            kb.add(Text(vc["name"], payload={"cmd": "housing_install_vc", "item_id": vc["item_id"]}), color=KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text("🔙 Назад", payload={"cmd": "housing_crypto_farm"}), color=KeyboardButtonColor.SECONDARY)
        await _edit_event(event, "Выберите видеокарту:", kb.get_json())

    elif cmd == "housing_install_vc":
        item_id = payload.get("item_id")
        success, msg = await install_videocard(event.user_id, item_id)
        await event.show_snackbar(msg[:80])
        await _edit_event(event, "Криптоферма", get_crypto_farm_keyboard(True))

    elif cmd == "housing_remove_videocard":
        farm = await db.fetchone("SELECT videocard_id FROM crypto_farm WHERE user_id = ? LIMIT 1", event.user_id)
        if not farm:
            await event.show_snackbar("В ферме нет видеокарт")
            return
        success, msg = await remove_videocard(event.user_id, farm["videocard_id"])
        await event.show_snackbar(msg[:80])
        await _edit_event(event, "Криптоферма", get_crypto_farm_keyboard(True))

    elif cmd == "housing_garden":
        await event.show_snackbar(" ")
        user_housing = await get_user_housing(event.user_id)
        if not user_housing or user_housing["type"] != "house":
            await _edit_event(event, "Садоводство доступно только в доме.", get_housing_main_keyboard(user_housing))
            return
        plots = await get_garden_plots(event.user_id)
        if not plots:
            await _edit_event(event, "Садоводство", get_garden_main_keyboard())
        else:
            await _edit_event(event, "Ваши участки:", get_garden_plots_keyboard(plots))

    elif cmd == "garden_buy_plot":
        plot_number = int(payload.get("plot"))
        success, msg = await buy_garden_plot(event.user_id, plot_number)
        await event.show_snackbar(msg[:80])
        plots = await get_garden_plots(event.user_id)
        if plots:
            await _edit_event(event, "Ваши участки:", get_garden_plots_keyboard(plots))
        else:
            await _edit_event(event, "Садоводство", get_garden_main_keyboard())

    elif cmd == "garden_plot":
        plot_number = int(payload.get("plot_number"))
        await event.show_snackbar(" ")
        await _edit_event(event, f"Участок {plot_number}", get_garden_plot_actions_keyboard(plot_number))

    elif cmd == "garden_plant":
        plot_number = int(payload.get("plot"))
        await event.show_snackbar(" ")
        seeds = await db.fetchall(
            "SELECT inv.item_id, i.name FROM inventory inv JOIN items i ON inv.item_id = i.item_id WHERE inv.user_id = ? AND i.type = 'seed'",
            event.user_id
        )
        if not seeds:
            await _edit_event(event, "У вас нет семян.", get_garden_plot_actions_keyboard(plot_number))
            return
        kb = Keyboard(one_time=False, inline=True)
        for s in seeds:
            kb.add(Text(s["name"], payload={"cmd": "garden_select_seed", "plot": plot_number, "seed_item_id": s["item_id"]}), color=KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text("🔙 Назад", payload={"cmd": "garden_plot", "plot_number": plot_number}), color=KeyboardButtonColor.SECONDARY)
        await _edit_event(event, "Выберите семя для посадки:", kb.get_json())

    elif cmd == "garden_select_seed":
        plot_number = int(payload.get("plot"))
        seed_item_id = payload.get("seed_item_id")
        await event.show_snackbar(" ")
        kb = Keyboard(one_time=False, inline=True)
        for slot in range(1, 26):
            kb.add(Text(str(slot), payload={"cmd": "garden_select_slot", "plot": plot_number, "seed_item_id": seed_item_id, "slot": slot}), color=KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text("🔙 Назад", payload={"cmd": "garden_plot", "plot_number": plot_number}), color=KeyboardButtonColor.SECONDARY)
        await _edit_event(event, "Выберите лунку (1-25):", kb.get_json())

    elif cmd == "garden_select_slot":
        plot_number = int(payload.get("plot"))
        slot_number = int(payload.get("slot"))
        seed_item_id = payload.get("seed_item_id")
        success, msg = await plant_seed(event.user_id, plot_number, slot_number, seed_item_id)
        await event.show_snackbar(msg[:80])
        await _edit_event(event, f"Участок {plot_number}", get_garden_plot_actions_keyboard(plot_number))

    elif cmd == "garden_water":
        plot_number = int(payload.get("plot"))
        await event.show_snackbar(" ")
        plants = await db.fetchall(
            "SELECT id, slot_number, plant_type FROM garden_plants WHERE user_id = ? AND plot_number = ? AND water_required_by <= datetime('now')",
            event.user_id, plot_number
        )
        if not plants:
            await _edit_event(event, "Нет растений, которые нужно полить.", get_garden_plot_actions_keyboard(plot_number))
            return
        kb = Keyboard(one_time=False, inline=True)
        for p in plants:
            kb.add(Text(f"Лунка {p['slot_number']}: {p['plant_type']}", payload={"cmd": "garden_water_plant", "plant_id": p["id"]}), color=KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text("🔙 Назад", payload={"cmd": "garden_plot", "plot_number": plot_number}), color=KeyboardButtonColor.SECONDARY)
        await _edit_event(event, "Какие растения полить?", kb.get_json())

    elif cmd == "garden_water_plant":
        plant_id = int(payload.get("plant_id"))
        success, msg = await water_plant(event.user_id, plant_id)
        await event.show_snackbar(msg[:80])

    elif cmd == "garden_harvest":
        plot_number = int(payload.get("plot"))
        await event.show_snackbar(" ")
        plants = await db.fetchall(
            "SELECT id, slot_number, plant_type FROM garden_plants WHERE user_id = ? AND plot_number = ? AND can_harvest = 1",
            event.user_id, plot_number
        )
        if not plants:
            await _edit_event(event, "Нет растений, готовых к сбору.", get_garden_plot_actions_keyboard(plot_number))
            return
        kb = Keyboard(one_time=False, inline=True)
        for p in plants:
            kb.add(Text(f"Лунка {p['slot_number']}: {p['plant_type']}", payload={"cmd": "garden_harvest_plant", "plant_id": p["id"]}), color=KeyboardButtonColor.POSITIVE)
        kb.row()
        kb.add(Text("🔙 Назад", payload={"cmd": "garden_plot", "plot_number": plot_number}), color=KeyboardButtonColor.SECONDARY)
        await _edit_event(event, "Что собрать?", kb.get_json())

    elif cmd == "garden_harvest_plant":
        plant_id = int(payload.get("plant_id"))
        success, msg = await harvest_plant(event.user_id, plant_id)
        await event.show_snackbar(msg[:80])

    elif cmd == "garden_chop_tree":
        plot_number = int(payload.get("plot"))
        await event.show_snackbar(" ")
        trees = await db.fetchall(
            "SELECT id, slot_number, plant_type FROM garden_plants WHERE user_id = ? AND plot_number = ? AND is_tree = 1",
            event.user_id, plot_number
        )
        if not trees:
            await _edit_event(event, "Нет деревьев для вырубки.", get_garden_plot_actions_keyboard(plot_number))
            return
        kb = Keyboard(one_time=False, inline=True)
        for t in trees:
            kb.add(Text(f"Лунка {t['slot_number']}: {t['plant_type']}", payload={"cmd": "garden_chop_tree_confirm", "plant_id": t["id"]}), color=KeyboardButtonColor.NEGATIVE)
        kb.row()
        kb.add(Text("🔙 Назад", payload={"cmd": "garden_plot", "plot_number": plot_number}), color=KeyboardButtonColor.SECONDARY)
        await _edit_event(event, "Какое дерево вырубить?", kb.get_json())

    elif cmd == "garden_chop_tree_confirm":
        plant_id = int(payload.get("plant_id"))
        success, msg = await chop_tree(event.user_id, plant_id)
        await event.show_snackbar(msg[:80])