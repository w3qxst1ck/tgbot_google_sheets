import os
import dotenv

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = [int(user_id) for user_id in os.getenv("ADMINS").split(",")]
TABLE_NAME = os.getenv("TABLE_NAME")
CREDS_FILE = os.getenv("CREDS_FILE")

