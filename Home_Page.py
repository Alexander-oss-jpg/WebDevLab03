import streamlit as st

st.title("Web Development Lab03")


st.header("CS 1301")
st.subheader("Team 111, Web Development - Section A")
st.subheader("Bryce Phan, Alexander Jaber")


st.write("""
Welcome to our Streamlit Web Development Lab03 app! You can navigate between the pages using the sidebar to the left. The following pages are:

1.Bryce Phan Portfolio: This is a brief description on Bryce\n 

2.Alexander Jaber Portfolioc: This is a brief description on Alexander\n

3.NFL Stats: This page shows our NFL data visualizations and analysis\n

""")

st.divider()

st.write("### About This Project")
st.write("""
This web application demonstrates our ability to:
- Build multi-page Streamlit applications
- Fetch and process data from external APIs
- Create data visualizations
- Integrate AI/LLM capabilities for data analysis
""")

st.divider()

st.info("👈 Use the sidebar to navigate between different pages of our application!")
