import os
import json
import asyncio
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from contextlib import asynccontextmanager
import dotenv

dotenv.load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN').replace(r'\x3a', ':')
DATA_FILE = "subscribers.json"

bot = Bot(TELEGRAM_TOKEN)
dp = Dispatcher()

def load_subscribers():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_subscribers(subscribers):
    with open(DATA_FILE, "w") as f:
        json.dump(subscribers, f)

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

async def start_polling():
    await dp.start_polling(bot)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        asyncio.create_task(start_polling())
        yield
    finally:
        await bot.session.close()

app = FastAPI(lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/send-text")
async def send_message(request: Request):
    data = await request.json()
    text = data.get("text")
    
    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Текст не может быть пустым"
        )
    
    subscribers = load_subscribers()
    success = 0

    for chat_id in subscribers:
        try:
            await bot.send_message(chat_id=chat_id, text=text)
            success += 1
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")
    
    return {
        "status": "success",
        "message": "Текст успешно получен",
        "received_text": text,
        "total_subscribers": len(subscribers),
        "successfully_sent": success
    }

@app.get("/")
def read_root():
    return {"message": "Сервер работает"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)