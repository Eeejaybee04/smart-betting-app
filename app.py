import streamlit as st
import requests

# ✅ App title
st.set_page_config(page_title="Smart Betting Assistant", layout="wide")
st.title("⚽ Smart Betting Assistant")

# ✅ API credentials
API_KEY = "1897b0d26emshd5ef2957aefbcafp16474ajsnd453703ee090"
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}


# ✅ Get upcoming fixtures
def get_fixtures(match_count):
    url = f"{BASE_URL}/fixtures?next={match_count}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json()["response"]
    else:
        st.error("⚠️ Couldn't fetch match data.")
        return []


# ✅ Sidebar controls
st.sidebar.header("🔧 Settings")
match_count = st.sidebar.slider("Matches to fetch", 1, 20, 5)

# ✅ Main button
if st.button("📡 Get Matches"):
    fixtures = get_fixtures(match_count)

    if fixtures:
        st.success(f"✅ Retrieved {len(fixtures)} matches")
        for match in fixtures:
            date = match["fixture"]["date"].split("T")[0]
            league = match["league"]["name"]
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]

            st.markdown(f"""
            ### {home} 🆚 {away}  
            - 📅 Date: {date}  
            - 🌍 League: *{league}*
            """)


            # Get team stats
            def get_team_stats(team_id, league_id, season):
                url = f"{BASE_URL}/teams/statistics?season={season}&team={team_id}&league={league_id}"
                res = requests.get(url, headers=HEADERS)
                if res.status_code == 200:
                    return res.json()["response"]
                else:
                    return None


            # Get IDs
            home_id = match["teams"]["home"]["id"]
            away_id = match["teams"]["away"]["id"]
            league_id = match["league"]["id"]
            season = match["league"]["season"]

            home_stats = get_team_stats(home_id, league_id, season)
            away_stats = get_team_stats(away_id, league_id, season)

            # Safeguard
            if home_stats and away_stats:
                # Pull key metrics safely
                btts_home = home_stats.get("both_teams_to_score", {}).get("yes", 0)
                btts_away = away_stats.get("both_teams_to_score", {}).get("yes", 0)

                over25_home = home_stats.get("goals", {}).get("for", {}).get("percentage", {}).get("over_2.5", 0)
                over25_away = away_stats.get("goals", {}).get("for", {}).get("percentage", {}).get("over_2.5", 0)

                avg_goals_home = float(home_stats.get("goals", {}).get("for", {}).get("total", {}).get("average", 0))
                avg_goals_away = float(away_stats.get("goals", {}).get("for", {}).get("total", {}).get("average", 0))

                # Check for missing data
                incomplete = any(stat == 0 for stat in [
                    btts_home, btts_away,
                    over25_home, over25_away,
                    avg_goals_home, avg_goals_away
                ])

                # Logic
                tips = []
                confidence = "Low"

                if btts_home >= 70 and btts_away >= 70 and over25_home >= 60 and over25_away >= 60:
                    tips.append("BTTS + Over 2.5")
                    confidence = "High"
                elif btts_home <= 40 and btts_away <= 40 and over25_home <= 40 and over25_away <= 40:
                    tips.append("Under 2.5")
                    confidence = "Medium"
                elif avg_goals_home >= 2.5 and avg_goals_away <= 1.0:
                    tips.append("Home -1 Handicap")
                    confidence = "Medium"
                elif avg_goals_away >= 2.5 and avg_goals_home <= 1.0:
                    tips.append("Away -1 Handicap")
                    confidence = "Medium"

                # ✅ PLACE THIS BLOCK RIGHT HERE:
                if incomplete:
                    st.markdown("⚠️ *Some stats are missing or incomplete — confidence adjusted*")
                    if confidence == "High":
                        confidence = "Medium"
                    elif confidence == "Medium":
                        confidence = "Low"

                    # ✅ Final tip display
                    if tips:
                        st.markdown(f"🧠 **Tip:** {', '.join(tips)}")
                        st.markdown(f"💪 **Confidence:** {confidence}")
                    else:
                        st.markdown("🧠 No clear tip for this match.")
                else:
                    st.warning("⚠️ Could not fetch team stats.")
