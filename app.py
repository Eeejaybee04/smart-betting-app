import streamlit as st
import requests

# Streamlit Page Setup
st.set_page_config(page_title="Smart Betting Tips", layout="wide")
st.title("⚽ Smart Betting Assistant")

# Sidebar Controls
st.sidebar.header("🔧 Settings")
match_count = st.sidebar.slider("Matches to fetch", 1, 20, 5)
show_only_high = st.sidebar.checkbox("Show only High Confidence tips", value=False)

# API Setup
API_KEY = "your_api_key_here"
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}


# Fetch fixtures
def get_fixtures(match_count):
    url = f"{BASE_URL}/fixtures?next={match_count}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json()["response"]
    return []


# Fetch team stats
def get_team_stats(team_id, league_id, season):
    url = f"{BASE_URL}/teams/statistics?season={season}&team={team_id}&league={league_id}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json()["response"]
    return {}


if st.button("📡 Get Matches"):
    fixtures = get_fixtures(match_count)
    for match in fixtures:
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        league = match["league"]["name"]
        date = match["fixture"]["date"].split("T")[0]
        season = match["league"]["season"]
        home_id = match["teams"]["home"]["id"]
        away_id = match["teams"]["away"]["id"]
        league_id = match["league"]["id"]

        st.markdown(f"### {home} 🆚 {away}")
        st.markdown(f"- 📅 {date} | 🌍 {league}")

        home_stats = get_team_stats(home_id, league_id, season)
        away_stats = get_team_stats(away_id, league_id, season)

        btts_home = home_stats.get("both_teams_to_score", {}).get("yes", 0)
        btts_away = away_stats.get("both_teams_to_score", {}).get("yes", 0)
        over25_home = home_stats.get("goals", {}).get("for", {}).get("percentage", {}).get("over_2.5", 0)
        over25_away = away_stats.get("goals", {}).get("for", {}).get("percentage", {}).get("over_2.5", 0)
        avg_goals_home = float(home_stats.get("goals", {}).get("for", {}).get("total", {}).get("average", 0))
        avg_goals_away = float(away_stats.get("goals", {}).get("for", {}).get("total", {}).get("average", 0))

        incomplete = any(stat == 0 for stat in [
            btts_home, btts_away, over25_home, over25_away, avg_goals_home, avg_goals_away
        ])

        tips = []
        confidence = "Low"

        if over25_home >= 60 and over25_away >= 60:
            tips.append("Over 2.5 Goals")
            if over25_home >= 75 and over25_away >= 75:
                confidence = "High"
            elif over25_home >= 65 or over25_away >= 65:
                confidence = "Medium"

        elif over25_home <= 40 and over25_away <= 40:
            tips.append("Under 2.5 Goals")
            confidence = "Medium"

        if btts_home >= 60 and btts_away >= 60:
            tips.append("BTTS")
            if confidence == "Low":
                confidence = "Medium"

        if avg_goals_home - avg_goals_away >= 1.5:
            tips.append("Home -1 Handicap")
            if confidence == "Low":
                confidence = "Medium"
        elif avg_goals_away - avg_goals_home >= 1.5:
            tips.append("Away -1 Handicap")
            if confidence == "Low":
                confidence = "Medium"

        if incomplete:
            st.markdown("⚠️ *Some stats are missing — confidence adjusted*")
            if confidence == "High":
                confidence = "Medium"
            elif confidence == "Medium":
                confidence = "Low"

        if tips:
            if not show_only_high or confidence == "High":
                st.markdown(f"🧠 **Tip(s):** {', '.join(tips)}")
                st.markdown(f"💪 **Confidence:** {confidence}")
            else:
                st.info("ℹ️ Tip skipped due to low confidence.")
        else:
            st.markdown("🧠 No strong tip available for this match.")
