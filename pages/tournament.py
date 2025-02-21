import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client
import os
from dotenv import load_dotenv
from streamlit_calendar import calendar

# Initialize Supabase client
# Check if running on Streamlit Cloud
if 'SUPABASE_URL' in st.secrets:
    supabase_url = st.secrets['SUPABASE_URL']
    supabase_key = st.secrets['SUPABASE_KEY']
else:
    # Load local environment variables
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

supabase = create_client(supabase_url, supabase_key)

# Tournament Calendar Page
st.title("🎾 Tournament Calendar")

def load_players():
    try:
        response = supabase.table('players').select('*').execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading players: {str(e)}")
        return pd.DataFrame()

def load_tournaments():
    try:
        response = supabase.table('tournaments').select('*').execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading tournaments: {str(e)}")
        return pd.DataFrame()

def save_tournament(tournament_data):
    try:
        supabase.table('tournaments').insert(tournament_data).execute()
        st.success("Tournament added successfully!")
        return True
    except Exception as e:
        st.error(f"Error saving tournament: {str(e)}")
        return False

def register_player(registration_data):
    try:
        supabase.table('tournament_registrations').insert(registration_data).execute()
        st.success("Player registered successfully!")
        return True
    except Exception as e:
        st.error(f"Error registering player: {str(e)}")
        return False

# Add Tournament Section
with st.expander("Add New Tournament"):
    with st.form("new_tournament_form"):
        col1, col2 = st.columns(2)
        with col1:
            tournament_name = st.text_input("Tournament Name")
            start_date = st.date_input("Start Date")
            location = st.text_input("Location")
        with col2:
            tournament_type = st.selectbox("Tournament Type", ["Singles", "Doubles", "Mixed"])
            end_date = st.date_input("End Date")
            level = st.selectbox("Tournament Level", ["Local", "Regional", "National", "International"])
        
        description = st.text_area("Tournament Description")
        submitted = st.form_submit_button("Add Tournament")
        
        if submitted:
            tournament_data = {
                'name': tournament_name,
                'start_date': str(start_date),
                'end_date': str(end_date),
                'location': location,
                'type': tournament_type,
                'level': level,
                'description': description,
                'created_at': datetime.now().isoformat()
            }
            if save_tournament(tournament_data):
                st.rerun()

# Calendar View
st.subheader("Tournament Schedule")
tournaments_df = load_tournaments()

if not tournaments_df.empty:
    # Prepare calendar events
    calendar_events = []
    for _, tournament in tournaments_df.iterrows():
        calendar_events.append({
            'title': tournament['name'],
            'start': tournament['start_date'],
            'end': tournament['end_date'],
            'description': f"Type: {tournament['type']}\nLevel: {tournament['level']}\nLocation: {tournament['location']}"
        })
    
    # Calendar configuration
    calendar_config = {
        "events": calendar_events,
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay"
        },
        "selectable": True,
        "editable": False
    }
    
    # Display calendar
    calendar(calendar_config)

# Tournament Registration Section
st.subheader("Tournament Registration")
players_df = load_players()

if not tournaments_df.empty and not players_df.empty:
    with st.form("tournament_registration_form"):
        # Select tournament
        selected_tournament = st.selectbox(
            "Select Tournament",
            tournaments_df['name']
        )
        
        # Select players
        selected_players = st.multiselect(
            "Select Players to Register",
            players_df.apply(lambda x: f"{x['first_name']} {x['last_name']}", axis=1)
        )
        
        registration_submitted = st.form_submit_button("Register Players")
        
        if registration_submitted and selected_players:
            tournament_id = tournaments_df[tournaments_df['name'] == selected_tournament]['id'].iloc[0]
            
            for player_name in selected_players:
                player_idx = players_df.apply(
                    lambda x: f"{x['first_name']} {x['last_name']}" == player_name,
                    axis=1
                ).idxmax()
                player_id = players_df.loc[player_idx, 'id']
                
                registration_data = {
                    'tournament_id': tournament_id,
                    'player_id': player_id,
                    'registration_date': datetime.now().isoformat()
                }
                register_player(registration_data)

# View Tournament Details
if not tournaments_df.empty:
    st.subheader("Tournament Details")
    for _, tournament in tournaments_df.iterrows():
        with st.expander(f"{tournament['name']} ({tournament['start_date']} - {tournament['end_date']})"): 
            st.write(f"**Type:** {tournament['type']}")
            st.write(f"**Level:** {tournament['level']}")
            st.write(f"**Location:** {tournament['location']}")
            if tournament['description']:
                st.write(f"**Description:** {tournament['description']}")
            
            # Show registered players
            try:
                registrations = supabase.table('tournament_registrations')\
                    .select('*')\
                    .eq('tournament_id', tournament['id'])\
                    .execute()
                
                if registrations.data:
                    reg_df = pd.DataFrame(registrations.data)
                    registered_players = players_df[players_df['id'].isin(reg_df['player_id'])]
                    
                    st.write("**Registered Players:**")
                    for _, player in registered_players.iterrows():
                        st.write(f"- {player['first_name']} {player['last_name']}")
                else:
                    st.info("No players registered yet.")
            except Exception as e:
                st.error(f"Error loading registrations: {str(e)}")
else:
    st.info("No tournaments found. Add a tournament to get started!")