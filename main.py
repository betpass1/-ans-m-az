import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Telegram Bot Tokenini birbaşa daxil edə bilərsiniz və ya Render-də Environment Variable kimi əlavə edə bilərsiniz
TOKEN = os.environ.get('BOT_TOKEN', '8922448048:AAFQDW9gZ24LEiIfG6yn9nZ6BM4nmM0stgg')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # 4 fərqli əmsallı düymələrin yaradılması
    markup = InlineKeyboardMarkup(row_width=2)
    btn_2_3 = InlineKeyboardButton("🔥 2-3 Əmsal Kuponu", callback_data="kox_2_3")
    btn_5 = InlineKeyboardButton("⭐ 5 Əmsal Kuponu", callback_data="kox_5")
    btn_7 = InlineKeyboardButton("🎯 7 Əmsal Kuponu", callback_data="kox_7")
    btn_10 = InlineKeyboardButton("🚀 10 Əmsal (Riskli)", callback_data="kox_10")
    
    markup.add(btn_2_3, btn_5, btn_7, btn_10)
    
    bot.send_message(
        message.chat.id, 
        "Salam! Günlük futbol kuponları üçün aşağıdakı düymələrdən birini seçin:", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # Düymələrə basıldıqda gələn cavablar
    if call.data == "kox_2_3":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📊 **2-3 Əmsallı Günün Kuponu:**\n\n1. Real Madrid - Getafe: Qələbə (1) - Əmsal: 1.45\n2. Arsenal - Chelsea: 2.5 Üst - Əmsal: 1.65\n🔹 **Ümumi Əmsal: ~2.39**")
    
    elif call.data == "kox_5":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "⭐ **5 Əmsallı Günün Kuponu:**\n\n1. Milan - Inter: KG Var - Əmsal: 1.80\n2. Bayern - Dortmund: 1 (Ev sahibi) - Əmsal: 1.75\n3. Barcelona - Sevilla: 1.5 Üst - Əmsal: 1.60\n⭐ **Ümumi Əmsal: ~5.04**")
        
    elif call.data == "kox_7":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🎯 **7 Əmsallı Günün Kuponu:**\n\n1. Feyenoord - Ajax: 2.5 Üst - Əmsal: 1.70\n2. Porto - Benfica: X (Heç-heçə) - Əmsal: 3.20\n🎯 **Ümumi Əmsal: ~5.44** (Yaxın zamanda 7-yə tamamlanacaq)")
        
    elif call.data == "kox_10":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🚀 **10 Əmsal (Bomba Kupon):**\n\n1. Roma - Lazio: X - Əmsal: 3.10\n2. Lyon - Marseille: 2 - Əmsal: 2.80\n3. Galatasaray - Beşiktaş: KG Var - Əmsal: 1.70\n🚀 **Ümumi Əmsal: ~14.75**")

# Botun işləməsi üçün
if __name__ == "__main__":
    print("Bot işə düşdü...")
    bot.infinity_polling()
