# utils/images.py
from images.images_id_list import IMAGES
from db.database import db


async def is_photos_enabled() -> bool:
    row = await db.fetchone("SELECT value FROM config WHERE key = 'photos_enabled'")
    return row is not None and row["value"] == "1"


async def get_attachment(key: str) -> str | None:
    if not await is_photos_enabled():
        return None
    entry = IMAGES.get(key)
    if not entry:
        return None
    return entry.get("attachment")