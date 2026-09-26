import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
from threading import Thread

# --- НАСТРОЙКИ ---
TOKEN = "8904347494:AAFwBS6gYABYaw-Q3Vj94tDmCZRxJPGSdx0"
SHORT_APP_URL = "https://t.me/go_durak_bot/start_durak"

bot = telebot.TeleBot(TOKEN)
app = FastAPI()

# Хранилище активных игроков в комнате: { websocket: user_id }
connected_players = {}

# --- БОТ В ТЕЛЕГРАМ ---
@bot.message_handler(func=lambda message: message.text in ['!игра', '/play', '/play@go_durak_bot', '/start'])
def send_game_link(message):
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="🃏 Зайти за игровой стол", url=SHORT_APP_URL)
    markup.add(button)
    
    text = (
        f"🎮 <b>{message.from_user.first_name}</b> создал игровой стол в Дурака!\n\n"
        f"Ребята, нажимайте на кнопку ниже, чтобы зайти в эту комнату и начать игру 👇"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')

# --- WEBSOCKET СЕРВЕР ДЛЯ ИГРЫ В РЕАЛЬНОМ ВРЕМЕНИ ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # При подключении генерируем временный ID игрока (или получаем из Telegram)
    player_id = f"Игрок_{len(connected_players) + 1}"
    connected_players[websocket] = player_id
    
    print(self_info := f" Подключился {player_id}")
    
    # Оповещаем всех, сколько человек за столом
    await broadcast({"type": "info", "message": f"За стол сел: {player_id}. Всего игроков: {len(connected_players)}"})

    try:
        while True:
            # Ждем действий от игрока (кликов по картам)
            data = await websocket.receive_json()
            
            if data.get("type") == "play_card":
                # Пересылаем ход сопернику, чтобы у него на экране тоже отобразилась карта
                await broadcast({
                    "type": "card_played",
                    "player": player_id,
                    "card": data.get("card")
                })
    except WebSocketDisconnect:
        del connected_players[websocket]
        print(f"❌ Отключился {player_id}")
        await broadcast({"type": "info", "message": f"{player_id} покинул стол."})

async def broadcast(message: dict):
    if connected_players:
        await asyncio.gather(*[ws.send_json(message) for ws in connected_players])

# Функция запуска FastAPI в отдельном потоке
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    # Запускаем WebSocket сервер на порту 8000
    Thread(target=run_fastapi, daemon=True).start()
    
    # Запускаем Телеграм-бота
    print("Бот и WebSocket-сервер успешно запущены!")
    bot.infinity_polling()

pyTelegramBotAPI==4.26.0
fastapi==0.115.0
uvicorn==0.30.6
requests==2.32.3
