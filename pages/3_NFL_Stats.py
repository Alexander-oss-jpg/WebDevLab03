import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.title("🏈 NFL Stats Analysis")

st.write("""
Explore live NFL statistics and team performance data!
This page fetches real-time data from the ESPN API to provide up-to-date football statistics.
""")

st.divider()

def get_nfl_teams():
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
    try:
        response = requests.get(url)
        data = response.json()
        teams = data['sports'][0]['leagues'][0]['teams']
        return teams
    except:
        st.error("Error: Could not load NFL teams")
        return []

def get_standings():
    url = "https://site.api.espn.com/apis/v2/sports/football/nfl/standings"
    try:
        response = requests.get(url)
        data = response.json()
        return data
    except:
        st.error("Error: Could not load standings")
        return None

st.header("🏈 NFL Team Explorer")

teams_data = get_nfl_teams()

if teams_data:
    teams_dict = {}
    for team_info in teams_data:
        try:
            team = team_info['team']
            team_id = team['id']
            teams_dict[team_id] = {
                'name': team['displayName'],
                'abbreviation': team['abbreviation'],
                'logo': team['logos'][0]['href']
            }
        except:
            continue
    
    st.success(f"✅ Loaded {len(teams_dict)} NFL teams!")
    
    selected_teams = st.multiselect(
        "Select Teams to View (up to 4)",
        options=list(teams_dict.keys()),
        format_func=lambda x: teams_dict[x]['name'],
        max_selections=4
    )
    
    if selected_teams:
        st.subheader("Selected Teams")
        
        cols = st.columns(len(selected_teams))
        for i in range(len(selected_teams)):
            team_id = selected_teams[i]
            with cols[i]:
                try:
                    st.image(teams_dict[team_id]['logo'], width=100)
                    st.write(f"**{teams_dict[team_id]['name']}**")
                    st.write(f"Abbreviation: {teams_dict[team_id]['abbreviation']}")
                except:
                    st.warning("Could not display team info")
    
    st.divider()
    
    st.header("🏆 NFL Standings")
    
    conference_choice = st.radio(
        "Select Conference",
        ["AFC", "NFC", "All"],
        horizontal=True
    )
    
    standings_data = get_standings()
    
    if standings_data:
        all_standings = []
        
        try:
            for conference in standings_data['children']:
                conf_abbr = conference['abbreviation']
                
                if conference_choice != "All" and conf_abbr != conference_choice:
                    continue
                
                for standing in conference['standings']['entries']:
                    try:
                        team = standing['team']
                        stats = standing['stats']
                        
                        team_name = team['displayName']
                        team_logo = team['logos'][0]['href']
                        
                        wins = 0
                        losses = 0
                        win_pct = 0
                        
                        for stat in stats:
                            if stat['name'] == 'wins':
                                wins = stat['value']
                            elif stat['name'] == 'losses':
                                losses = stat['value']
                            elif stat['name'] == 'winPercent':
                                win_pct = stat['value']
                        
                        team_data = {
                            'Conference': conf_abbr,
                            'Team': team_name,
                            'Logo': team_logo,
                            'Wins': wins,
                            'Losses': losses,
                            'Win %': round(win_pct, 3)
                        }
                        
                        all_standings.append(team_data)
                    except:
                        continue
        except:
            st.error("Error processing standings data")
        
        if all_standings:
            df_standings = pd.DataFrame(all_standings)
            
            for index, row in df_standings.iterrows():
                col1, col2, col3 = st.columns([1, 3, 2])
                
                try:
                    with col1:
                        st.image(row['Logo'], width=50)
                    
                    with col2:
                        st.write(f"**{row['Team']}**")
                    
                    with col3:
                        st.write(f"Record: {row['Wins']}-{row['Losses']} ({row['Win %']})")
                    
                    if (index + 1) % 8 == 0:
                        st.divider()
                except:
                    continue
            
            st.divider()
            
            st.subheader("📊 Wins Comparison")
            
            chart_type = st.selectbox(
                "Select Chart Type",
                ["Bar Chart", "Pie Chart - Conference Distribution"]
            )
            
            try:
                if chart_type == "Bar Chart":
                    df_sorted = df_standings.sort_values('Wins', ascending=False)
                    
                    fig = px.bar(
                        df_sorted,
                        x='Team',
                        y='Wins',
                        color='Conference',
                        title=f'NFL Team Wins - {conference_choice}',
                        color_discrete_map={'AFC': 'blue', 'NFC': 'red'}
                    )
                    
                    fig.update_layout(xaxis_tickangle=-45, height=600)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "Pie Chart - Conference Distribution":
                    afc_count = 0
                    nfc_count = 0
                    
                    for index, row in df_standings.iterrows():
                        if row['Conference'] == 'AFC':
                            afc_count += 1
                        else:
                            nfc_count += 1
                    
                    conf_data = {
                        'Conference': ['AFC', 'NFC'],
                        'Count': [afc_count, nfc_count]
                    }
                    
                    df_conf = pd.DataFrame(conf_data)
                    
                    fig = px.pie(
                        df_conf,
                        values='Count',
                        names='Conference',
                        title='Teams by Conference',
                        color='Conference',
                        color_discrete_map={'AFC': 'blue', 'NFC': 'red'}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            except:
                st.error("Error creating chart")
            
            st.divider()
            
            st.subheader("📈 Team Comparison Tool")
            
            if len(selected_teams) >= 2:
                comparison_teams = []
                
                try:
                    for team_id in selected_teams:
                        team_name = teams_dict[team_id]['name']
                        
                        for team_data in all_standings:
                            if team_data['Team'] == team_name:
                                comparison_teams.append(team_data)
                                break
                    
                    if len(comparison_teams) >= 2:
                        df_compare = pd.DataFrame(comparison_teams)
                        
                        st.dataframe(df_compare[['Team', 'Conference', 'Wins', 'Losses', 'Win %']], 
                                     use_container_width=True, 
                                     hide_index=True)
                        
                        fig = px.bar(
                            df_compare,
                            x='Team',
                            y='Wins',
                            title='Selected Teams Wins Comparison',
                            color='Wins',
                            color_continuous_scale='Blues'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                except:
                    st.error("Error comparing teams")
            else:
                st.info("Select at least 2 teams above to compare them!")
        else:
            st.warning("No standings data available")
    else:
        st.error("Could not load standings data")
else:
    st.error("Could not load NFL teams")

st.divider()

st.info("""
    **Data Source:** ESPN NFL API  
    **Note:** All data is publicly available and updates regularly during the NFL season.
    """)
