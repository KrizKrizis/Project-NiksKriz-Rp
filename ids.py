# db/ids.py
# Единый реестр всех ID в проекте.
# Структура:
#   1.x  — предметы (1.1 Base, 1.2 Blue, 1.3 Purple, 1.4 Red, 1.5 Gold, 1.6 Урожай, 1.8 Спец)
#   2.1  — магазинные novice
#   2.2  — магазинные experienced
#   2.3  — магазинные millionaire
#   2.4  — ВСЕ аукционные 
#   3.x  — жильё
#   4.x  — транспорт
#   5.x  — города
#   Работы — без ID, ключ = slug. Привязка к бизнесу через business_id.

# ============================================================
# БЛОК 1 — ПРЕДМЕТЫ
# ============================================================

# 1.1 — Base (дроп с работ + крафт)
ITEMS_BASE = {
    "1.1.1":  {"name": "Камень", "type": "resource", "base_price": 5, "stackable": 1},
    "1.1.2":  {"name": "Железо", "type": "resource", "base_price": 20, "stackable": 1},
    "1.1.3":  {"name": "Медь", "type": "resource", "base_price": 15, "stackable": 1},
    "1.1.4":  {"name": "Уголь", "type": "resource", "base_price": 10, "stackable": 1},
    "1.1.5":  {"name": "Золото", "type": "resource", "base_price": 100, "stackable": 1},
    "1.1.6":  {"name": "Алмаз", "type": "resource", "base_price": 200, "stackable": 1},
    "1.1.7":  {"name": "Изумруд", "type": "resource", "base_price": 250, "stackable": 1},
    "1.1.8":  {"name": "Металл", "type": "resource", "base_price": 50, "stackable": 1},
    "1.1.9":  {"name": "Неизвестное семечко", "type": "resource", "base_price": 30, "stackable": 1},
    "1.1.10": {"name": "Еда", "type": "resource", "base_price": 20, "stackable": 1},
    "1.1.11": {"name": "Доски", "type": "resource", "base_price": 25, "stackable": 1},
    "1.1.12": {"name": "Дерево", "type": "resource", "base_price": 10, "stackable": 1},
    "1.1.13": {"name": "Пластик", "type": "resource", "base_price": 40, "stackable": 1},
    "1.1.14": {"name": "Стекло", "type": "resource", "base_price": 30, "stackable": 1},
    "1.1.15": {"name": "Ящик с инструментами", "type": "resource", "base_price": 100, "stackable": 1},
    "1.1.16": {"name": "Семена огурца", "type": "seed", "base_price": 50, "stackable": 1, "plant_type": "огурцы"},
    "1.1.17": {"name": "Семена помидора", "type": "seed", "base_price": 50, "stackable": 1, "plant_type": "помидоры"},
    "1.1.18": {"name": "Семена моркови", "type": "seed", "base_price": 50, "stackable": 1, "plant_type": "морковь"},
    "1.1.19": {"name": "Семена земляники", "type": "seed", "base_price": 80, "stackable": 1, "plant_type": "земляника"},
    "1.1.20": {"name": "Семена ежевики", "type": "seed", "base_price": 80, "stackable": 1, "plant_type": "ежевика"},
    "1.1.21": {"name": "Семена дыни", "type": "seed", "base_price": 100, "stackable": 1, "plant_type": "дыня"},
    "1.1.22": {"name": "Семена арбуза", "type": "seed", "base_price": 100, "stackable": 1, "plant_type": "арбуз"},
    "1.1.23": {"name": "Семена яблока", "type": "seed", "base_price": 200, "stackable": 1, "plant_type": "яблоко"},
    "1.1.24": {"name": "Семена вишни", "type": "seed", "base_price": 200, "stackable": 1, "plant_type": "вишня"},
    "1.1.25": {"name": "Семена груши", "type": "seed", "base_price": 200, "stackable": 1, "plant_type": "груша"},
    "1.1.26": {"name": "Семена мандарина", "type": "seed", "base_price": 250, "stackable": 1, "plant_type": "мандарин"},
    "1.1.27": {"name": "Картошка (семена)", "type": "seed", "base_price": 50, "stackable": 1, "plant_type": "картошка"},
    "1.1.28": {"name": "Топор", "type": "tool", "base_price": 500, "stackable": 0, "durability": 100},
}

# 1.2 — Blue (Uncommon)
ITEMS_BLUE = {
    "1.2.1":  {"name": "Каркас платы", "type": "craft", "base_price": 0, "stackable": 1},
    "1.2.2":  {"name": "Каркас ангара", "type": "craft", "base_price": 0, "stackable": 1},
    "1.2.3":  {"name": "Каркас космического корабля (деревянный)", "type": "craft", "base_price": 0, "stackable": 1},
    "1.2.4":  {"name": "Каркас марсохода (деревянный)", "type": "craft", "base_price": 0, "stackable": 1},
    "1.2.5":  {"name": "Пустой баллон", "type": "craft", "base_price": 0, "stackable": 1},
    "1.2.6":  {"name": "Компьютер", "type": "craft", "base_price": 0, "stackable": 1},
    "1.2.7":  {"name": "Медные трубы", "type": "craft", "base_price": 0, "stackable": 1},
    "1.2.8":  {"name": "Резина", "type": "craft", "base_price": 0, "stackable": 1},
    "1.2.9":  {"name": "Компрессор", "type": "craft", "base_price": 0, "stackable": 1},
    "1.2.11": {"name": "Кислородный баллон", "type": "craft", "base_price": 0, "stackable": 1},
}

# 1.3 — Purple (Rare)
ITEMS_PURPLE = {
    "1.3.1":  {"name": "Плата", "type": "craft", "base_price": 0, "stackable": 1},
    "1.3.2":  {"name": "Металлический ангар", "type": "craft", "base_price": 0, "stackable": 1},
    "1.3.3":  {"name": "Металлический марсоход", "type": "craft", "base_price": 0, "stackable": 1},
    "1.3.4":  {"name": "Металлический космический корабль", "type": "craft", "base_price": 0, "stackable": 1},
    "1.3.5":  {"name": "Усовершенствованный металл", "type": "craft", "base_price": 0, "stackable": 1},
    "1.3.6":  {"name": "Биотопливо", "type": "craft", "base_price": 0, "stackable": 1},
    "1.3.7":  {"name": "Квантовый компьютер", "type": "craft", "base_price": 0, "stackable": 1},
    "1.3.8":  {"name": "Металлические трубы", "type": "craft", "base_price": 0, "stackable": 1},
    "1.3.9":  {"name": "Шины", "type": "craft", "base_price": 0, "stackable": 1},
    "1.3.10": {"name": "Скафандр", "type": "craft", "base_price": 0, "stackable": 1},
}

# 1.4 — Red (Epic)
ITEMS_RED = {
    "1.4.1": {"name": "Система управления без ИИ", "type": "craft", "base_price": 0, "stackable": 1},
    "1.4.2": {"name": "Улучшенный ангар", "type": "craft", "base_price": 0, "stackable": 1},
    "1.4.3": {"name": "Улучшенный каркас космического корабля", "type": "craft", "base_price": 0, "stackable": 1},
    "1.4.4": {"name": "Улучшенный каркас марсохода", "type": "craft", "base_price": 0, "stackable": 1},
    "1.4.5": {"name": "Космическое топливо", "type": "craft", "base_price": 0, "stackable": 1},
    "1.4.6": {"name": "ИИ", "type": "craft", "base_price": 0, "stackable": 1},
    "1.4.7": {"name": "Усовершенствованные трубы", "type": "craft", "base_price": 0, "stackable": 1},
    "1.4.8": {"name": "Усовершенствованные шины", "type": "craft", "base_price": 0, "stackable": 1},
}

# 1.5 — Gold (Legendary)
ITEMS_GOLD = {
    "1.5.1": {"name": "Система управления с ИИ", "type": "craft", "base_price": 0, "stackable": 1},
    "1.5.2": {"name": "СОЖ", "type": "craft", "base_price": 0, "stackable": 1},
    "1.5.3": {"name": "Космический корабль", "type": "craft", "base_price": 0, "stackable": 1},
    "1.5.4": {"name": "Марсоход", "type": "craft", "base_price": 0, "stackable": 1},
}

# 1.6 — Урожай (сдаётся скупщику)
ITEMS_HARVEST = {
    "1.6.1":  {"name": "Огурец", "type": "harvest", "base_price": 15, "stackable": 1, "min_batch": 20},
    "1.6.2":  {"name": "Помидор", "type": "harvest", "base_price": 15, "stackable": 1, "min_batch": 20},
    "1.6.3":  {"name": "Морковь", "type": "harvest", "base_price": 15, "stackable": 1, "min_batch": 20},
    "1.6.4":  {"name": "Земляника", "type": "harvest", "base_price": 25, "stackable": 1, "min_batch": 20},
    "1.6.5":  {"name": "Ежевика", "type": "harvest", "base_price": 25, "stackable": 1, "min_batch": 20},
    "1.6.6":  {"name": "Дыня", "type": "harvest", "base_price": 30, "stackable": 1, "min_batch": 20},
    "1.6.7":  {"name": "Арбуз", "type": "harvest", "base_price": 30, "stackable": 1, "min_batch": 20},
    "1.6.8":  {"name": "Яблоко", "type": "harvest", "base_price": 40, "stackable": 1, "min_batch": 100},
    "1.6.9":  {"name": "Вишня", "type": "harvest", "base_price": 40, "stackable": 1, "min_batch": 100},
    "1.6.10": {"name": "Груша", "type": "harvest", "base_price": 40, "stackable": 1, "min_batch": 100},
    "1.6.11": {"name": "Мандарин", "type": "harvest", "base_price": 50, "stackable": 1, "min_batch": 100},
    "1.6.12": {"name": "Картофель", "type": "harvest", "base_price": 15, "stackable": 1, "min_batch": 20},
}

# 1.8 — Спец-предметы (награда за Марс)
ITEMS_SPECIAL = {
    "1.8.1": {"name": "База на Марсе", "type": "special", "base_price": 0, "stackable": 0},
}

ALL_ITEMS = {
    **ITEMS_BASE, **ITEMS_BLUE, **ITEMS_PURPLE, **ITEMS_RED,
    **ITEMS_GOLD, **ITEMS_HARVEST, **ITEMS_SPECIAL,
}

# ============================================================
# БЛОК 2 — БИЗНЕСЫ
# ============================================================

# 2.1 — Магазинные novice
BUSINESSES_SHOP_NOVICE = {
    "2.1.1": {"name": "Ларёк с хот-догами", "type": "shop", "category": "novice", "shop_price": 50_000, "income_min": 5_000, "income_max": 25_000, "product_cost": 0, "tax_amount": 100_000},
    "2.1.2": {"name": "Шаурмечная", "type": "shop", "category": "novice", "shop_price": 100_000, "income_min": 15_000, "income_max": 45_000, "product_cost": 0, "tax_amount": 100_000},
}

# 2.2 — Магазинные experienced
BUSINESSES_SHOP_EXPERIENCED = {
    "2.2.1": {"name": "Фастфуд 1", "type": "shop", "category": "experienced", "shop_price": 250_000, "income_min": 55_000, "income_max": 125_000, "product_cost": 0, "tax_amount": 100_000},
    "2.2.2": {"name": "Фастфуд 2", "type": "shop", "category": "experienced", "shop_price": 250_000, "income_min": 55_000, "income_max": 125_000, "product_cost": 0, "tax_amount": 100_000},
}

# 2.3 — Магазинные millionaire
BUSINESSES_SHOP_MILLIONAIRE = {
    "2.3.1": {"name": "Ветряные мельницы", "type": "shop", "category": "millionaire", "shop_price": 300_000, "income_min": 75_000, "income_max": 225_000, "product_cost": 22_500, "tax_amount": 100_000},
    "2.3.2": {"name": "Заправка 1", "type": "shop", "category": "millionaire", "shop_price": 350_000, "income_min": 85_000, "income_max": 225_000, "product_cost": 23_250, "tax_amount": 100_000},
    "2.3.3": {"name": "Заправка 2", "type": "shop", "category": "millionaire", "shop_price": 350_000, "income_min": 85_000, "income_max": 225_000, "product_cost": 23_250, "tax_amount": 100_000},
    "2.3.4": {"name": "Компьютерный центр", "type": "shop", "category": "millionaire", "shop_price": 450_000, "income_min": 100_000, "income_max": 325_000, "product_cost": 31_875, "tax_amount": 100_000},
}

# 2.4 — ВСЕ аукционные
BUSINESSES_AUCTION = {
    "2.4.1":  {"name": "Завод", "type": "auction_standard", "income_min": 450_000, "income_max": 750_000, "product_cost": 150_000, "tax_amount": 100_000, "start_price": 500_000},
    "2.4.2":  {"name": "Ферма", "type": "auction_standard", "income_min": 450_000, "income_max": 750_000, "product_cost": 150_000, "tax_amount": 100_000, "start_price": 500_000},
    "2.4.3":  {"name": "Шахта", "type": "auction_standard", "income_min": 450_000, "income_max": 750_000, "product_cost": 150_000, "tax_amount": 100_000, "start_price": 500_000},
    "2.4.4":  {"name": "Каменоломня", "type": "auction_standard", "income_min": 450_000, "income_max": 750_000, "product_cost": 150_000, "tax_amount": 100_000, "start_price": 500_000},
    "2.4.5":  {"name": "Автобус Клуб", "type": "auction_standard", "income_min": 450_000, "income_max": 1_000_000, "product_cost": 150_000, "tax_amount": 100_000, "start_price": 500_000},
    "2.4.6":  {"name": "Авто Клуб", "type": "auction_standard", "income_min": 450_000, "income_max": 1_000_000, "product_cost": 150_000, "tax_amount": 100_000, "start_price": 500_000, "special_income_type": "auto_sale_percent"},
    "2.4.7":  {"name": "Таксопарк", "type": "auction_standard", "income_min": 450_000, "income_max": 1_000_000, "product_cost": 150_000, "tax_amount": 100_000, "start_price": 500_000},
    "2.4.8":  {"name": "Курьерская Фирма", "type": "auction_standard", "income_min": 450_000, "income_max": 1_000_000, "product_cost": 150_000, "tax_amount": 100_000, "start_price": 500_000},
    "2.4.9":  {"name": "Airo Клуб", "type": "auction_standard", "income_min": 500_000, "income_max": 1_200_000, "product_cost": 150_000, "tax_amount": 100_000, "start_price": 500_000},
    "2.4.10": {"name": "Train Клуб", "type": "auction_standard", "income_min": 500_000, "income_max": 1_200_000, "product_cost": 150_000, "tax_amount": 100_000, "start_price": 500_000},
    "2.4.11": {"name": "Казино «Золотое»", "type": "auction_casino", "income_min": 250_000, "income_max": 800_000, "product_cost": 150_000, "tax_amount": 150_000, "start_price": 2_000_000, "special_income_type": "casino_share", "hidden": 0},
    "2.4.12": {"name": "Zero Bank", "type": "auction_standard", "income_min": 500_000, "income_max": 1_200_000, "product_cost": 150_000, "tax_amount": 100_000, "start_price": 500_000, "special_income_type": "bank_commission", "commission_rate": 0.0},
    "2.4.13": {"name": "Fallen Bank", "type": "auction_standard", "income_min": 500_000, "income_max": 1_200_000, "product_cost": 150_000, "tax_amount": 100_000, "start_price": 500_000, "special_income_type": "bank_commission", "commission_rate": 0.0},
    "2.4.14": {"name": "Агентство недвижимости", "type": "auction_standard", "income_min": 500_000, "income_max": 1_200_000, "product_cost": 150_000, "tax_amount": 100_000, "start_price": 500_000, "special_income_type": "estate_sale_percent"},
    "2.4.15": {"name": "Фирма менеджеров", "type": "auction_standard", "income_min": 500_000, "income_max": 1_200_000, "product_cost": 150_000, "tax_amount": 100_000, "start_price": 500_000, "special_income_type": "manager_firm"},
}

ALL_BUSINESSES = {
    **BUSINESSES_SHOP_NOVICE,
    **BUSINESSES_SHOP_EXPERIENCED,
    **BUSINESSES_SHOP_MILLIONAIRE,
    **BUSINESSES_AUCTION,
}

# ============================================================
# БЛОК 3 — ЖИЛЬЁ
# ============================================================
HOUSING = {
    "3.1.1": {"name": "Квартира-студия", "type": "apartment", "price": 1_500_000, "parking_spots": 1},
    "3.1.2": {"name": "Однокомнатная квартира", "type": "apartment", "price": 800_000, "parking_spots": 1},
    "3.1.3": {"name": "Двухкомнатная квартира", "type": "apartment", "price": 1_200_000, "parking_spots": 2},
    "3.1.4": {"name": "Трёхкомнатная квартира", "type": "apartment", "price": 2_000_000, "parking_spots": 3},
    "3.2.1": {"name": "Одноэтажный дом", "type": "house", "price": 5_000_000, "parking_spots": 5},
    "3.2.2": {"name": "Двухэтажный дом", "type": "house", "price": 10_000_000, "parking_spots": 10},
}

# ============================================================
# БЛОК 4 — ТРАНСПОРТ
# ============================================================
VEHICLES = {
    "4.1.1": {"name": "Лада Нива", "price": 400_000, "tank_capacity": 50, "fuel_consumption": 8.0},
    "4.1.2": {"name": "Toyota Camry", "price": 2_500_000, "tank_capacity": 60, "fuel_consumption": 10.5},
    "4.1.3": {"name": "BMW M5", "price": 8_000_000, "tank_capacity": 70, "fuel_consumption": 15.0},
}

# ============================================================
# БЛОК 5 — ГОРОДА
# ============================================================
CITIES = {
    "5.1": {"name": "Величие", "description": "Стартовый город"},
    "5.2": {"name": "Звездограцк", "description": "Город инвестиций"},
    "5.3": {"name": "Мемград", "description": "Город казино"},
}

# ============================================================
# РАБОТЫ — БЕЗ ID, КЛЮЧ = SLUG
# ============================================================
JOBS = {
    "factory":    {"name": "🏭 Завод",             "category": "novice",      "base_reward_min": 100,    "base_reward_max": 250,    "duration_seconds": 60,    "level_required": 1,  "business_id": "2.4.1"},
    "farm":       {"name": "🌾 Ферма",             "category": "novice",      "base_reward_min": 200,    "base_reward_max": 450,    "duration_seconds": 60,    "level_required": 1,  "business_id": "2.4.2"},
    "mine":       {"name": "⛏ Шахта",             "category": "novice",      "base_reward_min": 200,    "base_reward_max": 350,    "duration_seconds": 60,    "level_required": 1,  "business_id": "2.4.3"},
    "stonemason": {"name": "🧱 Каменщик",          "category": "novice",      "base_reward_min": 45_000, "base_reward_max": 75_000, "duration_seconds": 10800, "level_required": 1,  "business_id": "2.4.4"},
    "taxi":       {"name": "🚕 Таксист",           "category": "permanent",   "base_reward_min": 2500,   "base_reward_max": 5000,   "duration_seconds": 600,   "level_required": 3,  "business_id": "2.4.7"},
    "courier":    {"name": "📦 Курьер",            "category": "permanent",   "base_reward_min": 2500,   "base_reward_max": 25_000, "duration_seconds": 600,   "level_required": 3,  "business_id": "2.4.8"},
    "bus_driver": {"name": "🚌 Водитель автобуса", "category": "permanent",   "base_reward_min": 25_000, "base_reward_max": 35_000, "duration_seconds": 600,   "level_required": 3,  "business_id": "2.4.5"},
    "trucker":    {"name": "🚛 Дальнобойщик",      "category": "permanent",   "base_reward_min": 50_000, "base_reward_max": 150_000,"duration_seconds": 1200,  "level_required": 3,  "business_id": "2.4.6"},
    "machinist":  {"name": "🚂 Машинист",          "category": "millionaire", "base_reward_min": 60_000, "base_reward_max": 100_000,"duration_seconds": 1500,  "level_required": 10, "business_id": "2.4.10"},
    "pilot":      {"name": "✈️ Пилот",             "category": "millionaire", "base_reward_min": 75_000, "base_reward_max": 200_000,"duration_seconds": 1800,  "level_required": 10, "business_id": "2.4.9"},
    "mars":       {"name": "🚀 Работа на Марсе",   "category": "elite",       "base_reward_min": 300_000,"base_reward_max": 500_000,"duration_seconds": 3600,  "level_required": 49, "business_id": None},
}

# ============================================================
# СЧЕТА ОСНОВАТЕЛЯ — БЕЗ ID, ТОЛЬКО ИМЕНА
# ============================================================
FOUNDER_ACCOUNTS = [
    "emission", "commission", "lottery", "investment", "giveaways", "salary",
]

# ============================================================
# РЕЦЕПТЫ КРАФТА
# Формат: "recipe_id": {"result_item_id", "duration_minutes", "success_chance", "ingredients": [(item_id, qty, is_tool)]}
# ============================================================
RECIPES = {
    # Base
    "r_1.1.4":  {"result_item_id": "1.1.4",  "duration_minutes": 1, "success_chance": 0.30, "ingredients": [("1.1.1", 5, 0)]},
    "r_1.1.2":  {"result_item_id": "1.1.2",  "duration_minutes": 1, "success_chance": 0.25, "ingredients": [("1.1.1", 5, 0)]},
    "r_1.1.3":  {"result_item_id": "1.1.3",  "duration_minutes": 1, "success_chance": 0.20, "ingredients": [("1.1.1", 5, 0)]},
    "r_1.1.5":  {"result_item_id": "1.1.5",  "duration_minutes": 1, "success_chance": 0.10, "ingredients": [("1.1.1", 5, 0)]},
    "r_1.1.6":  {"result_item_id": "1.1.6",  "duration_minutes": 1, "success_chance": 0.07, "ingredients": [("1.1.1", 5, 0)]},
    "r_1.1.7":  {"result_item_id": "1.1.7",  "duration_minutes": 1, "success_chance": 0.05, "ingredients": [("1.1.1", 5, 0)]},
    "r_1.1.11": {"result_item_id": "1.1.11", "duration_minutes": 1, "success_chance": 1.00, "ingredients": [("1.1.12", 1, 0)]},

    # Seeds
    "r_1.1.16": {"result_item_id": "1.1.16", "duration_minutes": 1, "success_chance": 0.11, "ingredients": [("1.1.9", 1, 0)]},
    "r_1.1.17": {"result_item_id": "1.1.17", "duration_minutes": 1, "success_chance": 0.11, "ingredients": [("1.1.9", 1, 0)]},
    "r_1.1.18": {"result_item_id": "1.1.18", "duration_minutes": 1, "success_chance": 0.11, "ingredients": [("1.1.9", 1, 0)]},
    "r_1.1.19": {"result_item_id": "1.1.19", "duration_minutes": 1, "success_chance": 0.11, "ingredients": [("1.1.9", 1, 0)]},
    "r_1.1.20": {"result_item_id": "1.1.20", "duration_minutes": 1, "success_chance": 0.11, "ingredients": [("1.1.9", 1, 0)]},
    "r_1.1.21": {"result_item_id": "1.1.21", "duration_minutes": 1, "success_chance": 0.08, "ingredients": [("1.1.9", 1, 0)]},
    "r_1.1.22": {"result_item_id": "1.1.22", "duration_minutes": 1, "success_chance": 0.08, "ingredients": [("1.1.9", 1, 0)]},
    "r_1.1.23": {"result_item_id": "1.1.23", "duration_minutes": 1, "success_chance": 0.06, "ingredients": [("1.1.9", 1, 0)]},
    "r_1.1.24": {"result_item_id": "1.1.24", "duration_minutes": 1, "success_chance": 0.06, "ingredients": [("1.1.9", 1, 0)]},
    "r_1.1.25": {"result_item_id": "1.1.25", "duration_minutes": 1, "success_chance": 0.06, "ingredients": [("1.1.9", 1, 0)]},
    "r_1.1.26": {"result_item_id": "1.1.26", "duration_minutes": 1, "success_chance": 0.06, "ingredients": [("1.1.9", 1, 0)]},
    "r_1.1.27": {"result_item_id": "1.1.27", "duration_minutes": 1, "success_chance": 0.06, "ingredients": [("1.1.9", 1, 0)]},

    # Blue
    "r_1.2.1":  {"result_item_id": "1.2.1",  "duration_minutes": 5, "success_chance": 0.40, "ingredients": [("1.1.13", 2, 0), ("1.1.3", 2, 0)]},
    "r_1.2.2":  {"result_item_id": "1.2.2",  "duration_minutes": 5, "success_chance": 0.15, "ingredients": [("1.1.11", 3, 0), ("1.1.2", 1, 0)]},
    "r_1.2.3":  {"result_item_id": "1.2.3",  "duration_minutes": 5, "success_chance": 0.15, "ingredients": [("1.1.11", 4, 0), ("1.1.2", 1, 0)]},
    "r_1.2.4":  {"result_item_id": "1.2.4",  "duration_minutes": 5, "success_chance": 0.15, "ingredients": [("1.1.11", 4, 0), ("1.1.2", 1, 0)]},
    "r_1.2.5":  {"result_item_id": "1.2.5",  "duration_minutes": 5, "success_chance": 0.40, "ingredients": [("1.1.8", 2, 0), ("1.1.4", 1, 0)]},
    "r_1.2.6":  {"result_item_id": "1.2.6",  "duration_minutes": 5, "success_chance": 0.40, "ingredients": [("1.1.13", 2, 0), ("1.1.3", 2, 0), ("1.1.14", 1, 0)]},
    "r_1.2.7":  {"result_item_id": "1.2.7",  "duration_minutes": 5, "success_chance": 0.40, "ingredients": [("1.1.3", 3, 0), ("1.1.4", 1, 0)]},
    "r_1.2.8":  {"result_item_id": "1.2.8",  "duration_minutes": 5, "success_chance": 0.40, "ingredients": [("1.1.4", 2, 0), ("1.1.13", 2, 0)]},
    "r_1.2.9":  {"result_item_id": "1.2.9",  "duration_minutes": 5, "success_chance": 0.15, "ingredients": [("1.1.8", 5, 0), ("1.1.13", 3, 0), ("1.1.3", 2, 0)]},
    "r_1.2.11": {"result_item_id": "1.2.11", "duration_minutes": 5, "success_chance": 1.00, "ingredients": [("1.2.5", 1, 0), ("1.2.9", 1, 1)]},

    # Purple
    "r_1.3.1":  {"result_item_id": "1.3.1",  "duration_minutes": 10, "success_chance": 0.30, "ingredients": [("1.2.1", 1, 0), ("1.1.5", 1, 0)]},
    "r_1.3.2":  {"result_item_id": "1.3.2",  "duration_minutes": 10, "success_chance": 0.12, "ingredients": [("1.2.2", 1, 0), ("1.1.8", 3, 0)]},
    "r_1.3.3":  {"result_item_id": "1.3.3",  "duration_minutes": 10, "success_chance": 0.12, "ingredients": [("1.2.4", 1, 0), ("1.1.8", 3, 0)]},
    "r_1.3.4":  {"result_item_id": "1.3.4",  "duration_minutes": 10, "success_chance": 0.12, "ingredients": [("1.2.3", 1, 0), ("1.1.8", 3, 0)]},
    "r_1.3.5":  {"result_item_id": "1.3.5",  "duration_minutes": 10, "success_chance": 0.12, "ingredients": [("1.1.8", 2, 0), ("1.1.6", 1, 0)]},
    "r_1.3.6":  {"result_item_id": "1.3.6",  "duration_minutes": 10, "success_chance": 0.12, "ingredients": [("1.1.10", 2, 0), ("1.1.4", 1, 0)]},
    "r_1.3.7":  {"result_item_id": "1.3.7",  "duration_minutes": 10, "success_chance": 0.12, "ingredients": [("1.2.6", 1, 0), ("1.1.5", 2, 0)]},
    "r_1.3.8":  {"result_item_id": "1.3.8",  "duration_minutes": 10, "success_chance": 0.12, "ingredients": [("1.2.7", 1, 0), ("1.1.8", 2, 0)]},
    "r_1.3.9":  {"result_item_id": "1.3.9",  "duration_minutes": 10, "success_chance": 0.12, "ingredients": [("1.2.8", 2, 0), ("1.1.8", 1, 0)]},
    "r_1.3.10": {"result_item_id": "1.3.10", "duration_minutes": 10, "success_chance": 0.08, "ingredients": [("1.2.11", 1, 0), ("1.2.8", 3, 0), ("1.1.14", 1, 0), ("1.1.8", 2, 0), ("1.2.7", 1, 0), ("1.3.1", 1, 0)]},

    # Red
    "r_1.4.1":  {"result_item_id": "1.4.1",  "duration_minutes": 15, "success_chance": 0.20, "ingredients": [("1.3.1", 1, 0), ("1.3.7", 1, 0)]},
    "r_1.4.2":  {"result_item_id": "1.4.2",  "duration_minutes": 15, "success_chance": 0.08, "ingredients": [("1.3.2", 1, 0), ("1.3.5", 1, 0)]},
    "r_1.4.3":  {"result_item_id": "1.4.3",  "duration_minutes": 15, "success_chance": 0.08, "ingredients": [("1.3.4", 1, 0), ("1.3.5", 1, 0)]},
    "r_1.4.4":  {"result_item_id": "1.4.4",  "duration_minutes": 15, "success_chance": 0.08, "ingredients": [("1.3.3", 1, 0), ("1.3.5", 1, 0)]},
    "r_1.4.5":  {"result_item_id": "1.4.5",  "duration_minutes": 15, "success_chance": 0.08, "ingredients": [("1.3.6", 1, 0), ("1.1.6", 1, 0)]},
    "r_1.4.6":  {"result_item_id": "1.4.6",  "duration_minutes": 15, "success_chance": 0.20, "ingredients": [("1.3.7", 1, 0), ("1.1.5", 2, 0), ("1.1.6", 1, 0)]},
    "r_1.4.7":  {"result_item_id": "1.4.7",  "duration_minutes": 15, "success_chance": 0.20, "ingredients": [("1.3.8", 1, 0), ("1.3.5", 1, 0)]},
    "r_1.4.8":  {"result_item_id": "1.4.8",  "duration_minutes": 15, "success_chance": 0.20, "ingredients": [("1.3.9", 1, 0), ("1.3.5", 1, 0)]},

    # Gold
    "r_1.5.1":  {"result_item_id": "1.5.1",  "duration_minutes": 60, "success_chance": 0.025, "ingredients": [("1.4.1", 1, 0), ("1.4.6", 1, 0)]},
    "r_1.5.2":  {"result_item_id": "1.5.2",  "duration_minutes": 60, "success_chance": 0.025, "ingredients": [("1.4.7", 2, 0), ("1.1.14", 3, 0), ("1.3.5", 2, 0)]},
    "r_1.5.3":  {"result_item_id": "1.5.3",  "duration_minutes": 60, "success_chance": 0.025, "ingredients": [("1.4.2", 1, 0), ("1.4.3", 1, 0), ("1.4.7", 2, 0), ("1.5.2", 1, 0), ("1.5.1", 1, 0), ("1.4.5", 3, 0)]},
    "r_1.5.4":  {"result_item_id": "1.5.4",  "duration_minutes": 60, "success_chance": 0.025, "ingredients": [("1.4.4", 1, 0), ("1.5.2", 1, 0), ("1.4.8", 4, 0), ("1.4.5", 2, 0)]},
}