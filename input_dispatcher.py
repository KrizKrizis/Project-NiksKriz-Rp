# middlewares/input_dispatcher.py
import logging
from datetime import datetime, timezone
from vkbottle.bot import Message
from vkbottle import BaseMiddleware
from db.database import db
from config import FOUNDER_ID, TECH_ADMIN_ID

logger = logging.getLogger(__name__)


class InputDispatcher(BaseMiddleware[Message]):
    async def pre(self):
        msg = self.event
        if not msg.from_id:
            return True

        # Основатель и тех-админ — пропускаем всегда
        if msg.from_id in (FOUNDER_ID, TECH_ADMIN_ID):
            return True

        # Проверка блокировки
        try:
            user = await db.fetchone(
                "SELECT is_blocked, temporary_blocked_until FROM users WHERE vk_id = ?",
                msg.from_id
            )
        except Exception:
            return True

        if user and user["is_blocked"]:
            until = user["temporary_blocked_until"]
            if until:
                try:
                    dt = datetime.fromisoformat(until)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    if datetime.now(timezone.utc) < dt:
                        return False
                    # Истёк — снимаем и пропускаем
                    await db.execute(
                        "UPDATE users SET is_blocked = 0, temporary_blocked_until = NULL WHERE vk_id = ?",
                        msg.from_id
                    )
                except Exception:
                    return False
            else:
                return False

        # Режимы чатов: беседы работают только в разрешённых режимах
        if msg.peer_id != msg.from_id:
            try:
                chat_cfg = await db.fetchone(
                    "SELECT chat_mode FROM chat_config WHERE chat_id = ?", msg.peer_id
                )
            except Exception:
                chat_cfg = None

            mode = chat_cfg["chat_mode"] if chat_cfg else 0

            # В беседе с режимом 0 — молчим (кроме 4.1/4.2, они уже пропущены)
            if mode == 0:
                return False

        return True

    async def post(self):
        pass