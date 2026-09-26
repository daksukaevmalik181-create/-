import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from threading import Thread
import json

# Секретный ключ вашего бота
TOKEN = "8904347494:AAFwBS6gYABYaw-Q3Vj94tDmCZRxJPGSdx0"

# ВАША ССЫЛКА MINI APP (Исправлено, теперь кнопка в группе откроет игру)
SHORT_APP_URL = "https://t.me"

bot = telebot.TeleBot(TOKEN)
app = FastAPI()

# Полное разрешение сетевых запросов для Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Стартовое состояние игрового стола
game_state = {"last_move": "Ходов пока нет. Сделайте первый ход!"}

# Обработка команд старта игры в группе
@bot.message_handler(func=lambda message: message.text in ['!игра', '/play', '/play@go_durak_bot', '/start'])
def send_game_link(message):
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="🃏 Зайти за игровой стол", url=SHORT_APP_URL)
    markup.add(button)
    
    text = (
        f"🎮 <b>{message.from_user.first_name}</b> создал стол в Дурака!\n\n"
        f"Нажимайте на кнопку ниже, чтобы зайти в игру 👇"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')

# Эндпоинт 1: Принять ход от игрока (ИСПРАВЛЕНО, всеядный метод чтения текста)
@app.post("/play")
async def play_card(request: Request):
    try:
        body = await request.body()
        data = json.loads(body.decode('utf-8'))
        card = data.get("card", "Неизвестная карта")
        game_state["last_move"] = f"Кто-то походил картой:<br><span style='font-size:24px; color:yellow;'>{card}</span>"
        return {"status": "success"}
    except Exception as e:
        game_state["last_move"] = "Ошибка формата хода"
        return {"status": "error"}

# Эндпоинт 2: Показать текущие карты на столе
@app.get("/state")
async def get_state():
    return {"message": game_state["last_move"]}

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    # Запуск сервера
    Thread(target=run_fastapi, daemon=True).start()
    print("Бот успешно запущен на надежных HTTP запросах!")
    
    # Слушаем чаты Telegram без конфликтов сессий
    bot.infinity_polling(drop_pending_updates=True)
