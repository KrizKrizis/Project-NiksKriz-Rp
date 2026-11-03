# admin/base.py
import logging
from vkbottle.bot import Blueprint, Message
from db.database import db
from utils.permissions import get_admin_info, reload_admin_cache
from utils.vk_utils import get_user_info_by_link
from config import FOUNDER_ID, TECH_ADMIN_ID, GROUP_ID
from admin.project_leadership.handlers.founder_handlers import show_founder_menu
from admin.spec_administration.handlers.spec_admin_handlers import show_spec_admin_menu
from admin.administration.handlers.administration_handlers import show_administration_menu
from admin.helpers.handlers.helpers_handlers import show_helpers_menu

logger = logging.getLogger(__name__)
bp = Blueprint("admin_base")

async def _is_user_in_db(user_id: int) -> bool:
    row = await db.fetchone("SELECT vk_id FROM users WHERE vk_id = ?", user_id)
    return row is not None

async def show_admin_panel(message: Message, edit: bool = True):
    user_id = message.from_id
    if not await _is_user_in_db(user_id):
        await message.answer("Вы не зарегистрированы.")
        return
    admin_info = await get_admin_info(user_id)
    if not admin_info:
        await message.answer("У вас нет админ-роли.")
        return
    category = admin_info["category"]
    if category == 4: await show_founder_menu(message, edit=edit)
    elif category == 3: await show_spec_admin_menu(message, edit=edit)
    elif category == 2: await show_administration_menu(message, edit=edit)
    elif category == 1: await show_helpers_menu(message, edit=edit)
    else: await message.answer("Недостаточно прав.")

@bp.on.message(payload={"cmd": "admin_main_menu"})
async def admin_main_menu(message: Message):
    await show_admin_panel(message, edit=True)

@bp.on.message(payload={"cmd": "admin_logout"})
async def admin_logout(message: Message):
    await message.answer("Вы вышли из админ-панели.")

@bp.on.message(payload={"cmd": "admin_reload_cache"})
async def admin_reload_cache(message: Message):
    admin_info = await get_admin_info(message.from_id)
    if admin_info and admin_info["category"] == 4:
        await reload_admin_cache()
        await message.answer("Кеш прав сброшен.")
    else:
        await message.answer("Недостаточно прав.")

@bp.on.message(text=["/loghelper", "/logadmin", "/logspecadmin", "/logosnovpan"])
async def admin_login(message: Message):
    user_id = message.from_id
    if not await _is_user_in_db(user_id):
        await message.answer("Вы не зарегистрированы. Напишите /start.")
        return
    command = message.text
    admin_info = await get_admin_info(user_id)
    if command == "/logosnovpan":
        if admin_info and admin_info["category"] == 4:
            from admin.project_leadership.handlers.founder_handlers import founder_login
            await founder_login(message)
        else:
            await message.answer("Недостаточно прав.")
        return
    if not admin_info:
        await message.answer("У вас нет админ-роли.")
        return
    category = admin_info["category"]
    if command == "/loghelper" and category == 1: await show_helpers_menu(message, edit=False)
    elif command == "/logadmin" and category == 2: await show_administration_menu(message, edit=False)
    elif command == "/logspecadmin" and category == 3: await show_spec_admin_menu(message, edit=False)
    else: await message.answer("Команда не соответствует вашей категории.")

@bp.on.message(text=["/dialogclear", "/dialogclear "])
async def dialog_clear(message: Message):
    admin_info = await get_admin_info(message.from_id)
    if not admin_info or admin_info["category"] != 4:
        await message.answer("Недостаточно прав.")
        return

    try:
        # Получаем историю сообщений (до 200)
        history = await message.ctx_api.messages.get_history(peer_id=message.peer_id, count=200)
        
        # Собираем ID всех сообщений (и бота, и пользователя)
        msg_ids = [msg.id for msg in history.items]
        
        if msg_ids:
            await message.ctx_api.messages.delete(message_ids=msg_ids, delete_for_all=True, group_id=GROUP_ID)
        
        # После удаления отправляем уведомление (если нужно)
        await message.answer("Диалог очищен. (Сообщения пользователя ВК API может не удалять, но бот попытался).")
    except Exception as e:
        logger.error(f"Ошибка при очистке диалога: {e}")
        await message.answer("Не удалось полностью очистить диалог. ВК API позволяет удалять только сообщения бота.")

@bp.on.message()
async def handle_resolve_command(message: Message):
    if not message.text or not message.text.startswith("/resolve"): return
    admin_info = await get_admin_info(message.from_id)
    if not admin_info or admin_info["category"] != 4:
        await message.answer("Недостаточно прав.")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /resolve <ссылка на страницу ВК>")
        return
    link = parts[1].strip()
    if not link:
        await message.answer("Использование: /resolve <ссылка на страницу ВК>")
        return
    info = await get_user_info_by_link(link)
    if not info:
        await message.answer("Не удалось получить информацию. Проверь ссылку.")
        return
    text = (
        f"🔎 Информация о пользователе:\n"
        f"👤 Имя: {info['full_name'] or 'не указано'}\n"
        f"🆔 VK ID: {info['vk_id']}\n"
        f"🔗 Короткое имя: {info['screen_name'] or 'нет'}\n"
        f"🌐 Ссылка: {info['link']}"
    )
    await message.answer(text)