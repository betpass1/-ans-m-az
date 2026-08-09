import os
import requests
import telebot
import hashlib
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from threading import Thread
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# 1. Flask Serveri
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

# 2. Sabit Təxmin Alqoritmi
def get_smart_prediction(home, away):
    match_string = f"{home}_vs_{away}".lower()
    hash_value = int(hashlib.md5(match_string.encode()).hexdigest(), 16)
    
    predictions = [
        "P1 (Ev Sahibi Qalib)",
        "Qol/Qol (Har Iki Komanda)",
        "2.5 Ust (Toplam Qol)",
        "P2 (Qonaq Komanda Qalib)",
        "X2 / GG (Barabarlik / Qol)"
    ]
    
    selected_index = hash_value % len(predictions)
    return predictions[selected_index]

# 3. Yalnız Başlamamış Oyunları Çəkən Funksiya
def get_real_matches():
    url = "https://api.football-data.org/v4/matches?status=SCHEDULED,TIMED"
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
            
            raw_date = match["utcDate"].replace("T", " ").replace("Z", "")
            match_date = raw_date[:16]
            
            real_matches.append({
                "home": home_team,
                "away": away_team,
                "league": league,
                "date": match_date,
                "prediction": get_smart_prediction(home_team, away_team)
            })
            
        return real_matches
    except Exception as e:
        print(f"Xata: {e}")
        return []

# 4. Pastel Gradient Fon
def draw_pastel_gradient(width, height):
    base = Image.new('RGB', (width, height), (255, 255, 255))
    
    for y in range(height):
        r = int(255 - (y / height) * 40)
        g = int(200 + (y / height) * 35)
        b = int(220 + (y / height) * 30)
        for x in range(width):
            r_x = int(r - (x / width) * 30)
            g_x = int(g + (x / width) * 20)
            b_x = int(b + (x / width) * 35)
            base.putpixel((x, y), (r_x, g_x, b_x))
            
    return base

# 5. Kvadrat və Simvol Xətasız Kupon Şəkli
def create_coupon_image(matches):
    width = 800
    height = 200 + (len(matches) * 130)
    
    img = draw_pastel_gradient(width, height)
    draw = ImageDraw.Draw(img, 'RGBA')

    try:
        font_logo = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
        font_main = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
        font_sub = ImageFont.truetype("DejaVuSans.ttf", 15)
    except:
        font_logo = font_title = font_main = font_sub = ImageFont.load_default()

    # Rənglər
    text_dark = (20, 30, 55, 255)       
    text_purple = (100, 40, 140, 255)   
    text_gray = (90, 100, 120, 255)     
    
    # Başlıq
    draw.text((width // 2, 45), "Sansim.az", fill=text_dark, font=font_logo, anchor="mm")
    draw.text((width // 2, 85), "GUNUN TAXMINLARI", fill=text_purple, font=font_title, anchor="mm")

    y_offset = 120
    for match in matches:
        # Yarı-şəffaf Ağ Kart
        draw.rounded_rectangle([40, y_offset, width - 40, y_offset + 110], radius=18, fill=(255, 255, 255, 215))

        # Şəkildə kvadrat yaratmayan təmiz mətn formatları
        league_date = f"> {match['league']}   |   {match['date']} UTC"
        teams = f"{match['home']}  VS  {match['away']}"
        pred = f"• Taxmin: {match['prediction']}"

        draw.text((60, y_offset + 15), league_date, fill=text_gray, font=font_sub)
        draw.text((60, y_offset + 42), teams, fill=text_dark, font=font_main)
        draw.text((60, y_offset + 72), pred, fill=text_purple, font=font_main)

        y_offset += 128

    bio = BytesIO()
    bio.name = 'coupon.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

# 6. Telegram Komandaları
try:
    bot.set_my_commands([
        telebot.types.BotCommand("start", "Kuponu Al 🚀")
    ])
except Exception as e:
    print(f"Komanda xetasi: {e}")

@bot.message_handler(commands=['start', 'kupon'])
def send_coupon(message):
    matches = get_real_matches()
    if not matches:
        bot.reply_to(message, "⚠️ Hələ ki, tətbiq üçün aktiv/başlamamış real oyun tapılmadı.")
        return

    photo = create_coupon_image(matches)
    bot.send_photo(message.chat.id, photo, caption="✨ **Sansım.az - Günün Yalnız Başlamamış Oyunlar Kuponu**", parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.lower()
    if "kupon" in text or "oyun" in text or "start" in text:
        send_coupon(message)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
