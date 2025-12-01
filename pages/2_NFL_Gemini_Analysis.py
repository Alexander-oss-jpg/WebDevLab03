import streamlit as st
import google.generativeai as genai
import requests

# CONFIGURE GEMINI (only once per file)

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# PAGE HEADER
st.title("NFL Insights: AI-Powered Team Breakdown")
st.write("""
This page takes real NFL data from the ESPN API and processes it 
with Google Gemini to create a clean, human-style comparison 
between two NFL teams.
""")

# ESPN API ENDPOINTS

TEAMS_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"

@st.cache_data
def get_nfl_teams():
    resp = requests.get(TEAMS_URL)
    if resp.status_code != 200:
        return []
    data = resp.json()
    teams = data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
    team_list = []
    for t in teams:
        info = t.get("team", {})
        tid = info.get("id")
        name = info.get("displayName")
        if tid and name:
            team_list.append((tid, name))
    return team_list

@st.cache_data
def get_team_stats(team_id):
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/statistics"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    return resp.json()

# LOAD TEAMS

teams = get_nfl_teams()
if not teams:
    st.error("Failed to load NFL teams.")
    st.stop()

team_names = [name for (tid, name) in teams]

# USER INPUTS (Required for Phase 3)

team_1 = st.selectbox("Choose your first NFL team:", team_names)
team_2 = st.selectbox("Choose your second NFL team:", team_names)
detail = st.slider("Choose detail level for the breakdown:", 1, 5, 3)

# FETCH → SHRINK → SEND TO GEMINI

if st.button("Generate Team Comparison"):
    try:
        with st.spinner("Generating analysis..."):

            id_1 = [tid for (tid, name) in teams if name == team_1][0]
            id_2 = [tid for (tid, name) in teams if name == team_2][0]
