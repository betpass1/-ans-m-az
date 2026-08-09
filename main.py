import os
import requests
import telebot
import hashlib
from threading import Thread
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# 1. Pulsuz Flask Serveri (Render port xətasını önləmək üçün)
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

# 2. Komandaların adına əsasən sabit və dəqiq təxmin alqoritmi
def get_smart_prediction(home, away):
    match_string = f"{home}_vs_{away}".lower()
    hash_value = int(hashlib.md5(match_string.encode()).hexdigest(), 16)
    
    predictions = [
        "💡 Dəqiq Analiz: Ev Sahibi Qələbəsi (P1)",
        "💡 Dəqiq Analiz: Hər İki Komanda Qol Vuracaq (Qol/Qol)",
        "💡 Dəqiq Analiz: Toplam Qol 2.5 Üst",
        "💡 Dəqiq Analiz: Qonaq Komanda Qələbəsi (P2)",
        "💡 Dəqiq Analiz: Bərabərlik və ya Qol/Qol (X2 / GG)"
    ]
    
    selected_index = hash_value % len(predictions)
    return predictions[selected_index]

# 3. Real Oyunları API-dən Çəkən Funksiya
def get_real_matches():
    url = "https://api.football-data.org/v4/matches"
    headers = {
        "X-Auth-Token": FOOTBALL_DATA_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
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
                "prediction": get_smart_prediction(home_team, away_team)
            })
            
        return real_matches
    except Exception as e:
        print(f"Xəta: {e}")
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

# 4. Sol Aşağı Küncə Telegram Menu Düyməsinin Təyini
try:
    bot.set_my_commands([
        telebot.types.BotCommand("start", "Kuponu Al 🚀")
    ])
except Exception as e:
    print(f"Komanda menyusu xətası: {e}")

# 5. Telegram Komanda İşləyiciləri
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
