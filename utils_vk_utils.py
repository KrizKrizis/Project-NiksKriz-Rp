# utils/vk_utils.py
import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


async def get_user_info_by_link(link: str) -> Optional[Dict[str, Any]]:
    import builtins
    bot = getattr(builtins, 'bot', None)
    if not bot:
        logger.error("bot не найден в builtins")
        return None

    link = link.strip()
    if not link:
        return None

    screen_name = None
    if "vk.com/" in link:
        match = re.search(r'vk\.com/([^?\s/]+)', link)
        if match:
            screen_name = match.group(1)
    elif link.startswith("id") and link[2:].isdigit():
        screen_name = link
    else:
        if link.isdigit():
            screen_name = f"id{link}"
        else:
            screen_name = link

    if not screen_name:
        return None

    try:
        resolved = await bot.api.utils.resolve_screen_name(screen_name=screen_name)
        if resolved and hasattr(resolved, 'object_id'):
            vk_id = resolved.object_id
        else:
            users = await bot.api.users.get(user_ids=screen_name)
            if users:
                vk_id = users[0].id
            else:
                return None
    except Exception as e:
        logger.warning(f"resolve_screen_name не сработал: {e}")
        try:
            users = await bot.api.users.get(user_ids=screen_name)
            if users:
                vk_id = users[0].id
            else:
                return None
        except Exception as e2:
            logger.error(f"users.get не сработал: {e2}")
            return None

    try:
        users = await bot.api.users.get(user_ids=vk_id, fields=["screen_name"])
        if not users:
            return None
        user = users[0]
        return {
            "vk_id": vk_id,
            "first_name": getattr(user, 'first_name', ''),
            "last_name": getattr(user, 'last_name', ''),
            "screen_name": getattr(user, 'screen_name', ''),
            "full_name": f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip(),
            "link": f"https://vk.com/id{vk_id}",
        }
    except Exception as e:
        logger.error(f"Ошибка получения данных пользователя: {e}")
        return {
            "vk_id": vk_id, "first_name": "", "last_name": "",
            "screen_name": screen_name, "full_name": "",
            "link": f"https://vk.com/id{vk_id}",
        }