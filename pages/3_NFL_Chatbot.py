import streamlit as st
import google.generativeai as genai
import requests

# CONFIGURE GEMINI
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("NFL Chatbot")
st.write("""
Ask anything about an NFL team — offense, defense, key players, matchups, strengths, 
weaknesses — and the AI will respond using real ESPN NFL data.
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

selected_team = st.selectbox("Choose an NFL team to chat about:", team_names)
team_id = [tid for (tid, name) in teams if name == selected_team][0]

raw_stats = get_team_stats(team_id)
if raw_stats:
    team_stats = raw_stats
else:
    team_stats = {"error": "Stats not available"}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask a question:")

if st.button("Send"):
    if not user_input.strip():
        st.warning("Please type a question.")
    else:
        try:
            prompt = f"""
You are an NFL analyst chatbot.

Team: {selected_team}
Stats: {team_stats}

Chat History: {st.session_state.chat_history}

User Question: {user_input}

Answer naturally, clearly, and based on the stats above.
"""

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            bot_reply = response.text
            st.session_state.chat_history.append(("User", user_input))
            st.session_state.chat_history.append(("Bot", bot_reply))

        except Exception:
            st.error("Gemini is overloaded or the request failed. Try again.")
            st.session_state.chat_history.append(("Bot", "Sorry, I hit a temporary error."))

st.subheader("Conversation")
for speaker, msg in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {msg}")
