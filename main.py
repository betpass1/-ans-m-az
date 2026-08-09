import os
import requests
import telebot
import random
from threading import Thread
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# 1. Pulsuz Flask Serveri
app = Flask('')

@app.route('/')
def home():
    return "Bot aktivdir və işləyir!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Avtomatik Təxmin Generasiyası
def get_smart_prediction():
    predictions = [
        "💡 Təxmin: Ev Sahibi Qələbəsi (P1)",
        "💡 Təxmin: Qonaq Komanda Qələbəsi (P2)",
        "💡 Təxmin: Bərabərlik (X)",
        "💡 Təxmin: Üst 2.5 Qol",
        "💡 Təxmin: Hər İki Komanda Qol Vuracaq (Qol/Qol)"
    ]
    return random.choice(predictions)

# 3. Real Oyunları Çəkən Funksiya
def get_real_matches():
    url = "https://api.football-data.org/v4/matches"
    headers = {
        "X-Auth-Token": FOOTBALL_DATA_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"API Xətası Kodu: {response.status_code}")
            return []

        data = response.json()
        matches = data.get("matches", [])
        
        real_matches = []
        for match in matches[:5]:
            home_team = match["homeTeam"]["name"]
            away_team = match["awayTeam"]["name"]
            league = match["competition"]["name"]
            match_date = match["utcDate"].split("T")[0]
            
            real_matches.append({
                "home": home_team,
                "away": away_team,
                "league": league,
                "date": match_date,
                "prediction": get_smart_prediction() # Təxmin əlavə olundu
            })
            
        return real_matches
    except Exception as e:
        print(f"Xəta baş verdi: {e}")
        return []

def generate_coupon():
    matches = get_real_matches()
    
    if not matches:
        return "⚠️ Bu gün üçün sistemdə aktiv real oyun tapılmadı və ya API xətası var."
    
    text = "🔥 **Günün Real Oyunlar Kuponu** 🔥\n\n"
    
    for m in matches:
        text += f"🏆 {m['league']}\n"
        text += f"⚽️ {m['home']} vs {m['away']}\n"
        text += f"📅 Tarix: {m['date']}\n"
        text += f"{m['prediction']}\n"
        text += "-------------------------\n"
        
    return text

# 4. Telegram Komandaları
@bot.message_handler(commands=['start', 'kupon'])
def send_coupon(message):
    coupon_text = generate_coupon()
    bot.reply_to(message, coupon_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if "kupon" in message.text.lower() or "oyun" in message.text.lower():
        coupon_text = generate_coupon()
        bot.reply_to(message, coupon_text, parse_mode='Markdown')

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
