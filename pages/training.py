import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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

# Training Dynamics Page
st.title("🎾 Training Dynamics")

# Helper functions
def load_players():
    try:
        response = supabase.table('players').select('*').execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading players: {str(e)}")
        return pd.DataFrame()

def save_training_plan(plan_data):
    try:
        supabase.table('training_plans').insert(plan_data).execute()
        st.success("Training plan saved successfully!")
        return True
    except Exception as e:
        st.error(f"Error saving training plan: {str(e)}")
        return False

def save_group_session(session_data):
    try:
        supabase.table('group_training_sessions').insert(session_data).execute()
        st.success("Group training session added successfully!")
        return True
    except Exception as e:
        st.error(f"Error saving group session: {str(e)}")
        return False

def save_training_report(report_data):
    try:
        supabase.table('training_reports').insert(report_data).execute()
        st.success("Training report saved successfully!")
        return True
    except Exception as e:
        st.error(f"Error saving training report: {str(e)}")
        return False

# Load players for selection
players_df = load_players()

# Tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["Group Training Schedule", "Individual Training Plans", "Group Training Reports", "Individual Training Reports"])

with tab1:
    st.header("Group Training Schedule")
    
    # Add new group training session
    with st.expander("Add New Group Training Session"):
        with st.form("new_group_session"):
            col1, col2 = st.columns(2)
            with col1:
                session_date = st.date_input("Date")
                session_time = st.time_input("Time")
            with col2:
                level = st.selectbox("Training Level", ["Beginner", "Intermediate", "Advanced", "Professional"])
                max_participants = st.number_input("Maximum Participants", min_value=1, value=8)
            
            notes = st.text_area("Session Notes")
            submitted = st.form_submit_button("Add Session")
            
            if submitted:
                session_data = {
                    'date': str(session_date),
                    'time': str(session_time),
                    'level': level,
                    'max_participants': max_participants,
                    'notes': notes,
                    'created_at': datetime.now().isoformat()
                }
                if save_group_session(session_data):
                    st.rerun()
    
    # View upcoming group sessions
    st.subheader("Upcoming Group Sessions")
    try:
        sessions = supabase.table('group_training_sessions').select('*').execute()
        sessions_df = pd.DataFrame(sessions.data)
        
        if not sessions_df.empty:
            for _, session in sessions_df.iterrows():
                with st.expander(f"{session['date']} - {session['time']} ({session['level']})"):
                    st.write(f"**Maximum Participants:** {session['max_participants']}")
                    if session['notes']:
                        st.write(f"**Notes:** {session['notes']}")
        else:
            st.info("No upcoming group training sessions scheduled.")
    except Exception as e:
        st.error(f"Error loading group sessions: {str(e)}")

with tab2:
    st.header("Individual Training Plans")
    
    if not players_df.empty:
        # Create individual training plan
        with st.expander("Create Individual Training Plan"):
            with st.form("training_plan_form"):
                selected_player = st.selectbox(
                    "Select Player",
                    players_df.apply(lambda x: f"{x['first_name']} {x['last_name']}", axis=1)
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date")
                    duration_weeks = st.number_input("Duration (weeks)", min_value=1, max_value=52, value=4)
                with col2:
                    focus_area = st.selectbox(
                        "Focus Area",
                        ["Technique", "Fitness", "Strategy", "Mental Game", "Match Practice"]
                    )
                    intensity = st.slider("Training Intensity", 1, 5, 3)
                
                technical_goal = st.text_area("Technical Goals")
                fitness_goal = st.text_area("Fitness Goals")
                tactical_goal = st.text_area("Tactical Goals")
                notes = st.text_area("Additional Notes")
                
                submitted = st.form_submit_button("Save Training Plan")
                
                if submitted:
                    player_idx = players_df.apply(
                        lambda x: f"{x['first_name']} {x['last_name']}" == selected_player,
                        axis=1
                    ).idxmax()
                    player_id = players_df.loc[player_idx, 'id']
                    
                    plan_data = {
                        'player_id': player_id,
                        'start_date': str(start_date),
                        'end_date': str(start_date + timedelta(weeks=duration_weeks)),
                        'focus_area': focus_area,
                        'intensity': intensity,
                        'technical_goal': technical_goal,
                        'fitness_goal': fitness_goal,
                        'tactical_goal': tactical_goal,
                        'notes': notes,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    if save_training_plan(plan_data):
                        st.rerun()

with tab3:
    st.header("Group Training Reports")
    
    # Add new group training report
    with st.expander("Add Group Training Report"):
        with st.form("group_report_form"):
            # Load group sessions for selection
            try:
                sessions = supabase.table('group_training_sessions').select('*').execute()
                sessions_df = pd.DataFrame(sessions.data)
                
                if not sessions_df.empty:
                    session = st.selectbox(
                        "Select Training Session",
                        sessions_df.apply(lambda x: f"{x['date']} - {x['time']} ({x['level']})", axis=1)
                    )
                    
                    report_date = st.date_input("Report Date")
                    performance = st.slider("Overall Performance Rating", 1, 5, 3)
                    attendance = st.multiselect(
                        "Select Attendees",
                        players_df.apply(lambda x: f"{x['first_name']} {x['last_name']}", axis=1)
                    )
                    achievements = st.text_area("Key Achievements")
                    improvements = st.text_area("Areas for Improvement")
                    notes = st.text_area("Coach Notes")
                    
                    submitted = st.form_submit_button("Save Report")
                    
                    if submitted:
                        session_idx = sessions_df.apply(
                            lambda x: f"{x['date']} - {x['time']} ({x['level']})" == session,
                            axis=1
                        ).idxmax()
                        session_id = sessions_df.loc[session_idx, 'id']
                        
                        report_data = {
                            'training_type': 'Group',
                            'session_id': session_id,
                            'report_date': str(report_date),
                            'performance_rating': performance,
                            'attendance': attendance,
                            'achievements': achievements,
                            'areas_for_improvement': improvements,
                            'coach_notes': notes,
                            'created_at': datetime.now().isoformat()
                        }
                        
                        if save_training_report(report_data):
                            st.rerun()
                else:
                    st.info("No group training sessions available for reporting.")
            except Exception as e:
                st.error(f"Error loading group sessions: {str(e)}")

with tab4:
    st.header("Individual Training Reports")
    
    # Add new individual training report
    with st.expander("Add Individual Training Report"):
        with st.form("individual_report_form"):
            # Load training plans for selection
            try:
                plans = supabase.table('training_plans').select('*').execute()
                plans_df = pd.DataFrame(plans.data)
                
                if not plans_df.empty:
                    # Merge with player data
                    plans_df = plans_df.merge(
                        players_df[['id', 'first_name', 'last_name']],
                        left_on='player_id',
                        right_on='id',
                        suffixes=('', '_player')
                    )
                    
                    plan = st.selectbox(
                        "Select Training Plan",
                        plans_df.apply(lambda x: f"{x['first_name']} {x['last_name']} - {x['focus_area']} ({x['start_date']} to {x['end_date']})", axis=1)
                    )
                    
                    report_date = st.date_input("Report Date")
                    performance = st.slider("Performance Rating", 1, 5, 3)
                    achievements = st.text_area("Key Achievements")
                    improvements = st.text_area("Areas for Improvement")
                    notes = st.text_area("Coach Notes")
                    
                    submitted = st.form_submit_button("Save Report")
                    
                    if submitted:
                        plan_idx = plans_df.apply(
                            lambda x: f"{x['first_name']} {x['last_name']} - {x['focus_area']} ({x['start_date']} to {x['end_date']})" == plan,
                            axis=1
                        ).idxmax()
                        plan_id = plans_df.loc[plan_idx, 'id']
                        
                        report_data = {
                            'training_type': 'Individual',
                            'training_plan_id': plan_id,
                            'report_date': str(report_date),
                            'performance_rating': performance,
                            'achievements': achievements,
                            'areas_for_improvement': improvements,
                            'coach_notes': notes,
                            'created_at': datetime.now().isoformat()
                        }
                        
                        if save_training_report(report_data):
                            st.rerun()
                else:
                    st.info("No individual training plans available for reporting.")
            except Exception as e:
                st.error(f"Error loading training plans: {str(e)}")