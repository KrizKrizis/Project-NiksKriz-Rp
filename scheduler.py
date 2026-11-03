# services/scheduler.py
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def lottery_draw_job():
    from lottery.handlers.lottery_handlers import process_finished_draws
    await process_finished_draws()


async def savings_interest_job():
    from services.bank_service import apply_savings_interest_to_all
    await apply_savings_interest_to_all()


async def auction_incomes_job():
    from services.business_service import collect_all_auction_incomes
    await collect_all_auction_incomes()


async def personal_incomes_job():
    from services.business_service import collect_all_personal_incomes
    await collect_all_personal_incomes()


async def products_job():
    from services.business_service import pay_all_products
    await pay_all_products()


async def taxes_job():
    from services.business_service import pay_all_taxes
    await pay_all_taxes()


async def auctions_check_job():
    from services.auction_service import check_and_finish_auctions
    await check_and_finish_auctions()


async def manager_salaries_job():
    from services.business_service import process_all_manager_salaries
    await process_all_manager_salaries()


async def director_election_job():
    from services.business_service import maybe_elect_director, remove_director_if_bad
    await maybe_elect_director()
    await remove_director_if_bad()


async def emission_job():
    """Эмиссионный счёт: каждые 3 часа 500к–1.5кк NK."""
    import random
    from db.database import db
    amount = random.randint(500_000, 1_500_000)
    await db.execute(
        "UPDATE system_accounts SET balance = balance + ? WHERE account_name = 'emission'",
        amount
    )


async def casino_income_job():
    from services.casino_service import distribute_casino_income
    await distribute_casino_income()


async def exchange_pending_job():
    from services.shop_service import process_exchange_pending
    await process_exchange_pending()


async def nkvito_expire_job():
    from services.nkvito_service import check_expired_listings
    await check_expired_listings()


async def unlock_temporary_blocks_job():
    """Снимает временные блокировки с истёкшим сроком."""
    from datetime import datetime, timezone
    from db.database import db
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "UPDATE users SET is_blocked = 0, temporary_blocked_until = NULL "
        "WHERE is_blocked = 1 AND temporary_blocked_until IS NOT NULL AND temporary_blocked_until < ?",
        now
    )


def init_scheduler():
    logger.info("Инициализация планировщика...")

    scheduler.add_job(lottery_draw_job, 'cron', minute=0, id='lottery_draw', replace_existing=True)
    scheduler.add_job(savings_interest_job, 'cron', minute=0, id='savings_interest', replace_existing=True)
    scheduler.add_job(auction_incomes_job, 'cron', hour='*/3', minute=0, id='auction_incomes', replace_existing=True)
    scheduler.add_job(personal_incomes_job, 'cron', hour='*/6', minute=0, id='personal_incomes', replace_existing=True)
    scheduler.add_job(products_job, 'cron', hour='*/6', minute=0, id='products', replace_existing=True)
    scheduler.add_job(taxes_job, 'cron', hour='*/12', minute=0, id='taxes', replace_existing=True)
    scheduler.add_job(auctions_check_job, 'interval', minutes=1, id='auctions_check', replace_existing=True)
    scheduler.add_job(manager_salaries_job, 'cron', hour='*/6', minute=0, id='manager_salaries', replace_existing=True)
    scheduler.add_job(director_election_job, 'interval', hours=24, id='director_election', replace_existing=True)
    scheduler.add_job(emission_job, 'cron', hour='*/3', minute=0, id='emission', replace_existing=True)
    scheduler.add_job(casino_income_job, 'cron', minute=0, id='casino_income', replace_existing=True)
    scheduler.add_job(exchange_pending_job, 'cron', minute='*/10', id='exchange_pending', replace_existing=True)
    scheduler.add_job(nkvito_expire_job, 'cron', minute='*/5', id='nkvito_expire', replace_existing=True)
    scheduler.add_job(unlock_temporary_blocks_job, 'cron', minute='*/5', id='unlock_blocks', replace_existing=True)

    scheduler.start()
    logger.info("Планировщик запущен.")