import streamlit as st

# Title of App
st.title("Web Development Lab03 – NBA Analytics")

# Assignment Data
st.header("CS 1301")
st.subheader("Team 111, Web Development – Section A")
st.subheader("Alexander Jaber and Bryce Phan")  # add teammates if you have them

# Introduction
st.write("""
Welcome to our Streamlit Web Development Lab03 app! This project uses the
public **balldontlie** NBA API plus Google Gemini to explore basketball data.

Here is what each page does:

1. **NBA API Analysis** – Shows an NBA team's games, scores, and a chart of
   points per game using data from the API.
2. **Gemini + NBA Analysis** – Uses the same team and season data, but sends
   a summary to Google Gemini to generate an analyst-style breakdown.
3. **NBA Chatbot** – A small chatbot that knows about the selected team's
   season and can answer questions in a conversational way.
4. **Home Page** – Explains the purpose of the app and how to use it.
""")

st.info("Use the sidebar on the left to switch between the different pages.")
