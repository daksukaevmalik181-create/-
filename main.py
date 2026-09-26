import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from threading import Thread

TOKEN = "8904347494:AAFwBS6gYABYaw-Q3Vj94tDmCZRxJPGSdx0"
SHORT_APP_URL = "https://t.me"

bot = telebot.TeleBot(TOKEN)
app = FastAPI()

# Разрешаем сайту Netlify делать запросы к нашему серверу
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Память сервера: храним последний сделанный ход
game_state = {"last_move": "Ходов пока нет. Сделайте первый ход!"}

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

# Эндпоинт 1: Принять ход от игрока
@app.post("/play")
async def play_card(request: Request):
    data = await request.json()
    card = data.get("card", "Неизвестная карта")
    game_state["last_move"] = f"Кто-то походил картой:<br><span style='font-size:24px; color:yellow;'>{card}</span>"
    return {"status": "success"}

# Эндпоинт 2: Отдать текущее состояние стола на экран
@app.get("/state")
async def get_state():
    return {"message": game_state["last_move"]}

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    Thread(target=run_fastapi, daemon=True).start()
    print("Бот запущен на надежных HTTP запросах!")
    bot.infinity_polling(drop_pending_updates=True)


