from contextlib import asynccontextmanager
import asyncio
import uvicorn
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from telegram_bot import start_polling
from telegram_lib import TelegramBotManager
from starlette.responses import FileResponse 

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.bot_manager = TelegramBotManager()
    try:
        asyncio.create_task(start_polling(app.state.bot_manager.bot))
        yield
    finally:
        await app.state.bot_manager.close_session()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_bot_manager(request: Request) -> TelegramBotManager:
    return request.app.state.bot_manager

@app.post("/api/send-text")
async def send_message(
    request: Request,
    bot_manager: TelegramBotManager = Depends(get_bot_manager)
):
    data = await request.json()
    text = data.get("text")
    
    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Текст не может быть пустым"
        )
    
    result = await bot_manager.send_to_all(text)
        
    return {
        "status": "success",
        "message": "Текст успешно получен",
        "received_text": text,
        **result.model_dump()
    }


@app.get("/")
def read_root():
    return FileResponse('../frontend/web.html')
    
    # return {"message": "Сервер работает"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)