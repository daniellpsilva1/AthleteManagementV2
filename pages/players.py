import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import os
from dotenv import load_dotenv

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

def load_players():
    try:
        response = supabase.table('players').select('*').execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading players: {str(e)}")
        return pd.DataFrame()

def save_player(player_data):
    try:
        supabase.table('players').insert(player_data).execute()
        st.success("Player added successfully!")
        return True
    except Exception as e:
        st.error(f"Error saving player: {str(e)}")
        return False

def update_player(player_id, player_data):
    try:
        supabase.table('players').update(player_data).eq('id', player_id).execute()
        st.success("Player updated successfully!")
        return True
    except Exception as e:
        st.error(f"Error updating player: {str(e)}")
        return False

# Player Management UI
st.title("🎾 Player Management")

# Add New Player Form
with st.expander("Add New Player"):
    with st.form("new_player_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
            birth_date = st.date_input("Birth Date")
            phone = st.text_input("Phone Number")
        with col2:
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            level = st.selectbox("Player Level", ["Beginner", "Intermediate", "Advanced", "Professional"])
        
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Player")
        
        if submitted:
            player_data = {
                'first_name': first_name,
                'last_name': last_name,
                'birth_date': str(birth_date),
                'email': email,
                'phone': phone,
                'level': level,
                'notes': notes,
                'created_at': datetime.now().isoformat()
            }
            if save_player(player_data):
                st.rerun()

# Display Players
st.subheader("Player List")
players_df = load_players()

if not players_df.empty:
    # Add search functionality
    search_term = st.text_input("Search Players", "")
    if search_term:
        players_df = players_df[players_df.apply(lambda x: search_term.lower() in str(x).lower(), axis=1)]
    
    # Display player data in an interactive table
    st.dataframe(
        players_df[["first_name", "last_name", "email", "phone", "level"]],
        hide_index=True,
        use_container_width=True
    )
    
    # Player Details Section
    if st.button("View/Edit Player Details"):
        selected_player = st.selectbox(
            "Select Player",
            players_df.apply(lambda x: f"{x['first_name']} {x['last_name']}", axis=1)
        )
        
        if selected_player:
            player_idx = players_df.apply(
                lambda x: f"{x['first_name']} {x['last_name']}" == selected_player, 
                axis=1
            ).idxmax()
            player = players_df.loc[player_idx]
            
            with st.form("edit_player_form"):
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name", player['first_name'])
                    birth_date = st.date_input("Birth Date", datetime.strptime(player['birth_date'], '%Y-%m-%d'))
                    phone = st.text_input("Phone Number", player['phone'])
                with col2:
                    last_name = st.text_input("Last Name", player['last_name'])
                    email = st.text_input("Email", player['email'])
                    level = st.selectbox("Player Level", 
                                        ["Beginner", "Intermediate", "Advanced", "Professional"],
                                        index=["Beginner", "Intermediate", "Advanced", "Professional"].index(player['level']))
                
                notes = st.text_area("Notes", player['notes'])
                update_submitted = st.form_submit_button("Update Player")
                
                if update_submitted:
                    player_data = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'birth_date': str(birth_date),
                        'email': email,
                        'phone': phone,
                        'level': level,
                        'notes': notes,
                        'updated_at': datetime.now().isoformat()
                    }
                    if update_player(player['id'], player_data):
                        st.rerun()
else:
    st.info("No players found. Add a new player to get started!")