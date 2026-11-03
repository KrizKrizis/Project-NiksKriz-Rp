# nkbot.py
import logging
import importlib
import pkgutil
from pathlib import Path

from vkbottle.bot import Bot, Blueprint

from config import VK_TOKEN, LOG_LEVEL, FOUNDER_ID, TECH_ADMIN_ID
from db.database import db
from db.migrations import init_db
from middlewares.input_dispatcher import InputDispatcher
from services.scheduler import init_scheduler

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(token=VK_TOKEN)
bot.labeler.message_view.register_middleware(InputDispatcher)

import builtins
builtins.bot = bot


async def sync_leadership_ids():
    try:
        if FOUNDER_ID:
            await db.execute("UPDATE users SET game_id = 0 WHERE vk_id = ?", FOUNDER_ID)
        if TECH_ADMIN_ID:
            await db.execute("UPDATE users SET game_id = 1 WHERE vk_id = ?", TECH_ADMIN_ID)
    except Exception as e:
        logger.warning(f"sync_leadership_ids: {e}")


def _load_from_dir(handlers_path: Path, module_base: str):
    if not handlers_path.is_dir():
        return
    for module_info in pkgutil.iter_modules([str(handlers_path)]):
        module_name = f"{module_base}.{module_info.name}"
        try:
            module = importlib.import_module(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, Blueprint):
                    attr.load(bot)
                    logger.info(f"Загружен Blueprint '{attr_name}' из {module_name}")
        except Exception as e:
            logger.error(f"Ошибка загрузки {module_name}: {e}", exc_info=True)


def discover_and_load_blueprints():
    base = Path(__file__).parent

    for handlers_dir in base.rglob("handlers"):
        if not handlers_dir.is_dir():
            continue
        try:
            rel_parent = handlers_dir.parent.relative_to(base)
        except ValueError:
            continue
        module_base = ".".join(rel_parent.parts) + ".handlers"
        _load_from_dir(handlers_dir, module_base)

    for extra in ("jobs.menu", "admin.base"):
        try:
            module = importlib.import_module(extra)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, Blueprint):
                    attr.load(bot)
                    logger.info(f"Загружен Blueprint '{attr_name}' из {extra}")
        except Exception as e:
            logger.error(f"Ошибка загрузки {extra}: {e}", exc_info=True)


async def on_startup():
    try:
        logger.info("Запуск NiksKriz Corporation...")
        await db.initialize()
        await init_db()
        await sync_leadership_ids()
        init_scheduler()
        discover_and_load_blueprints()
        logger.info("Бот готов.")
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}", exc_info=True)
        raise


async def on_shutdown():
    logger.info("Завершение работы...")
    await db.close()
    logger.info("Бот остановлен.")


if __name__ == "__main__":
    bot.on_startup.append(on_startup())
    bot.on_shutdown.append(on_shutdown())
    bot.run()