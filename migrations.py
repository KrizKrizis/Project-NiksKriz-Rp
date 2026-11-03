# db/migrations.py
# Создание всех таблиц и заполнение базовыми данными из db.ids.

from db.database import db
from db.ids import (
    ALL_ITEMS, ALL_BUSINESSES, HOUSING, VEHICLES, JOBS, CITIES,
    FOUNDER_ACCOUNTS, RECIPES,
)


async def init_db():
    # ==================== ИГРОКИ ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            vk_id INTEGER PRIMARY KEY,
            game_id INTEGER UNIQUE NOT NULL,
            first_name TEXT NOT NULL DEFAULT '',
            last_name TEXT NOT NULL DEFAULT '',
            nickname TEXT DEFAULT NULL,
            accepted_terms INTEGER NOT NULL DEFAULT 0,
            balance INTEGER NOT NULL DEFAULT 0,
            crypto_balance REAL NOT NULL DEFAULT 0,
            casino_chips INTEGER NOT NULL DEFAULT 0,
            bank_name TEXT,
            bank_checking INTEGER NOT NULL DEFAULT 0,
            bank_savings INTEGER NOT NULL DEFAULT 0,
            tax_account INTEGER NOT NULL DEFAULT 0,
            level INTEGER NOT NULL DEFAULT 1,
            exp INTEGER NOT NULL DEFAULT 0,
            current_city TEXT NOT NULL DEFAULT 'Величие',
            reputation INTEGER NOT NULL DEFAULT 0,
            current_work TEXT,
            work_start_time TEXT,
            work_end_time TEXT,
            work_reward INTEGER,
            work_drop_data TEXT,
            last_exp_bonus_time TEXT,
            last_interest_time TEXT,
            is_blocked INTEGER NOT NULL DEFAULT 0,
            temporary_blocked_until TEXT,
            registration_date TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ==================== СОСТОЯНИЯ ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS user_states (
            user_id INTEGER PRIMARY KEY,
            state TEXT NOT NULL,
            data TEXT DEFAULT '{}',
            FOREIGN KEY (user_id) REFERENCES users(vk_id) ON DELETE CASCADE
        )
    """)

    # ==================== ТРАНЗАКЦИИ ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            amount INTEGER NOT NULL,
            currency TEXT DEFAULT 'NK',
            transaction_type TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ==================== ПРЕДМЕТЫ ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS items (
            item_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL DEFAULT 'resource',
            base_price INTEGER NOT NULL DEFAULT 0,
            stackable INTEGER NOT NULL DEFAULT 1
        )
    """)
    for item_id, data in ALL_ITEMS.items():
        await db.execute(
            "INSERT OR IGNORE INTO items (item_id, name, type, base_price, stackable) VALUES (?, ?, ?, ?, ?)",
            item_id, data["name"], data["type"], data["base_price"], data["stackable"]
        )

    await db.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            durability INTEGER DEFAULT 100,
            FOREIGN KEY (user_id) REFERENCES users(vk_id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
        )
    """)

    # ==================== ЖИЛЬЁ ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS housing (
            housing_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            price INTEGER NOT NULL,
            parking_spots INTEGER NOT NULL
        )
    """)
    for h_id, data in HOUSING.items():
        await db.execute(
            "INSERT OR IGNORE INTO housing (housing_id, name, type, price, parking_spots) VALUES (?, ?, ?, ?, ?)",
            h_id, data["name"], data["type"], data["price"], data["parking_spots"]
        )

    await db.execute("""
        CREATE TABLE IF NOT EXISTS player_housing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            housing_id TEXT NOT NULL,
            has_crypto_farm INTEGER NOT NULL DEFAULT 0,
            crypto_farm_installed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(vk_id) ON DELETE CASCADE,
            FOREIGN KEY (housing_id) REFERENCES housing(housing_id) ON DELETE CASCADE
        )
    """)

    # ==================== ТРАНСПОРТ ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            tank_capacity INTEGER NOT NULL,
            fuel_consumption REAL NOT NULL,
            mileage INTEGER NOT NULL DEFAULT 0,
            country TEXT NOT NULL DEFAULT 'Россия',
            type TEXT NOT NULL DEFAULT 'car'
        )
    """)
    for v_id, data in VEHICLES.items():
        await db.execute(
            "INSERT OR IGNORE INTO vehicles (vehicle_id, name, price, tank_capacity, fuel_consumption) VALUES (?, ?, ?, ?, ?)",
            v_id, data["name"], data["price"], data["tank_capacity"], data["fuel_consumption"]
        )

    await db.execute("""
        CREATE TABLE IF NOT EXISTS player_vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vehicle_id TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 0,
            fuel_amount REAL NOT NULL DEFAULT 0,
            mileage INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(vk_id) ON DELETE CASCADE,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE
        )
    """)

    # ==================== РАБОТЫ (ключ = slug) ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            base_reward_min INTEGER NOT NULL,
            base_reward_max INTEGER NOT NULL,
            duration_seconds INTEGER NOT NULL,
            level_required INTEGER NOT NULL DEFAULT 1,
            business_id TEXT
        )
    """)
    for job_slug, data in JOBS.items():
        await db.execute(
            "INSERT OR IGNORE INTO jobs (job_id, name, category, base_reward_min, base_reward_max, duration_seconds, level_required, business_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            job_slug, data["name"], data["category"], data["base_reward_min"],
            data["base_reward_max"], data["duration_seconds"], data["level_required"],
            data.get("business_id")
        )

    await db.execute("""
        CREATE TABLE IF NOT EXISTS work_settings (
            job_id TEXT PRIMARY KEY,
            reward_min INTEGER NOT NULL,
            reward_max INTEGER NOT NULL,
            FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS work_bonuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            chance REAL NOT NULL,
            check_interval_minutes INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
        )
    """)

    # ==================== КРАФТ ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS craft_recipes (
            recipe_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            success_chance REAL NOT NULL,
            result_item_id TEXT NOT NULL,
            result_quantity INTEGER NOT NULL DEFAULT 1
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS craft_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            is_tool INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Заполняем рецепты (удаляем старые ингредиенты, чтобы не дублировались)
    for r_id, data in RECIPES.items():
        item_name = ALL_ITEMS.get(data["result_item_id"], {}).get("name", "Неизвестно")
        await db.execute(
            "INSERT OR IGNORE INTO craft_recipes (recipe_id, name, duration_minutes, success_chance, result_item_id, result_quantity) VALUES (?, ?, ?, ?, ?, 1)",
            r_id, item_name, data["duration_minutes"], data["success_chance"], data["result_item_id"]
        )
        await db.execute("DELETE FROM craft_ingredients WHERE recipe_id = ?", r_id)
        for ing in data["ingredients"]:
            await db.execute(
                "INSERT INTO craft_ingredients (recipe_id, item_id, quantity, is_tool) VALUES (?, ?, ?, ?)",
                r_id, ing[0], ing[1], ing[2]
            )

    await db.execute("""
        CREATE TABLE IF NOT EXISTS active_crafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recipe_id TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        )
    """)

    # ==================== БИЗНЕСЫ ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
            business_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT,
            shop_price INTEGER NOT NULL DEFAULT 0,
            city TEXT,
            owner_id INTEGER,
            income_min INTEGER NOT NULL,
            income_max INTEGER NOT NULL,
            product_cost INTEGER NOT NULL DEFAULT 0,
            tax_amount INTEGER NOT NULL DEFAULT 0,
            special_income_type TEXT DEFAULT 'none',
            business_balance INTEGER NOT NULL DEFAULT 0,
            is_on_auction INTEGER NOT NULL DEFAULT 0,
            current_bid_user_id INTEGER,
            current_bid_amount INTEGER,
            commission_rate REAL DEFAULT 0.0,
            auction_owner_id INTEGER,
            auction_start_time TEXT,
            auction_end_time TEXT,
            last_bid_time TEXT,
            hidden INTEGER DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    for b_id, data in ALL_BUSINESSES.items():
        await db.execute(
            """INSERT OR IGNORE INTO businesses
               (business_id, name, type, category, shop_price, income_min, income_max,
                product_cost, tax_amount, special_income_type, commission_rate, hidden,
                is_on_auction, current_bid_amount)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)""",
            b_id, data["name"], data["type"], data.get("category"),
            data.get("shop_price", 0),
            data["income_min"], data["income_max"],
            data["product_cost"], data["tax_amount"],
            data.get("special_income_type", "none"),
            data.get("commission_rate", 0.0),
            data.get("hidden", 0),
            data.get("start_price", 0)
        )

    await db.execute("""
        CREATE TABLE IF NOT EXISTS business_managers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id TEXT NOT NULL,
            manager_type TEXT NOT NULL,
            manager_user_id INTEGER,
            salary INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'active',
            hired_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS manager_reputation (
            user_id INTEGER PRIMARY KEY,
            reputation INTEGER NOT NULL DEFAULT 50,
            boss_reputation INTEGER NOT NULL DEFAULT 50,
            FOREIGN KEY (user_id) REFERENCES users(vk_id) ON DELETE CASCADE
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS director_elections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            voter_id INTEGER NOT NULL,
            voted_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS auction_bids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            bid_time TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ==================== САД И ФЕРМА ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS garden_plots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plot_number INTEGER NOT NULL,
            capacity INTEGER NOT NULL DEFAULT 25
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS garden_plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plot_number INTEGER NOT NULL,
            slot_number INTEGER NOT NULL,
            plant_type TEXT NOT NULL,
            seed_item_id TEXT NOT NULL,
            planted_at TEXT NOT NULL,
            water_required_by TEXT,
            harvest_ready_at TEXT,
            can_harvest INTEGER NOT NULL DEFAULT 0,
            is_tree INTEGER NOT NULL DEFAULT 0
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS crypto_farm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            videocard_id TEXT NOT NULL,
            installed_at TEXT NOT NULL
        )
    """)

    # ==================== КРИПТОБИРЖА ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS exchange_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(vk_id) ON DELETE CASCADE
        )
    """)

    # ==================== КАЗИНО, ЛОТЕРЕЯ, МАРС, NKVITO ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS casino_bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_type TEXT NOT NULL,
            bet_amount INTEGER NOT NULL,
            result_amount INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS nkvito_listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            item_id TEXT,
            price INTEGER NOT NULL,
            listing_duration_days INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            expires_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS lottery_draws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draw_time TEXT NOT NULL,
            total_pool INTEGER NOT NULL DEFAULT 0,
            winners TEXT,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS lottery_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            draw_id INTEGER NOT NULL,
            ticket_count INTEGER NOT NULL DEFAULT 1,
            purchased_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS mars_investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            invested_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ==================== ГОРОДА ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            city_id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    """)
    for c_id, data in CITIES.items():
        await db.execute(
            "INSERT OR IGNORE INTO cities (city_id, name, description) VALUES (?, ?, ?)",
            c_id, data["name"], data["description"]
        )

    # ==================== АДМИНИСТРАЦИЯ ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS admin_roles (
            user_id INTEGER PRIMARY KEY,
            category INTEGER NOT NULL,
            position TEXT NOT NULL,
            permissions TEXT DEFAULT '{}',
            assigned_by INTEGER NOT NULL,
            assigned_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(vk_id) ON DELETE CASCADE
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS admin_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (admin_id) REFERENCES users(vk_id) ON DELETE CASCADE
        )
    """)

    # ==================== СИСТЕМНЫЕ СЧЕТА ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS system_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT UNIQUE NOT NULL,
            balance INTEGER NOT NULL DEFAULT 0,
            description TEXT
        )
    """)
    for acc_name in FOUNDER_ACCOUNTS:
        await db.execute(
            "INSERT OR IGNORE INTO system_accounts (account_name, balance) VALUES (?, 0)",
            acc_name
        )

    # ==================== НАСТРОЙКИ (CONFIG) ====================
    await db.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT
        )
    """)
    defaults = {
        "crypto_to_nk_rate": ("10", "Курс крипты к NK"),
        "weekly_shop_purchase_multiplier": ("5", "Множитель скупщика"),
        "exchange_rate_variation_percent": ("2", "Вариация биржи"),
        "photos_enabled": ("0", "Показ фото объектов (0 = выкл, 1 = вкл)"),
    }
    for key, (value, desc) in defaults.items():
        await db.execute(
            "INSERT OR IGNORE INTO config (key, value, description) VALUES (?, ?, ?)",
            key, value, desc
        )

    await db.execute("""
        CREATE TABLE IF NOT EXISTS chat_config (
            chat_mode INTEGER PRIMARY KEY,
            chat_id INTEGER NOT NULL,
            description TEXT
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS promocodes (
            code TEXT PRIMARY KEY,
            reward_type TEXT NOT NULL,
            reward_id TEXT,
            reward_amount INTEGER,
            uses_left INTEGER NOT NULL,
            expires_at TEXT
        )
    """)

    await db.commit()