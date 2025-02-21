import streamlit as st

# Set page config
st.set_page_config(
    page_title="Tennis Player Management",
    page_icon="🎾",
    layout="wide"
)

# Main title with a welcoming message
st.title("🎾 Welcome to Tennis Player Management")
st.markdown("### Your all-in-one solution for managing tennis players, training, and tournaments")

# Create three columns for the main features
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 👥 Player Management")
    st.write("""
    - Maintain detailed player profiles
    - Track player progress and development
    - Manage contact information
    - Monitor skill levels and achievements
    """)
    if st.button("Go to Player Management 👥"):
        st.switch_page("pages/players.py")

with col2:
    st.markdown("### 🏃 Training Dynamics")
    st.write("""
    - Schedule group training sessions
    - Create individual training plans
    - Track performance and attendance
    - Set and monitor training goals
    """)
    if st.button("Go to Training Dynamics 🏃"):
        st.switch_page("pages/training.py")

with col3:
    st.markdown("### 🏆 Tournament Calendar")
    st.write("""
    - Organize and manage tournaments
    - Handle player registrations
    - View tournament schedules
    - Track tournament results
    """)
    if st.button("Go to Tournament Calendar 🏆"):
        st.switch_page("pages/tournament.py")

# Footer with additional information
st.markdown("---")
st.markdown("""
### Get Started
Click on any of the sections above to begin managing your tennis program. Each section provides 
comprehensive tools to help you organize and optimize your tennis operations.
""")