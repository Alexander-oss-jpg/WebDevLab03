import streamlit as st
import google.generativeai as genai
import requests
import json

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

team_info = f"Team: {selected_team}\n"
if raw_stats:
    splits = raw_stats.get("splits", {})
    if splits and "categories" in splits:
        categories = splits["categories"][:3]
        team_info += "Key Stats:\n"
        for cat in categories:
            cat_name = cat.get("displayName", "")
            team_info += f"  {cat_name}:\n"
            for stat in cat.get("stats", [])[:5]:
                team_info += f"    - {stat.get('displayName', '')}: {stat.get('displayValue', '')}\n"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = ""

user_input = st.text_input("Ask a question:")

if st.button("Send"):
    if not user_input.strip():
        st.warning("Please type a question.")
    else:
        try:
            st.session_state.conversation_context += f"\nUser: {user_input}"
            
            prompt = f"""You are an NFL analyst chatbot. Answer questions about NFL teams using the data provided.

{team_info}

Previous Conversation:
{st.session_state.conversation_context}

Respond naturally and conversationally to the latest user question. Use the team stats when relevant."""

            model = genai.GenerativeModel("models/gemini-1.5-pro")
            response = model.generate_content(prompt)
            bot_reply = response.text
            
            st.session_state.conversation_context += f"\nBot: {bot_reply}"
            
            st.session_state.chat_history.append(("User", user_input))
            st.session_state.chat_history.append(("Bot", bot_reply))
            
        except Exception as e:
            error_msg = "Sorry, I hit a temporary error. Try again."
            st.error(f"Gemini error: {str(e)}")
            st.session_state.chat_history.append(("Bot", error_msg))

st.subheader("Conversation")
for speaker, msg in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {msg}")
