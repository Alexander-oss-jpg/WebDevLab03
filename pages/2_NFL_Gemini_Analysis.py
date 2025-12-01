import streamlit as st
import google.generativeai as genai
import requests

# CONFIGURE GEMINI
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# PAGE TITLE
st.title("NFL Insights: AI-Powered Team Breakdown")
st.write("""
This page uses real NFL data from the ESPN API and processes it through Google Gemini 
to create a conversational, human-style breakdown between two NFL teams.
""")

TEAMS_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"

@st.cache_data
def get_nfl_teams():
    resp = requests.get(TEAMS_URL)
    if resp.status_code != 200:
        return []
    data = resp.json()
    teams = data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
    return [(t["team"]["id"], t["team"]["displayName"]) for t in teams]

@st.cache_data
def get_team_stats(team_id):
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/statistics"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    return resp.json()

teams = get_nfl_teams()
if not teams:
    st.error("Could not load NFL teams.")
    st.stop()

team_names = [name for (tid, name) in teams]

team_1 = st.selectbox("Choose your first NFL team:", team_names)
team_2 = st.selectbox("Choose your second NFL team:", team_names)
detail = st.slider("Choose detail level:", 1, 5, 3)

if st.button("Generate Team Comparison"):
    try:
        id_1 = [tid for (tid, name) in teams if name == team_1][0]
        id_2 = [tid for (tid, name) in teams if name == team_2][0]

        raw1 = get_team_stats(id_1)
        raw2 = get_team_stats(id_2)

        stats_1 = {
            "season": raw1.get("season", {}),
            "leaders": raw1.get("leaders", [])
        }

        stats_2 = {
            "season": raw2.get("season", {}),
            "leaders": raw2.get("leaders", [])
        }

        prompt = f"""
You are an NFL analyst. Compare the two NFL teams using the data below.

Team 1: {team_1}
Stats: {stats_1}

Team 2: {team_2}
Stats: {stats_2}

Write a conversational, human-style comparison. Detail level {detail}/5.
Include:
- Offensive strengths
- Defensive strengths
- Weaknesses
- Playstyle tendencies
- Predicted matchup result
"""

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        st.subheader(f"{team_1} vs {team_2}")
        st.write(response.text)

    except Exception:
        st.error("There was an error generating the AI analysis. Try again.")
