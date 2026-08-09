import os
import requests

FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

def get_real_matches():
    url = "https://api.football-data.org/v4/matches"
    headers = {
        "X-Auth-Token": FOOTBALL_DATA_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"API Xətası: {response.status_code}")
            return []

        data = response.json()
        matches = data.get("matches", [])
        
        real_matches = []
        for match in matches[:5]:  # İlk 5 real oyunu götürür
            home_team = match["homeTeam"]["name"]
            away_team = match["awayTeam"]["name"]
            league = match["competition"]["name"]
            match_date = match["utcDate"].split("T")[0]
            
            real_matches.append({
                "home": home_team,
                "away": away_team,
                "league": league,
                "date": match_date
            })
            
        return real_matches
    except Exception as e:
        print(f"Xəta: {e}")
        return []

def generate_coupon():
    matches = get_real_matches()
    
    if not matches:
        return "⚠️ Hazırda aktiv real oyun tapılmadı və ya API xətası var."
    
    text = "🔥 **Günün Real Oyunlar Kuponu** 🔥\n\n"
    
    for m in matches:
        text += f"🏆 {m['league']}\n"
        text += f"⚽️ {m['home']} vs {m['away']}\n"
        text += f"📅 Tarix: {m['date']}\n"
        text += "-------------------------\n"
        
    return text
