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
        response = supabase.table('training_reports').insert(report_data).execute()
        report_id = response.data[0]['id']
        st.success("Training report saved successfully!")
        return report_id
    except Exception as e:
        st.error(f"Error saving training report: {str(e)}")
        return None

def save_pse_scores(pse_data_list):
    try:
        supabase.table('player_pse_scores').insert(pse_data_list).execute()
        st.success("PSE scores saved successfully!")
        return True
    except Exception as e:
        st.error(f"Error saving PSE scores: {str(e)}")
        return False

# Initialize session state to avoid duplicate submissions
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

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
            
            if submitted and not st.session_state.form_submitted:
                st.session_state.form_submitted = True
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
    
    # Reset form submitted state when the form is not being submitted
    if not st.session_state.form_submitted:
        st.session_state.form_submitted = False
    
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
                    
                    # Display associated training reports
                    try:
                        reports = supabase.table('training_reports')\
                            .select('*')\
                            .eq('training_type', 'Group')\
                            .eq('session_id', session['id'])\
                            .execute()
                        
                        reports_df = pd.DataFrame(reports.data)
                        
                        if not reports_df.empty:
                            st.markdown("---")
                            st.markdown("### Training Reports")
                            for _, report in reports_df.iterrows():
                                st.markdown(f"**Report Date:** {report['report_date']}")
                                st.markdown(f"**Performance Rating:** {'⭐' * report['performance_rating']}")
                                if report['achievements']:
                                    st.markdown(f"**Key Achievements:**\n{report['achievements']}")
                                if report['areas_for_improvement']:
                                    st.markdown(f"**Areas for Improvement:**\n{report['areas_for_improvement']}")
                                if report['coach_notes']:
                                    st.markdown(f"**Coach Notes:**\n{report['coach_notes']}")
                                
                                # Display PSE scores
                                try:
                                    pse_scores = supabase.table('player_pse_scores')\
                                        .select('*')\
                                        .eq('report_id', report['id'])\
                                        .execute()
                                    
                                    if pse_scores.data:
                                        st.markdown("**PSE Scores:**")
                                        for pse in pse_scores.data:
                                            player = players_df[players_df['id'] == pse['player_id']].iloc[0]
                                            st.markdown(f"*{player['first_name']} {player['last_name']}:*")
                                            st.markdown(f"PSE Score: {'⭐' * pse['pse_score']}")
                                except Exception as e:
                                    st.error(f"Error loading PSE scores: {str(e)}")
                                st.markdown("---")
                        else:
                            st.info("No training reports available for this session.")
                    except Exception as e:
                        st.error(f"Error loading training reports: {str(e)}")
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
                
                if submitted and not st.session_state.form_submitted:
                    st.session_state.form_submitted = True
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

# Modification for tab3 (Group Training Reports)
# Replace the current form handling in tab3 with this:

with tab3:
    st.header("Group Training Reports")
    
    # Add new group training report
    with st.expander("Add Group Training Report"):
        # Check if we are in PSE score entry mode
        if 'report_id' in st.session_state and 'attendees' in st.session_state:
            st.subheader("Enter PSE Scores")
            
            with st.form("pse_scores_form"):
                pse_scores = {}
                for player in st.session_state.attendees:
                    st.write(f"**{player}**")
                    pse_score = st.slider("PSE Score", 1, 10, 5, key=f"pse_{player}")
                    pse_scores[player] = {
                        "pse_score": pse_score
                    }
                
                pse_submitted = st.form_submit_button("Save PSE Scores")
                
                if pse_submitted:
                    # Save PSE scores for each attendee as a batch
                    pse_data_list = []
                    for player in st.session_state.attendees:
                        player_idx = players_df.apply(
                            lambda x: f"{x['first_name']} {x['last_name']}" == player,
                            axis=1
                        ).idxmax()
                        player_id = players_df.loc[player_idx, 'id']
                        
                        pse_data_list.append({
                            'player_id': player_id,
                            'report_id': st.session_state.report_id,
                            'pse_score': pse_scores[player]['pse_score'],
                            'created_at': datetime.now().isoformat()
                        })
                    
                    if pse_data_list and save_pse_scores(pse_data_list):
                        # Clear the session state
                        del st.session_state.report_id
                        del st.session_state.attendees
                        st.rerun()
        else:
            # Original form for report creation
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
                        
                        submitted = st.form_submit_button("Save Report and Continue to PSE Scores")
                        
                        if submitted and not st.session_state.form_submitted:
                            st.session_state.form_submitted = True
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
                            
                            report_id = save_training_report(report_data)
                            if report_id and attendance:
                                # Store the report ID and attendees in session state
                                st.session_state.report_id = report_id
                                st.session_state.attendees = attendance
                                st.rerun()
                    else:
                        st.info("No group training sessions available for reporting.")
                except Exception as e:
                    st.error(f"Error loading group sessions: {str(e)}")

# Modification for tab4 (Individual Training Reports)
# Replace the current form handling in tab4 with this:

with tab4:
    st.header("Individual Training Reports")
    
    # Add new individual training report
    with st.expander("Add Individual Training Report"):
        # Check if we are in PSE score entry mode
        if 'individual_report_id' in st.session_state and 'player_id' in st.session_state:
            st.subheader("Enter PSE Score")
            
            with st.form("individual_pse_form"):
                pse_score = st.slider("PSE Score", 1, 10, 5, key="pse_individual")
                
                pse_submitted = st.form_submit_button("Save PSE Score")
                
                if pse_submitted:
                    # Save PSE score
                    pse_data = [{
                        'player_id': st.session_state.player_id,
                        'report_id': st.session_state.individual_report_id,
                        'pse_score': pse_score,
                        'created_at': datetime.now().isoformat()
                    }]
                    
                    if save_pse_scores(pse_data):
                        # Clear the session state
                        del st.session_state.individual_report_id
                        del st.session_state.player_id
                        st.rerun()
        else:
            # Original form for report creation
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
                        
                        submitted = st.form_submit_button("Save Report and Continue to PSE Score")
                        
                        if submitted and not st.session_state.form_submitted:
                            st.session_state.form_submitted = True
                            plan_idx = plans_df.apply(
                                lambda x: f"{x['first_name']} {x['last_name']} - {x['focus_area']} ({x['start_date']} to {x['end_date']})" == plan,
                                axis=1
                            ).idxmax()
                            plan_id = plans_df.loc[plan_idx, 'id']
                            player_id = plans_df.loc[plan_idx, 'player_id']
                            
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
                            
                            report_id = save_training_report(report_data)
                            if report_id:
                                # Store the report ID and player ID in session state
                                st.session_state.individual_report_id = report_id
                                st.session_state.player_id = player_id
                                st.rerun()
                    else:
                        st.info("No individual training plans available for reporting.")
                except Exception as e:
                    st.error(f"Error loading training plans: {str(e)}")

# Reset the form_submitted state if we're not in the middle of a form submission
if st.session_state.form_submitted:
    st.session_state.form_submitted = False