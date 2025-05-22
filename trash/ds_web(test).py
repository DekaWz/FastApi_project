from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Модель для входящих данных
class TextRequest(BaseModel):
    text: str

app = FastAPI()

# Настройка CORS для доступа из браузера
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/send-text")
async def receive_text(request: TextRequest):
    # Проверка на пустой текст
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Текст не может быть пустым")
    
    print(request)
    
    # Здесь можно добавить логику обработки текста
    # Например: сохранение в базу данных, обработка NLP и т.д.
    
    # Возвращаем результат
    return {
        "status": "success",
        "message": "Текст успешно получен",
        "received_text": request.text
    }

@app.get("/")
def read_root():
    return {"message": "Сервер работает"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)