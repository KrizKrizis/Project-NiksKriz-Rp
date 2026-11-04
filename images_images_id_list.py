# images/images_id_list.py
# Реестр фото. Ключ = ID из БД (совпадает с business_id/housing_id/vehicle_id/job_id/city_id).
# Имя файла = {english_category}_{english_name}_{item_id}.{ext}
# Attachment заполняется после загрузки фото в ВК через upload_photos.py

IMAGES = {
    # ============================================================
    # БАНКИ (2.5.x)
    # ============================================================
    # "2.5.1": {"attachment": "photo-XXX_YYY", "name": "NK Bank",     "file": "bank_nk_2.5.1.jpg"},
    # "2.5.2": {"attachment": "photo-XXX_YYY", "name": "Zero Bank",   "file": "bank_zero_2.5.2.jpg"},
    # "2.5.3": {"attachment": "photo-XXX_YYY", "name": "Fallen Bank", "file": "bank_fallen_2.5.3.jpg"},

    # ============================================================
    # БИЗНЕСЫ (2.1.x – 2.4.x)
    # ============================================================
    # 2.1 — Новичковые
    # "2.1.1": {"attachment": "photo-XXX_YYY", "name": "Завод",        "file": "business_zavod_2.1.1.jpg"},
    # "2.1.2": {"attachment": "photo-XXX_YYY", "name": "Ферма",        "file": "business_farm_2.1.2.jpg"},
    # "2.1.3": {"attachment": "photo-XXX_YYY", "name": "Шахта",        "file": "business_mine_2.1.3.jpg"},
    # "2.1.4": {"attachment": "photo-XXX_YYY", "name": "Каменоломня",  "file": "business_quarry_2.1.4.jpg"},
    # 2.2 — Следующие
    # "2.2.1": {"attachment": "photo-XXX_YYY", "name": "Автобус Клуб",         "file": "business_busclub_2.2.1.jpg"},
    # "2.2.2": {"attachment": "photo-XXX_YYY", "name": "Авто Клуб",            "file": "business_autoclub_2.2.2.jpg"},
    # "2.2.3": {"attachment": "photo-XXX_YYY", "name": "Таксопарк",            "file": "business_taxi_2.2.3.jpg"},
    # "2.2.4": {"attachment": "photo-XXX_YYY", "name": "Курьерская Фирма",     "file": "business_courier_2.2.4.jpg"},
    # 2.3 — Продвинутые
    # "2.3.1": {"attachment": "photo-XXX_YYY", "name": "Airo Клуб",   "file": "business_airoclub_2.3.1.jpg"},
    # "2.3.2": {"attachment": "photo-XXX_YYY", "name": "Train Клуб",  "file": "business_trainclub_2.3.2.jpg"},
    # 2.4 — Элитные
    # "2.4.1": {"attachment": "photo-XXX_YYY", "name": "Казино «Золотое»",      "file": "business_casino_2.4.1.jpg"},
    # "2.4.2": {"attachment": "photo-XXX_YYY", "name": "Агентство недвижимости","file": "business_estate_2.4.2.jpg"},
    # "2.4.3": {"attachment": "photo-XXX_YYY", "name": "Фирма менеджеров",      "file": "business_managerfirm_2.4.3.jpg"},

    # ============================================================
    # БИЗНЕС ОСНОВАТЕЛЯ (2.6.x — системные счета)
    # ============================================================
    # "2.6.1": {"attachment": "photo-XXX_YYY", "name": "Эмиссионный счёт",     "file": "business_founder_emission_2.6.1.jpg"},
    # "2.6.2": {"attachment": "photo-XXX_YYY", "name": "Комиссионный счёт",    "file": "business_founder_commission_2.6.2.jpg"},
    # "2.6.3": {"attachment": "photo-XXX_YYY", "name": "Счёт лотереи",         "file": "business_founder_lottery_2.6.3.jpg"},
    # "2.6.4": {"attachment": "photo-XXX_YYY", "name": "Инвестиционный счёт",  "file": "business_founder_investment_2.6.4.jpg"},
    # "2.6.5": {"attachment": "photo-XXX_YYY", "name": "Счёт раздач",          "file": "business_founder_giveaways_2.6.5.jpg"},
    # "2.6.6": {"attachment": "photo-XXX_YYY", "name": "Зарплатный счёт",      "file": "business_founder_salary_2.6.6.jpg"},

    # ============================================================
    # ЖИЛЬЁ (3.x)
    # ============================================================
    # 3.1 — Квартиры
    # "3.1.1": {"attachment": "photo-XXX_YYY", "name": "Квартира-студия",         "file": "housing_studio_3.1.1.jpg"},
    # "3.1.2": {"attachment": "photo-XXX_YYY", "name": "Однокомнатная квартира",  "file": "housing_flat1_3.1.2.jpg"},
    # "3.1.3": {"attachment": "photo-XXX_YYY", "name": "Двухкомнатная квартира",  "file": "housing_flat2_3.1.3.jpg"},
    # "3.1.4": {"attachment": "photo-XXX_YYY", "name": "Трёхкомнатная квартира",  "file": "housing_flat3_3.1.4.jpg"},
    # 3.2 — Дома
    # "3.2.1": {"attachment": "photo-XXX_YYY", "name": "Одноэтажный дом", "file": "housing_house1_3.2.1.jpg"},
    # "3.2.2": {"attachment": "photo-XXX_YYY", "name": "Двухэтажный дом", "file": "housing_house2_3.2.2.jpg"},

    # ============================================================
    # ТРАНСПОРТ (4.1.x)
    # ============================================================
    # "4.1.1": {"attachment": "photo-XXX_YYY", "name": "Лада Нива",    "file": "vehicle_niva_4.1.1.jpg"},
    # "4.1.2": {"attachment": "photo-XXX_YYY", "name": "Toyota Camry", "file": "vehicle_camry_4.1.2.jpg"},
    # "4.1.3": {"attachment": "photo-XXX_YYY", "name": "BMW M5",       "file": "vehicle_bmw_4.1.3.jpg"},

    # ============================================================
    # РАБОТЫ (5.x)
    # ============================================================
    # 5.1 — Начальные
    # "5.1.1": {"attachment": "photo-XXX_YYY", "name": "Завод",     "file": "job_factory_5.1.1.jpg"},
    # "5.1.2": {"attachment": "photo-XXX_YYY", "name": "Ферма",     "file": "job_farm_5.1.2.jpg"},
    # "5.1.3": {"attachment": "photo-XXX_YYY", "name": "Шахта",     "file": "job_mine_5.1.3.jpg"},
    # "5.1.4": {"attachment": "photo-XXX_YYY", "name": "Каменщик",  "file": "job_mason_5.1.4.jpg"},
    # 5.2 — Постоянные
    # "5.2.1": {"attachment": "photo-XXX_YYY", "name": "Таксист",           "file": "job_taxi_5.2.1.jpg"},
    # "5.2.2": {"attachment": "photo-XXX_YYY", "name": "Курьер",            "file": "job_courier_5.2.2.jpg"},
    # "5.2.3": {"attachment": "photo-XXX_YYY", "name": "Водитель автобуса", "file": "job_busdriver_5.2.3.jpg"},
    # "5.2.4": {"attachment": "photo-XXX_YYY", "name": "Автомойщик",        "file": "job_carwash_5.2.4.jpg"},
    # "5.2.5": {"attachment": "photo-XXX_YYY", "name": "Машинист поезда",   "file": "job_train_5.2.5.jpg"},
    # "5.2.6": {"attachment": "photo-XXX_YYY", "name": "Пилот",             "file": "job_pilot_5.2.6.jpg"},
    # 5.3 — Миллионер
    # "5.3.1": {"attachment": "photo-XXX_YYY", "name": "Бизнесмен",  "file": "job_businessman_5.3.1.jpg"},
    # "5.3.2": {"attachment": "photo-XXX_YYY", "name": "Банкир",     "file": "job_banker_5.3.2.jpg"},
    # "5.3.3": {"attachment": "photo-XXX_YYY", "name": "Ростовщик",  "file": "job_usurer_5.3.3.jpg"},
    # 5.4 — Элитные
    # "5.4.1": {"attachment": "photo-XXX_YYY", "name": "Работа на Марсе", "file": "job_mars_5.4.1.jpg"},

    # ============================================================
    # ГОРОДА (6.x)
    # ============================================================
    # "6.1": {"attachment": "photo-XXX_YYY", "name": "Величие",     "file": "city_velichie_6.1.jpg"},
    # "6.2": {"attachment": "photo-XXX_YYY", "name": "Звездограцк", "file": "city_zvezdogratsk_6.2.jpg"},
    # "6.3": {"attachment": "photo-XXX_YYY", "name": "Мемград",     "file": "city_memgrad_6.3.jpg"},
}