import asyncio
from aiogram import Dispatcher, types
from aiogram.filters import Command
from telegram_lib import load_subscribers, save_subscribers, init_dispatcher


dp = init_dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    chat_id = message.chat.id
    subscribers = load_subscribers()
    
    if chat_id not in subscribers:
        subscribers.append(chat_id)
        save_subscribers(subscribers)
        await message.answer("✅ Вы подписались на рассылку!")
    else:
        await message.answer("ℹ️ Вы уже подписаны.")

async def start_polling(bot):
    await dp.start_polling(bot)