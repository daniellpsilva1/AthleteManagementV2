# Tennis Player Management System

## Overview
A comprehensive tennis player management system built with Streamlit, featuring player profiles, training plans, and tournament management.

## Features
- Player Management
- Training Dynamics
- Tournament Calendar
- Group and Individual Training Reports

## Deployment Guide

### Prerequisites
- Python 3.7 or higher
- Streamlit account
- Supabase account and project

### Local Development
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Supabase credentials:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

3. Run the app:
```bash
streamlit run app.py
```

### Streamlit Cloud Deployment
1. Push your code to a GitHub repository

2. Log in to [Streamlit Cloud](https://streamlit.io/cloud)

3. Deploy from GitHub:
   - Select your repository
   - Set the main file path as `app.py`

4. Configure Environment Variables:
   - In Streamlit Cloud settings, add the following secrets:
     ```
     SUPABASE_URL = 'your_supabase_url'
     SUPABASE_KEY = 'your_supabase_key'
     ```

5. Deploy the app

## Security Note
Never commit the `.env` file to version control. It has been added to `.gitignore` for security.