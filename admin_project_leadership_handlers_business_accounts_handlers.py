# admin/project_leadership/handlers/business_accounts.py
import logging
from vkbottle.bot import Blueprint, MessageEvent
from vkbottle import GroupEventType, Keyboard, Text, KeyboardButtonColor
from db.database import db

logger = logging.getLogger(__name__)
bp = Blueprint("founder_business_accounts")


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
            logger.error(f"business_accounts edit: {e}")


async def show_account_event(event: MessageEvent, account_name: str, title: str):
    row = await db.fetchone("SELECT balance FROM system_accounts WHERE account_name = ?", account_name)
    balance = row["balance"] if row else 0
    text = f"💼 {title}\nБаланс: {balance} NK"
    kb = Keyboard(inline=True)
    kb.add(Text("🔙 Назад", payload={"cmd": "founder_business_accounts"}), color=KeyboardButtonColor.SECONDARY)
    await _edit_event(event, text, kb.get_json())


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_business_accounts_events(event: MessageEvent):
    payload = event.payload or {}
    cmd = payload.get("cmd")

    if cmd == "founder_business_accounts":
        await event.show_snackbar(" ")
        from admin.project_leadership.keyboards.leadership_menu_keyboards import get_business_accounts_keyboard
        accounts = await db.fetchall("SELECT * FROM system_accounts ORDER BY id")
        lines = ["💼 Бизнес основателя"]
        for acc in accounts:
            lines.append(f"  {acc['account_name']}: {acc['balance']} NK")
        await _edit_event(event, "\n".join(lines), get_business_accounts_keyboard())

    elif cmd == "business_account_emission":
        await event.show_snackbar(" ")
        await show_account_event(event, "emission", "Эмиссионный счёт")

    elif cmd == "business_account_commission":
        await event.show_snackbar(" ")
        await show_account_event(event, "commission", "Комиссионный счёт")

    elif cmd == "business_account_lottery":
        await event.show_snackbar(" ")
        await show_account_event(event, "lottery", "Счёт лотереи")

    elif cmd == "business_account_investment":
        await event.show_snackbar(" ")
        await show_account_event(event, "investment", "Инвестиционный счёт")

    elif cmd == "business_account_giveaways":
        await event.show_snackbar(" ")
        await show_account_event(event, "giveaways", "Счёт раздач")

    elif cmd == "business_account_salary":
        await event.show_snackbar(" ")
        await show_account_event(event, "salary", "Зарплатный счёт")