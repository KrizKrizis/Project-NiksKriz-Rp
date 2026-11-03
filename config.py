# config.py
import os
from dotenv import load_dotenv

load_dotenv()

VK_TOKEN = os.getenv("VK_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
SQLITE_PATH = os.getenv("SQLITE_PATH", "nikskriz.db")
PG_DSN = os.getenv("PG_DSN", "")

FOUNDER_ID = int(os.getenv("FOUNDER_ID", "0"))
TECH_ADMIN_ID = int(os.getenv("TECH_ADMIN_ID", "0"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

CHAT_HELPERS = int(os.getenv("CHAT_HELPERS", "0"))
CHAT_ADMINS = int(os.getenv("CHAT_ADMINS", "0"))
CHAT_GA_STATS = int(os.getenv("CHAT_GA_STATS", "0"))
CHAT_TEAM_GENERAL = int(os.getenv("CHAT_TEAM_GENERAL", "0"))
CHAT_TESTERS = int(os.getenv("CHAT_TESTERS", "0"))
CHAT_FULL_LOG = int(os.getenv("CHAT_FULL_LOG", "0"))