import json
import os
from aiogram import Bot
from pydantic import BaseModel
from aiogram import Dispatcher

DATA_FILE = "subscribers.json"

def init_dispatcher():
    dp = Dispatcher()
    return dp

def load_subscribers():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_subscribers(subscribers):
    with open(DATA_FILE, "w") as f:
        json.dump(subscribers, f)

class SendResult(BaseModel):
    total_subscribers: int
    successfully_sent: int

class TelegramBotManager:
    def __init__(self):
        self.bot = None
        self._initialize_bot()

    def _initialize_bot(self):
        token = os.getenv('TELEGRAM_TOKEN').replace(r'\x3a', ':')
        self.bot = Bot(token=token)

    async def send_to_all(self, text: str) -> SendResult:
        subscribers = load_subscribers()
        success = 0
        
        for chat_id in subscribers:
            try:
                await self.bot.send_message(chat_id=chat_id, text=text)
                success += 1

            except Exception as e:
                print(f"Error sending to {chat_id}: {e}")
        
        return SendResult(
            total_subscribers=len(subscribers),
            successfully_sent=success
        )

    async def close_session(self):
        await self.bot.session.close()