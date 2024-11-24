import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Set page configuration at the top
st.set_page_config(page_title="Match Summary Dashboard", layout="wide")

# Inject custom CSS for styling
st.markdown("""
    <style>
    /* Set font and background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #1c1c1e;
        color: #fefefe;
    }
    
    /* Title styles */
    .css-1hqn5qi {
        color: #fefefe;
        font-size: 2rem;
        font-weight: 600;
    }

    /* Customize sidebar */
    .css-1y4p8pa { 
        background-color: #2c2c2e; 
        color: #fefefe; 
    }

    /* Table and chart borders */
    .css-2trqyj { 
        border-radius: 10px; 
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); 
    }
    </style>
""", unsafe_allow_html=True)

# Function to process JSON and generate the DataFrame
def process_match_data(json_data):
    player_data = []
    for team in json_data["teams"]:
        team_name = team["name"]
        team_color = team["color"]
        for player in team["players"]:
            # Extract stats and apply transformations
            kills = player["stats"].get("kills", 0)
            deaths = player["stats"].get("deaths", 0)
            damageDone = round(player["stats"].get("damageDone", 0) / 2, 1)
            damageTaken = round(player["stats"].get("damageTaken", 0) / 2, 1)
            damageDifferential = round(player["stats"].get("damageDifferential", 0) / 2, 1)
            flagsCaptured = player["stats"].get("flagsCaptured", 0)
            totalFlagHoldMillis = round(player["stats"].get("totalFlagHoldMillis", 0) / 1000)  # Convert to seconds
            bowAccuracy = round(player["stats"].get("bowAccuracy", 0) * 100)  # Convert to percentage
            goldenApplesEaten = player["stats"].get("goldenApplesEaten", 0)

            # Format the transformed stats
            player_entry = {
                "team_name": team_name,
                "team_color": team_color,
                "username": player["username"],
                "kills": kills,
                "deaths": deaths,
                "damageDone": damageDone,
                "damageTaken": damageTaken,
                "damageDifferential": damageDifferential,
                "flagsCaptured": flagsCaptured,
                "totalFlagHoldTime": f"{totalFlagHoldMillis} s",  # Add "s" suffix
                "bowAccuracy": f"{bowAccuracy}%",  # Add "%" suffix
                "goldenApplesEaten": goldenApplesEaten,
            }
            player_data.append(player_entry)
    return pd.DataFrame(player_data)

# Streamlit App UI
st.sidebar.title("🏆 Match Dashboard")
match_id = st.sidebar.text_input("Enter Match ID:", "Your match id, i.e: 7250636141171")

if st.sidebar.button("Fetch Match Data"):
    # Fetch JSON file
    url = f"https://stratus.network/match/{match_id}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        match_data = response.json()

        # Process the data and store it in session state
        st.session_state.df = process_match_data(match_data)
        st.session_state.match_id = match_id

    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")

# Ensure data is loaded before displaying pages
if "df" in st.session_state:
    df = st.session_state.df

    # Sidebar navigation
    page = st.sidebar.radio("Navigate:", ["Team Comparison", "Player Comparison"])

    if page == "Team Comparison":
        st.title("🔴🔵 Team Comparison")
        team_summary = df.groupby("team_name").agg(
            kills=("kills", "sum"),
            deaths=("deaths", "sum"),
            damageDone=("damageDone", "sum"),
            damageTaken=("damageTaken", "sum"),
            flagsCaptured=("flagsCaptured", "sum")
        ).reset_index()

        # Display team metrics
        st.dataframe(team_summary.style.background_gradient(cmap="coolwarm"))

        # Bar Chart Layout: 2x3 Grid
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        # Plot each bar chart in the respective columns
        with col1:
            fig1 = px.bar(
                team_summary,
                x="team_name",
                y="kills",
                color="team_name",  # Color by team
                title="Total Kills",
                labels={"kills": "Kills"}
            )
            st.plotly_chart(fig1)

        with col2:
            fig2 = px.bar(
                team_summary,
                x="team_name",
                y="deaths",
                color="team_name",  # Color by team
                title="Total Deaths",
                labels={"deaths": "Deaths"}
            )
            st.plotly_chart(fig2)

        with col3:
            fig3 = px.bar(
                team_summary,
                x="team_name",
                y="flagsCaptured",
                color="team_name",  # Color by team
                title="Total Flags Captured",
                labels={"flagsCaptured": "Flags Captured"}
            )
            st.plotly_chart(fig3)

        with col4:
            fig4 = px.bar(
                team_summary,
                x="team_name",
                y="damageDone",
                color="team_name",  # Color by team
                title="Total Damage Done",
                labels={"damageDone": "Damage Done"}
            )
            st.plotly_chart(fig4)

        with col5:
            fig5 = px.bar(
                team_summary,
                x="team_name",
                y="damageTaken",
                color="team_name",  # Color by team
                title="Total Damage Taken",
                labels={"damageTaken": "Damage Taken"}
            )
            st.plotly_chart(fig5)

        with col6:
            # You can choose to add another chart if you wish
            st.write("Additional chart space")


    # Updated Player Comparison Section
    elif page == "Player Comparison":
        st.title("👤 Player Comparison")
        
        # Dropdown to select players
        selected_players = st.multiselect(
            "Select Players:", df["username"].unique(), default=df["username"].unique()[:2]
        )
        
        if len(selected_players) < 2:
            st.warning("Please select at least two players to compare.")
        else:
            # Filter data for selected players
            player_data = df[df["username"].isin(selected_players)]

            # List of metrics to compare
            metrics = ["kills", "deaths", "damageDone", "damageTaken", "flagsCaptured", "bowAccuracy"]
            
            # Generate individual bar charts for each stat
            st.write("### Individual Stat Comparisons")
            
            # Create a 2x3 grid of columns
            cols = st.columns(3)  # Three columns per row
            
            # Iterate over metrics and place each bar chart in a column
            for i, metric in enumerate(metrics):
                col = cols[i % 3]  # Determine the column for the chart (0, 1, 2)
                with col:
                    fig = px.bar(
                        player_data,
                        x="username",
                        y=metric,
                        color="team_color",  # Color by the player's team_color
                        labels={"username": "Player", metric: metric.replace("damage", "Damage ").title()},
                        title=f"Comparison: {metric.replace('damage', 'Damage ').title()}",
                        text_auto=True
                    )
                    st.plotly_chart(fig, use_container_width=True)


else:
    st.write("Please fetch match data to display the dashboard.")
