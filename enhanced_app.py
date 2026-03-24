# Enhanced Mental Health Screening App with Sentiment Analysis
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List
import re
import os
import json
import hashlib
import secrets

# Data Storage Configuration
DATA_DIR = "user_data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CURRENT_USER_FILE = os.path.join(DATA_DIR, "current_user.json")

def get_user_data_dir(username):
    """Get user-specific data directory"""
    if username == "guest":
        return os.path.join(DATA_DIR, "guest_session")
    return os.path.join(DATA_DIR, "users", username)

def get_user_files(username):
    """Get user-specific file paths"""
    user_dir = get_user_data_dir(username)
    return {
        'mood': os.path.join(user_dir, "mood_history.json"),
        'journal': os.path.join(user_dir, "journal_entries.json"),
        'screening': os.path.join(user_dir, "screening_results.json"),
        'profile': os.path.join(user_dir, "user_profile.json")
    }

# Create data directories if they don't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if not os.path.exists(os.path.join(DATA_DIR, "users")):
    os.makedirs(os.path.join(DATA_DIR, "users"))
if not os.path.exists(os.path.join(DATA_DIR, "guest_session")):
    os.makedirs(os.path.join(DATA_DIR, "guest_session"))

# Authentication Functions
def hash_password(password):
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwd_hash.hex()

def verify_password(password, hashed):
    """Verify password against hash"""
    salt = hashed[:32]
    stored_hash = hashed[32:]
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return pwd_hash.hex() == stored_hash

def load_users():
    """Load users database"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception:
        return {}

def save_users(users_db):
    """Save users database"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_db, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def create_user(username, password, full_name, role="user"):
    """Create new user account"""
    users_db = load_users()
    
    if username in users_db:
        return False, "Username already exists"
    
    # Create user directory
    user_dir = get_user_data_dir(username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    
    # Add user to database
    users_db[username] = {
        'password_hash': hash_password(password),
        'full_name': full_name,
        'role': role,
        'created_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'last_login': None,
        'active': True
    }
    
    if save_users(users_db):
        return True, "Account created successfully"
    return False, "Failed to create account"

def authenticate_user(username, password):
    """Authenticate user login"""
    users_db = load_users()
    
    if username not in users_db:
        return False, "Username not found"
    
    user = users_db[username]
    if not user.get('active', True):
        return False, "Account is disabled"
    
    if verify_password(password, user['password_hash']):
        # Update last login
        users_db[username]['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_users(users_db)
        return True, "Login successful"
    
    return False, "Invalid password"

def get_current_user():
    """Get currently logged in user"""
    try:
        if os.path.exists(CURRENT_USER_FILE):
            with open(CURRENT_USER_FILE, 'r', encoding='utf-8') as f:
                return json.load(f).get('username')
        return None
    except Exception:
        return None

def set_current_user(username):
    """Set current logged in user"""
    try:
        with open(CURRENT_USER_FILE, 'w', encoding='utf-8') as f:
            json.dump({'username': username, 'login_time': datetime.now().strftime("%Y-%m-%d %H:%M")}, f)
        return True
    except Exception:
        return False

def logout_user():
    """Logout current user"""
    try:
        if os.path.exists(CURRENT_USER_FILE):
            os.remove(CURRENT_USER_FILE)
        return True
    except Exception:
        return False

# Storage Functions
def save_to_file(data, filename):
    """Save data to JSON file"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def load_from_file(filename, default=None):
    """Load data from JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default if default is not None else []
    except Exception as e:
        print(f"Error loading data: {e}")
        return default if default is not None else []

def save_all_data():
    """Save all session data to files"""
    if 'current_user' not in st.session_state:
        return False
    
    username = st.session_state.current_user
    files = get_user_files(username)
    
    save_to_file(st.session_state.mood_history, files['mood'])
    save_to_file(st.session_state.journal_entries, files['journal'])
    save_to_file(st.session_state.screening_results, files['screening'])
    save_to_file(st.session_state.user_profile, files['profile'])
    return True

def load_all_data():
    """Load all data from files into session state"""
    if 'current_user' not in st.session_state:
        return False
    
    username = st.session_state.current_user
    files = get_user_files(username)
    
    st.session_state.mood_history = load_from_file(files['mood'], [])
    st.session_state.journal_entries = load_from_file(files['journal'], [])
    st.session_state.screening_results = load_from_file(files['screening'], {})
    st.session_state.user_profile = load_from_file(files['profile'], {})
    return True

# For sentiment analysis
try:
    from textblob import TextBlob
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    st.warning("Install textblob for sentiment analysis: pip install textblob")

# For audio recording
try:
    from audio_recorder_streamlit import audio_recorder
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False

# For speech recognition
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Mental Health Screening App",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
def init_session_state():
    # Initialize authentication state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    
    # Load data only if authenticated
    if st.session_state.authenticated and 'data_loaded' not in st.session_state:
        load_all_data()
        st.session_state.data_loaded = True
    
    # Initialize data structures
    if 'mood_history' not in st.session_state:
        st.session_state.mood_history = []
    if 'journal_entries' not in st.session_state:
        st.session_state.journal_entries = []
    if 'screening_results' not in st.session_state:
        st.session_state.screening_results = {}
    if 'user_age' not in st.session_state:
        st.session_state.user_age = None
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    if 'comprehensive_screening' not in st.session_state:
        st.session_state.comprehensive_screening = {
            'phq9_responses': None,
            'gad7_responses': None,
            'stress_responses': None,
            'current_step': 1,
            'calculated_results': None
        }

init_session_state()

# Authentication Check - Show login if not authenticated
if not st.session_state.authenticated:
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🧠 Mental Health Screening Platform</h1>
        <h3>Professional Mental Health Assessment & Wellness Support</h3>
        <p style="color: #666; margin-bottom: 2rem;">Secure, confidential, and clinically validated</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if any users exist (smart login detection)
    users_db = load_users()
    has_users = len(users_db) > 0
    
    # FIRST TIME USER - No accounts exist yet
    if not has_users:
        st.info("👋 Welcome! Let's create your first account to get started.")
        
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.markdown("### 👤 Create Your Account")
            
            with st.form("first_account_form"):
                full_name = st.text_input("Full Name", placeholder="Enter your full name")
                new_username = st.text_input("Choose Username", placeholder="Enter desired username")
                new_password = st.text_input("Choose Password", type="password", placeholder="Enter secure password (min 6 characters)")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                
                register_btn = st.form_submit_button("✨ Create Account & Start", use_container_width=True, type="primary")
                
                if register_btn:
                    if full_name and new_username and new_password and confirm_password:
                        if new_password != confirm_password:
                            st.error("❌ Passwords do not match")
                        elif len(new_password) < 6:
                            st.error("❌ Password must be at least 6 characters")
                        elif len(new_username) < 3:
                            st.error("❌ Username must be at least 3 characters")
                        else:
                            success, message = create_user(new_username, new_password, full_name)
                            if success:
                                st.success(f"✅ Account created! Logging you in...")
                                # Auto-login after registration
                                st.session_state.authenticated = True
                                st.session_state.current_user = new_username
                                set_current_user(new_username)
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                    else:
                        st.error("❌ Please fill in all fields")
        
        with col_side:
            st.markdown("### 🎯 What You'll Get")
            st.markdown("""
            - 📊 **Mood Tracking**  
              Track your daily emotions
            
            - 📝 **Private Journal**  
              Secure personal space
            
            - 🔥 **Streak System**  
              Build healthy habits
            
            - 🏆 **Achievements**  
              Unlock milestones
            
            - 📈 **Progress Analytics**  
              Visualize your journey
            
            - 🔍 **Mental Health Screening**  
              Professional assessments
            """)
        
        st.markdown("---")
        
        # Guest mode always available
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("🚪 Continue as Guest", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.current_user = "guest"
                set_current_user("guest")
                st.success("✅ Welcome! You're using Guest Mode.")
                st.rerun()
        with col2:
            st.caption("💡 Try the app without creating an account. Your data won't be permanently saved.")
    
    # RETURNING USER - Accounts exist
    else:
        tab1, tab2, tab3 = st.tabs(["🔐 Login", "👤 Create Account", "🚪 Guest Access"])
        
        with tab1:
            st.markdown("### 🔐 Welcome Back!")
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    login_btn = st.form_submit_button("🔐 Login", use_container_width=True, type="primary")
                
                if login_btn:
                    if username and password:
                        success, message = authenticate_user(username, password)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.current_user = username
                            set_current_user(username)
                            st.session_state.login_attempts = 0
                            st.success(f"✅ Welcome back, {username}!")
                            st.rerun()
                        else:
                            st.session_state.login_attempts += 1
                            st.error(f"❌ {message}")
                            if st.session_state.login_attempts >= 3:
                                st.warning("⚠️ Multiple failed attempts. Please check your credentials or use Guest Access.")
                    else:
                        st.error("❌ Please enter both username and password")
            
            st.info("💡 First time here? Go to the 'Create Account' tab!")
        
        with tab2:
            st.markdown("### 👤 Create New Account")
            
            with st.form("register_form"):
                full_name = st.text_input("Full Name", placeholder="Enter your full name")
                new_username = st.text_input("Choose Username", placeholder="Enter desired username")
                new_password = st.text_input("Choose Password", type="password", placeholder="Enter secure password (min 6 characters)")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                
                st.info("💡 **Account Benefits:** Secure data storage, progress tracking, streak system, achievements")
                
                register_btn = st.form_submit_button("👤 Create Account", use_container_width=True, type="primary")
                
                if register_btn:
                    if full_name and new_username and new_password and confirm_password:
                        if new_password != confirm_password:
                            st.error("❌ Passwords do not match")
                        elif len(new_password) < 6:
                            st.error("❌ Password must be at least 6 characters")
                        elif len(new_username) < 3:
                            st.error("❌ Username must be at least 3 characters")
                        else:
                            success, message = create_user(new_username, new_password, full_name)
                            if success:
                                st.success(f"✅ Account created successfully!")
                                st.info("🔐 Go to the 'Login' tab to sign in with your new account")
                            else:
                                st.error(f"❌ {message}")
                    else:
                        st.error("❌ Please fill in all fields")
        
        with tab3:
            st.markdown("### 🚪 Guest Access")
            st.info("💡 **Guest Mode:** Full access to all features. Data saved temporarily for this session only.")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🚪 Continue as Guest", use_container_width=True, type="primary"):
                    st.session_state.authenticated = True
                    st.session_state.current_user = "guest"
                    set_current_user("guest")
                    st.success("✅ Welcome! You're using Guest Mode.")
                    st.rerun()
            
            with col2:
                st.markdown("**Guest Limitations:**")
                st.caption("• Data not permanently saved")
                st.caption("• No streak tracking")
                st.caption("• Session expires on close")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem;">
        <p>🔒 Your privacy is protected. All data is stored locally and encrypted.</p>
        <p>📞 Crisis Support: India: 1860-2662-345 (Vandrevala) | International: 988 | Emergency: 112</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()  # Stop execution here if not authenticated

# If authenticated, load user data
if st.session_state.authenticated and st.session_state.current_user:
    # Load user data if not already loaded
    if 'data_loaded' not in st.session_state or not st.session_state.data_loaded:
        load_all_data()
        st.session_state.data_loaded = True

# Navigation helper
PAGE_ORDER = ["🏠 Dashboard", "👤 Profile", "📊 Daily Mood Tracker", "📝 Journal",
              "🔍 Screening Modules", "📋 Comprehensive Report", "📈 Trend Analysis",
              "🎮 Stress Relief Games", "🥗 Healthy Nutrition", "📞 Resources"]

def next_page_button(current_page):
    """Render a Next button that navigates to the next page."""
    idx = PAGE_ORDER.index(current_page) if current_page in PAGE_ORDER else -1
    if idx != -1 and idx < len(PAGE_ORDER) - 1:
        next_pg = PAGE_ORDER[idx + 1]
        st.markdown("---")
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button(f"Next: {next_pg} →", use_container_width=True, key=f"next_{idx}"):
                st.session_state.nav_to = next_pg
                st.rerun()

# Sentiment Analysis Functions
def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze sentiment of text using TextBlob"""
    if not SENTIMENT_AVAILABLE or not text:
        return {'polarity': 0, 'subjectivity': 0, 'sentiment': 'Neutral', 'score': 5}
    
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        
        # Classify sentiment
        if polarity > 0.3:
            sentiment = 'Positive'
        elif polarity < -0.3:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'sentiment': sentiment,
            'score': (polarity + 1) * 5  # Convert to 0-10 scale
        }
    except:
        return {'polarity': 0, 'subjectivity': 0, 'sentiment': 'Neutral', 'score': 5}

def get_sentiment_emoji(sentiment: str) -> str:
    """Get emoji for sentiment"""
    emojis = {
        'Positive': '😊',
        'Neutral': '😐',
        'Negative': '😔'
    }
    return emojis.get(sentiment, '😐')

def analyze_mood_from_text(text: str) -> int:
    """Estimate mood score from text sentiment"""
    analysis = analyze_sentiment(text)
    return int(analysis['score'])

def load_audio_file(filename: str):
    """Load audio file from audio folder"""
    audio_path = os.path.join("audio", filename)
    if os.path.exists(audio_path):
        with open(audio_path, 'rb') as audio_file:
            return audio_file.read()
    return None


# Calming CSS Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');

* {
    font-family: 'Poppins', sans-serif;
}

/* Ensure text is always readable on teal background */
.stMarkdown, .stText, p, h1, h2, h3, h4, label {
    color: #1a1a1a !important;
}

.stApp {
    background: linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 25%, #80cbc4 50%, #4db6ac 75%, #26a69a 100%);
    background-attachment: scroll;
    min-height: 100vh;
}

/* Calming color palette */
:root {
    --calm-teal: #26a69a;
    --calm-mint: #80cbc4;
    --calm-sage: #a5d6a7;
    --calm-lavender: #b39ddb;
    --calm-peach: #ffccbc;
}

.metric-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.85));
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    color: #2c3e50;
    box-shadow: 0 8px 32px rgba(38, 166, 154, 0.2);
    border: 2px solid rgba(38, 166, 154, 0.3);
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(38, 166, 154, 0.3);
}

.resource-card {
    background: rgba(255, 255, 255, 0.9);
    border-left: 5px solid var(--calm-teal);
    padding: 20px;
    margin: 15px 0;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.profile-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(179, 157, 219, 0.1));
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border: 2px solid rgba(179, 157, 219, 0.3);
}

/* Soft buttons */
.stButton>button {
    background: linear-gradient(135deg, var(--calm-teal), var(--calm-mint)) !important;
    color: white !important;
    border: none !important;
    border-radius: 25px !important;
    padding: 12px 30px !important;
    font-weight: 500 !important;
    box-shadow: 0 4px 15px rgba(38, 166, 154, 0.3) !important;
    transition: all 0.3s ease !important;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(38, 166, 154, 0.4) !important;
}

/* Soft inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    border-radius: 15px !important;
    border: 2px solid rgba(38, 166, 154, 0.5) !important;
    background: #ffffff !important;
    color: #1a1a1a !important;
}

.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: var(--calm-teal) !important;
    box-shadow: 0 0 0 3px rgba(38, 166, 154, 0.1) !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: #ffffff !important;
    color: #1a1a1a !important;
    border-radius: 15px !important;
    border: 2px solid rgba(38, 166, 154, 0.5) !important;
}

/* Download button fix */
.stDownloadButton > button {
    background: linear-gradient(135deg, var(--calm-teal), var(--calm-mint)) !important;
    color: white !important;
    border: none !important;
    border-radius: 25px !important;
    font-weight: 500 !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #e0f2f1, #b2dfdb) !important;
}

/* Radio buttons */
.stRadio > label {
    background: rgba(255, 255, 255, 0.95);
    padding: 12px 20px;
    border-radius: 15px;
    margin: 5px 0;
    border: 2px solid rgba(38, 166, 154, 0.2);
    transition: all 0.3s ease;
    color: #1a1a1a !important;
}

.stRadio > label:hover {
    background: rgba(38, 166, 154, 0.1);
    border-color: var(--calm-teal);
}

/* Force question label text to be dark and visible */
.stRadio p, .stRadio label, div[data-testid="stRadio"] p {
    color: #1a1a1a !important;
    font-weight: 600 !important;
}

/* Info boxes */
.stInfo {
    background: rgba(165, 214, 167, 0.2) !important;
    border-left: 5px solid var(--calm-sage) !important;
    border-radius: 10px !important;
}

.stSuccess {
    background: rgba(165, 214, 167, 0.3) !important;
    border-left: 5px solid var(--calm-sage) !important;
}

.stWarning {
    background: rgba(255, 204, 188, 0.3) !important;
    border-left: 5px solid var(--calm-peach) !important;
}

.stError {
    background: rgba(239, 154, 154, 0.3) !important;
    border-left: 5px solid #ef9a9a !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 10px;
    border: 2px solid rgba(38, 166, 154, 0.2);
}

/* Slider */
.stSlider > div > div > div {
    background: var(--calm-mint) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 15px;
    padding: 10px 20px;
    border: 2px solid rgba(38, 166, 154, 0.2);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--calm-teal), var(--calm-mint));
    color: white;
}
</style>
""", unsafe_allow_html=True)

# GAD-7 Questions
GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it's hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid as if something awful might happen"
]

# PHQ-9 Questions (Depression)
PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself - or that you are a failure or have let yourself or your family down",
    "Trouble concentrating on things, such as reading the newspaper or watching television",
    "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
    "Thoughts that you would be better off dead, or of hurting yourself in some way"
]

# Stress Scale Questions
STRESS_QUESTIONS = [
    "How often have you been upset because of something unexpected?",
    "How often have you felt unable to control important things in your life?",
    "How often have you felt nervous and stressed?",
    "How often have you felt confident about handling personal problems?",
    "How often have you felt things were going your way?",
    "How often have you found that you could not cope with all the things you had to do?",
    "How often have you been able to control irritations in your life?",
    "How often have you felt that you were on top of things?",
    "How often have you been angered because of things outside your control?",
    "How often have you felt difficulties were piling up so high you could not overcome them?"
]

# PTSD Checklist (PCL-5) - Simplified
PTSD_QUESTIONS = [
    "Repeated, disturbing, and unwanted memories of the stressful experience",
    "Repeated, disturbing dreams of the stressful experience",
    "Suddenly feeling or acting as if the stressful experience were actually happening again",
    "Feeling very upset when something reminded you of the stressful experience",
    "Having strong physical reactions when something reminded you of the stressful experience",
    "Avoiding memories, thoughts, or feelings related to the stressful experience",
    "Avoiding external reminders of the stressful experience",
    "Trouble remembering important parts of the stressful experience",
    "Having strong negative beliefs about yourself, other people, or the world",
    "Blaming yourself or someone else for the stressful experience or what happened after it",
    "Having strong negative feelings such as fear, horror, anger, guilt, or shame",
    "Loss of interest in activities that you used to enjoy",
    "Feeling distant or cut off from other people",
    "Trouble experiencing positive feelings",
    "Irritable behavior, angry outbursts, or acting aggressively",
    "Taking too many risks or doing things that could cause you harm",
    "Being super alert or watchful or on guard",
    "Feeling jumpy or easily startled",
    "Having difficulty concentrating",
    "Trouble falling or staying asleep"
]

# Social Anxiety Inventory (SPIN) - Simplified
SOCIAL_ANXIETY_QUESTIONS = [
    "I am afraid of people in authority",
    "I am bothered by blushing in front of people",
    "Parties and social events scare me",
    "I avoid talking to people I don't know",
    "Being criticized scares me a lot",
    "I avoid doing things or speaking to people for fear of embarrassment",
    "Sweating in front of people causes me distress",
    "I avoid going to parties",
    "I avoid activities in which I am the center of attention",
    "Talking to strangers scares me",
    "I avoid having to give speeches",
    "I would do anything to avoid being criticized",
    "Heart palpitations bother me when I am around people",
    "I am afraid of doing things when people might be watching",
    "Being embarrassed or looking stupid are among my worst fears",
    "I avoid speaking to anyone in authority",
    "Trembling or shaking in front of others is distressing to me"
]

# Obsessive-Compulsive Inventory (OCI-R)
OCD_QUESTIONS = [
    "I have saved up so many things that they get in the way",
    "I check things more often than necessary",
    "I get upset if objects are not arranged properly",
    "I feel compelled to count while I am doing things",
    "I find it difficult to touch an object when I know it has been touched by strangers",
    "I find it difficult to control my own thoughts",
    "I collect things I don't need",
    "I repeatedly check doors, windows, drawers, etc.",
    "I get upset if others change the way I have arranged things",
    "I feel I have to repeat certain numbers",
    "I sometimes have to wash or clean myself simply because I feel contaminated",
    "I am upset by unpleasant thoughts that come into my mind against my will",
    "I avoid throwing things away because I am afraid I might need them later",
    "I repeatedly check gas and water taps and light switches after turning them off",
    "I need things to be arranged in a particular order",
    "I feel that there are good and bad numbers",
    "I wash my hands more often and longer than necessary",
    "I frequently get nasty thoughts and have difficulty in getting rid of them"
]

# Eating Attitudes Test (EAT-26) - Simplified
EATING_DISORDER_QUESTIONS = [
    "Am terrified about being overweight",
    "Avoid eating when I am hungry",
    "Find myself preoccupied with food",
    "Have gone on eating binges where I feel that I may not be able to stop",
    "Cut my food into small pieces",
    "Aware of the calorie content of foods that I eat",
    "Particularly avoid food with a high carbohydrate content",
    "Feel that others would prefer if I ate more",
    "Vomit after I have eaten",
    "Feel extremely guilty after eating",
    "Am preoccupied with a desire to be thinner",
    "Think about burning up calories when I exercise",
    "Other people think that I am too thin",
    "Am preoccupied with the thought of having fat on my body",
    "Take longer than others to eat my meals",
    "Avoid foods with sugar in them",
    "Eat diet foods",
    "Feel that food controls my life",
    "Display self-control around food",
    "Feel that others pressure me to eat",
    "Give too much time and thought to food",
    "Feel uncomfortable after eating sweets",
    "Engage in dieting behavior",
    "Like my stomach to be empty",
    "Have the impulse to vomit after meals",
    "Enjoy trying new rich foods"
]

# Alcohol Use Disorders Identification Test (AUDIT-C)
ALCOHOL_QUESTIONS = [
    "How often do you have a drink containing alcohol?",
    "How many standard drinks containing alcohol do you have on a typical day?",
    "How often do you have six or more drinks on one occasion?",
    "How often during the last year have you found that you were not able to stop drinking once you had started?",
    "How often during the last year have you failed to do what was normally expected of you because of drinking?",
    "How often during the last year have you needed a drink in the morning to get yourself going after a heavy drinking session?",
    "How often during the last year have you had a feeling of guilt or remorse after drinking?",
    "How often during the last year have you been unable to remember what happened the night before because of your drinking?",
    "Have you or someone else been injured because of your drinking?",
    "Has a relative, friend, doctor, or other health care worker been concerned about your drinking or suggested you cut down?"
]

# Insomnia Severity Index (ISI)
INSOMNIA_QUESTIONS = [
    "Difficulty falling asleep",
    "Difficulty staying asleep",
    "Problem waking up too early",
    "How satisfied/dissatisfied are you with your current sleep pattern?",
    "How noticeable to others do you think your sleeping problem is in terms of impairing the quality of your life?",
    "How worried/distressed are you about your current sleep problem?",
    "To what extent do you consider your sleep problem to interfere with your daily functioning?"
]

# Bipolar Spectrum Diagnostic Scale (BSDS) - Key Questions
BIPOLAR_QUESTIONS = [
    "My mood and energy are generally stable",
    "I have periods of extreme happiness and high energy",
    "I have periods of extreme sadness and low energy",
    "My mood swings between highs and lows",
    "During high periods, I need less sleep than usual",
    "During high periods, I am more talkative than usual",
    "During high periods, my thoughts race",
    "During high periods, I take on many projects at once",
    "During high periods, I am more impulsive or reckless",
    "During high periods, I am more irritable",
    "These mood changes cause problems in my life",
    "Family members have noticed these mood changes"
]

# Mental Health Resources
RESOURCES = {
    "🇮🇳 Indian Crisis Helplines": [
        {"name": "Vandrevala Foundation", "contact": "1860-2662-345 / 1800-2333-330", "available": "24/7", "languages": "English, Hindi, Regional"},
        {"name": "AASRA (Mumbai)", "contact": "91-9820466726", "available": "24/7", "languages": "English, Hindi"},
        {"name": "Sneha Foundation (Chennai)", "contact": "044-24640050", "available": "24/7", "languages": "English, Tamil, Hindi"},
        {"name": "iCall (TISS)", "contact": "9152987821", "available": "Mon-Sat, 8 AM-10 PM", "languages": "English, Hindi, Marathi"},
        {"name": "Fortis Stress Helpline", "contact": "8376804102", "available": "24/7", "languages": "English, Hindi"}
    ],
    "🇮🇳 Indian Mental Health Support": [
        {"name": "NIMHANS Helpline (Bangalore)", "contact": "080-46110007", "available": "Mon-Sat, 9 AM-5:30 PM", "languages": "English, Hindi, Kannada"},
        {"name": "Mann Talks", "contact": "8686139139", "available": "Mon-Sat, 10 AM-6 PM", "languages": "English, Hindi"},
        {"name": "Women's Helpline", "contact": "1091 / 181", "available": "24/7", "languages": "All regional languages"},
        {"name": "Childline India", "contact": "1098", "available": "24/7", "languages": "All regional languages"}
    ],
    "🇮🇳 Indian Emergency": [
        {"name": "Emergency Services", "contact": "112", "available": "24/7"},
        {"name": "Police", "contact": "100", "available": "24/7"},
        {"name": "Ambulance", "contact": "102 / 108", "available": "24/7"}
    ],
    "🌍 International Crisis Helplines": [
        {"name": "US - Suicide & Crisis Lifeline", "contact": "988", "available": "24/7"},
        {"name": "US - Crisis Text Line", "contact": "Text HOME to 741741", "available": "24/7"},
        {"name": "UK - Samaritans", "contact": "116 123", "available": "24/7"},
        {"name": "Australia - Lifeline", "contact": "13 11 14", "available": "24/7"},
        {"name": "Canada - Crisis Services", "contact": "1-833-456-4566", "available": "24/7"}
    ],
    "Counseling Services": [
        {"name": "BetterHelp", "type": "Online Therapy", "url": "betterhelp.com"},
        {"name": "Talkspace", "type": "Online Therapy", "url": "talkspace.com"},
        {"name": "Psychology Today", "type": "Therapist Directory", "url": "psychologytoday.com"}
    ],
    "Support Platforms": [
        {"name": "7 Cups", "type": "Peer Support", "url": "7cups.com"},
        {"name": "NAMI", "type": "Mental Health Organization", "url": "nami.org"},
        {"name": "Mental Health America", "type": "Resources & Screening", "url": "mhanational.org"}
    ]
}

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🧠 Mental Health Screening")
    
    # User info and logout
    if st.session_state.authenticated and st.session_state.current_user:
        users_db = load_users()
        current_user = st.session_state.current_user
        
        if current_user == "guest":
            st.info("👤 **Guest User**")
            st.caption("Temporary session")
        else:
            user_info = users_db.get(current_user, {})
            st.success(f"👤 **{user_info.get('full_name', current_user)}**")
            st.caption(f"@{current_user}")
            if user_info.get('last_login'):
                st.caption(f"Last login: {user_info['last_login']}")
            
            # Show streak information
            st.markdown("---")
            st.markdown("### 🔥 Wellness Streak")
            
            try:
                from database import db
                user = db.get_user_by_username(current_user)
                if user:
                    user_id = user['user_id']
                    streak_stats = db.get_streak_statistics(user_id)
                    current_streak = streak_stats['combined']['current_streak']
                    longest_streak = streak_stats['combined']['longest_streak']
                    total_days = streak_stats['combined']['total_days']
                    achievements = [a for a in streak_stats['achievements'] if a.get('unlocked')]
                    
                    # Streak metrics in sidebar
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("🔥 Current", f"{current_streak} days")
                    
                    with col2:
                        st.metric("🏆 Best", f"{longest_streak} days")
                    
                    st.caption(f"📊 Total: {total_days} days")
                    if achievements:
                        st.caption(f"🎖️ {len(achievements)} achievements")
                else:
                    st.info("Start tracking to build your streak!")
            except Exception as e:
                st.info("💡 Streak tracking requires database setup")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.data_loaded = False
            # Clear session data
            for key in ['mood_history', 'journal_entries', 'screening_results', 'user_profile']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Check if there's a navigation request
    if 'nav_to' in st.session_state:
        st.session_state.current_page = st.session_state.nav_to
        del st.session_state.nav_to

    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Dashboard"

    page_options = ["🏠 Dashboard", "👤 Profile", "📊 Daily Mood Tracker", "📝 Journal", 
                   "🔍 Screening Modules", "📋 Comprehensive Report", "📈 Trend Analysis", "🎮 Stress Relief Games", "🥗 Healthy Nutrition", "📞 Resources"]
    
    current_index = page_options.index(st.session_state.current_page) if st.session_state.current_page in page_options else 0

    page = st.radio(
        "Navigation",
        page_options,
        index=current_index,
        label_visibility="collapsed"
    )
    st.session_state.current_page = page
    
    st.markdown("---")
    
    # Quick Profile Summary
    if st.session_state.user_age:
        st.markdown("### 👤 Quick Profile")
        st.info(f"**Age:** {st.session_state.user_age}")
        if st.session_state.user_profile.get('name'):
            st.info(f"**Name:** {st.session_state.user_profile['name']}")
    else:
        st.warning("⚠️ Please complete your profile")
    
    st.markdown("---")
    
    # Data Management
    st.markdown("### 💾 Data Management")
    
    # Show data stats
    mood_count = len(st.session_state.mood_history)
    journal_count = len(st.session_state.journal_entries)
    screening_count = len(st.session_state.screening_results)
    
    st.caption(f"📊 Mood entries: {mood_count}")
    st.caption(f"📝 Journal entries: {journal_count}")
    st.caption(f"🔍 Screenings: {screening_count}")
    
    # Manual save button
    if st.button("💾 Save All Data", use_container_width=True):
        save_all_data()
        st.success("✅ Data saved!")
    
    # Clear data button
    if st.button("🗑️ Clear All Data", use_container_width=True):
        if st.checkbox("⚠️ Confirm deletion"):
            st.session_state.mood_history = []
            st.session_state.journal_entries = []
            st.session_state.screening_results = {}
            st.session_state.user_profile = {}
            st.session_state.user_age = None
            save_all_data()
            st.success("✅ All data cleared!")
            st.rerun()

# Page: Dashboard
if page == "🏠 Dashboard":
    st.title("🏠 Mental Health Dashboard")
    
    # Welcome message
    if st.session_state.user_profile.get('name'):
        st.markdown(f"### Welcome back, {st.session_state.user_profile['name']}! 👋")
    else:
        st.markdown("### Welcome to Your Mental Health Dashboard 👋")
    
    st.markdown("---")
    
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        mood_count = len(st.session_state.mood_history)
        st.metric("📊 Mood Entries", mood_count, 
                 delta=f"+{min(mood_count, 7)} this week" if mood_count > 0 else None)
    
    with col2:
        journal_count = len(st.session_state.journal_entries)
        st.metric("📝 Journal Entries", journal_count,
                 delta=f"+{min(journal_count, 7)} this week" if journal_count > 0 else None)
    
    with col3:
        screening_count = len(st.session_state.screening_results)
        st.metric("🔍 Screenings Done", screening_count)
    
    with col4:
        avg_mood = np.mean([m['mood'] for m in st.session_state.mood_history]) if st.session_state.mood_history else 0
        mood_trend = "📈" if avg_mood >= 7 else "📉" if avg_mood < 5 else "➡️"
        st.metric("😊 Avg Mood", f"{avg_mood:.1f}/10", delta=mood_trend)
    
    st.markdown("---")
    
    # Main content area
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Mood Trend Chart
        st.markdown("### 📈 Your Mood Journey")
        
        if st.session_state.mood_history:
            recent_moods = st.session_state.mood_history[-30:]  # Last 30 entries
            df_moods = pd.DataFrame(recent_moods)
            
            fig = px.line(df_moods, x='date', y='mood', 
                         title='Mood Trend (Last 30 Entries)',
                         labels={'mood': 'Mood Score', 'date': 'Date'})
            fig.update_traces(line_color='#26a69a', line_width=3)
            fig.add_hline(y=7, line_dash="dash", line_color="#a5d6a7", 
                         annotation_text="Good Mood", annotation_position="right")
            fig.add_hline(y=5, line_dash="dash", line_color="#ffccbc", 
                         annotation_text="Neutral", annotation_position="right")
            fig.add_hline(y=3, line_dash="dash", line_color="#ef9a9a", 
                         annotation_text="Low Mood", annotation_position="right")
            fig.update_layout(
                template='plotly_white',
                plot_bgcolor='rgba(255, 255, 255, 0.9)',
                paper_bgcolor='rgba(255, 255, 255, 0.9)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Mood Statistics
            st.markdown("#### 📊 Mood Statistics")
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            with stat_col1:
                highest_mood = max([m['mood'] for m in st.session_state.mood_history])
                st.info(f"**Highest**\n\n{highest_mood}/10 🌟")
            
            with stat_col2:
                lowest_mood = min([m['mood'] for m in st.session_state.mood_history])
                st.info(f"**Lowest**\n\n{lowest_mood}/10 😔")
            
            with stat_col3:
                good_days = len([m for m in st.session_state.mood_history if m['mood'] >= 7])
                st.info(f"**Good Days**\n\n{good_days} days 😊")
            
            with stat_col4:
                recent_avg = np.mean([m['mood'] for m in st.session_state.mood_history[-7:]])
                st.info(f"**7-Day Avg**\n\n{recent_avg:.1f}/10")
        else:
            st.info("📊 Start tracking your mood to see your journey here!")
            if st.button("🎯 Track Your First Mood", use_container_width=True):
                st.session_state.nav_to = "📊 Daily Mood Tracker"
                st.rerun()
        
        # Emotional Insights
        if st.session_state.mood_history:
            st.markdown("---")
            st.markdown("### 🎭 Emotional Insights")
            
            insight_col1, insight_col2 = st.columns(2)
            
            with insight_col1:
                # Most common emotions
                all_emotions = []
                for entry in st.session_state.mood_history:
                    all_emotions.extend(entry['emotions'])
                
                if all_emotions:
                    emotion_counts = pd.Series(all_emotions).value_counts().head(5)
                    fig_emotions = px.bar(
                        x=emotion_counts.values, 
                        y=emotion_counts.index,
                        orientation='h',
                        title='Top 5 Emotions',
                        labels={'x': 'Frequency', 'y': 'Emotion'},
                        color=emotion_counts.values,
                        color_continuous_scale='Teal'
                    )
                    fig_emotions.update_layout(
                        template='plotly_white',
                        plot_bgcolor='rgba(255, 255, 255, 0.9)',
                        paper_bgcolor='rgba(255, 255, 255, 0.9)',
                        height=300,
                        showlegend=False
                    )
                    st.plotly_chart(fig_emotions, use_container_width=True)
            
            with insight_col2:
                # Most common activities
                all_activities = []
                for entry in st.session_state.mood_history:
                    all_activities.extend(entry['activities'])
                
                if all_activities:
                    activity_counts = pd.Series(all_activities).value_counts().head(5)
                    fig_activities = px.bar(
                        x=activity_counts.values,
                        y=activity_counts.index,
                        orientation='h',
                        title='Top 5 Activities',
                        labels={'x': 'Frequency', 'y': 'Activity'},
                        color=activity_counts.values,
                        color_continuous_scale='Mint'
                    )
                    fig_activities.update_layout(
                        template='plotly_white',
                        plot_bgcolor='rgba(255, 255, 255, 0.9)',
                        paper_bgcolor='rgba(255, 255, 255, 0.9)',
                        height=300,
                        showlegend=False
                    )
                    st.plotly_chart(fig_activities, use_container_width=True)
    
    with col_right:
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("  Track Mood Now", use_container_width=True):
            st.session_state.nav_to = "📊 Daily Mood Tracker"
            st.rerun()
        
        if st.button("  Write Journal Entry", use_container_width=True):
            st.session_state.nav_to = "  Journal"
            st.rerun()
        
        if st.button("🔍 Take Screening", use_container_width=True):
            st.session_state.nav_to = "🔍 Screening Modules"
            st.rerun()
        
        st.markdown("---")
        
        # Goals Progress
        st.markdown("### 🎯 Your Goals")
        if st.session_state.user_profile.get('goals'):
            for goal in st.session_state.user_profile['goals']:
                st.success(f"✓ {goal}")
        else:
            st.info("Set your goals in the Profile page")
            if st.button("⚙️ Set Goals Now", use_container_width=True):
                st.session_state.nav_to = "👤 Profile"
                st.rerun()
        
        st.markdown("---")
        
        # Recent Screening Results
        st.markdown("### 📋 Recent Screenings")
        if st.session_state.screening_results:
            recent_screenings = list(st.session_state.screening_results.values())[-3:]
            for screening in reversed(recent_screenings):
                severity_color = {
                    "Minimal": "🟢",
                    "Mild": "🟡",
                    "Moderate": "🟠",
                    "Moderately Severe": "🔴",
                    "Severe": "🔴",
                    "Low": "🟢",
                    "High": "🔴",
                    "Excellent": "🟢",
                    "Good": "🟡",
                    "Fair": "🟠",
                    "Concerning": "🔴"
                }
                
                # Handle comprehensive vs individual screening results
                if screening['type'] == 'Comprehensive':
                    # Comprehensive screening has multiple scores
                    color = severity_color.get(screening['overall_status'].split()[0], "⚪")
                    st.info(f"{color} **{screening['type']} Assessment**\n\n"
                           f"Depression: {screening['phq9_severity']} ({screening['phq9_score']}/27)\n\n"
                           f"Anxiety: {screening['gad7_severity']} ({screening['gad7_score']}/21)\n\n"
                           f"Stress: {screening['stress_severity']} ({screening['stress_score']}/40)\n\n"
                           f"Overall: {screening['overall_status']} ({screening['overall_index']}/100)\n\n"
                           f"{screening['date']}")
                else:
                    # Individual screening has single severity
                    color = severity_color.get(screening['severity'].split()[0], "⚪")
                    st.info(f"{color} **{screening['type']}**\n\n{screening['severity']}\n\n{screening['date']}")
        else:
            st.info("No screenings yet. Take your first assessment!")
        
        st.markdown("---")
        
        # Wellness Tips
        st.markdown("### 💡 Daily Wellness Tip")
        tips = [
            "Take 5 deep breaths when feeling stressed",
            "Practice gratitude - write 3 things you're thankful for",
            "Get 7-9 hours of sleep tonight",
            "Take a 10-minute walk outside",
            "Connect with a friend or loved one",
            "Drink plenty of water today",
            "Practice mindfulness for 5 minutes",
            "Limit screen time before bed",
            "Do something you enjoy today",
            "Be kind to yourself - you're doing great!"
        ]
        import random
        daily_tip = random.choice(tips)
        st.success(f"💚 {daily_tip}")
        
        st.markdown("---")
        
        # Crisis Resources
        st.markdown("### 🆘 Need Help?")
        st.error("**Crisis Support:**\n\n🇮🇳 India: 1860-2662-345 (24/7)\n🌍 International: 988 (US) | 116 123 (UK)\n🚨 Emergency: 112")
        if st.button("📞 View All Resources", use_container_width=True):
            st.session_state.nav_to = "📞 Resources"
            st.rerun()
    
    # Bottom Section - Journal Preview
    if st.session_state.journal_entries:
        st.markdown("---")
        st.markdown("### 📖 Recent Journal Entries")
        
        recent_journals = list(reversed(st.session_state.journal_entries[-3:]))
        journal_cols = st.columns(3)
        
        for idx, (col, entry) in enumerate(zip(journal_cols, recent_journals)):
            with col:
                with st.expander(f"📄 {entry['title'][:30]}..."):
                    st.write(f"**Date:** {entry['date']}")
                    st.write(f"**Mood After:** {entry['mood_after']}")
                    st.write(f"**Preview:** {entry['content'][:100]}...")
                    if st.button("📖 Read Full Entry", key=f"journal_btn_{idx}", use_container_width=True):
                        st.session_state.nav_to = "📝 Journal"
                        st.rerun()

    next_page_button("🏠 Dashboard")

# Page: Profile
elif page == "👤 Profile":
    st.title("👤 Your Profile")
    
    st.markdown("""
    <div class="profile-card">
        <h3 style="color: #26a69a;">Personal Information</h3>
        <p style="color: #546e7a;">Help us personalize your experience and provide age-appropriate recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Name (optional)", value=st.session_state.user_profile.get('name', ''))
        age = st.number_input("Age", min_value=13, max_value=100, 
                             value=st.session_state.user_age if st.session_state.user_age else 25)
        gender = st.selectbox("Gender (optional)", 
                             ["Prefer not to say", "Male", "Female", "Non-binary", "Other"],
                             index=0 if not st.session_state.user_profile.get('gender') else 
                             ["Prefer not to say", "Male", "Female", "Non-binary", "Other"].index(st.session_state.user_profile.get('gender')))
    
    with col2:
        location = st.text_input("Location (optional)", value=st.session_state.user_profile.get('location', ''))
        occupation = st.text_input("Occupation (optional)", value=st.session_state.user_profile.get('occupation', ''))
        emergency_contact = st.text_input("Emergency Contact (optional)", 
                                         value=st.session_state.user_profile.get('emergency_contact', ''),
                                         help="Phone number of someone to contact in case of emergency")
    
    st.markdown("### 🎯 Mental Health Goals")
    goals = st.multiselect(
        "What are your mental health goals?",
        ["Reduce anxiety", "Improve mood", "Better sleep", "Stress management", 
         "Build resilience", "Improve relationships", "Increase self-awareness", "Manage depression"],
        default=st.session_state.user_profile.get('goals', [])
    )
    
    st.markdown("### 📝 Additional Information")
    current_treatment = st.checkbox("Currently in therapy or treatment", 
                                   value=st.session_state.user_profile.get('current_treatment', False))
    medication = st.checkbox("Currently taking medication for mental health", 
                            value=st.session_state.user_profile.get('medication', False))
    
    notes = st.text_area("Personal notes (private)", 
                        value=st.session_state.user_profile.get('notes', ''),
                        help="Any additional information you'd like to remember")
    
    if st.button("💾 Save Profile", use_container_width=True):
        st.session_state.user_age = age
        st.session_state.user_profile = {
            'name': name,
            'age': age,
            'gender': gender,
            'location': location,
            'occupation': occupation,
            'emergency_contact': emergency_contact,
            'goals': goals,
            'current_treatment': current_treatment,
            'medication': medication,
            'notes': notes,
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_all_data()  # Auto-save
        st.success("✅ Profile saved successfully!")
        st.balloons()
    
    # Display profile summary
    if st.session_state.user_profile:
        st.markdown("---")
        st.markdown("### 📋 Profile Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Age:** {st.session_state.user_age}")
            if st.session_state.user_profile.get('gender') != "Prefer not to say":
                st.info(f"**Gender:** {st.session_state.user_profile.get('gender', 'Not set')}")
        
        with col2:
            if st.session_state.user_profile.get('occupation'):
                st.info(f"**Occupation:** {st.session_state.user_profile['occupation']}")
            if st.session_state.user_profile.get('location'):
                st.info(f"**Location:** {st.session_state.user_profile['location']}")
        
        with col3:
            if st.session_state.user_profile.get('goals'):
                st.info(f"**Goals:** {len(st.session_state.user_profile['goals'])} set")
            if st.session_state.user_profile.get('last_updated'):
                st.info(f"**Updated:** {st.session_state.user_profile['last_updated']}")

    next_page_button("👤 Profile")

# Page: Daily Mood Tracker
elif page == "📊 Daily Mood Tracker":
    st.title("📊 Daily Mood Tracker")
    
    st.info("Track your daily mood to identify patterns and triggers")
    
    # Add tabs for different input methods
    input_tab1, input_tab2 = st.tabs(["✍️ Manual Entry", "🎤 Voice Entry"])
    
    with input_tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            mood_score = st.slider(
                "Rate your mood (1-10)",
                min_value=1, max_value=10, value=5,
                help="1 = Very Low, 10 = Excellent"
            )
            
            mood_emoji = ["😢", "😟", "😐", "🙂", "😊", "😄", "🤗", "😁", "🌟", "✨"][mood_score-1]
            st.markdown(f"<h1 style='text-align: center;'>{mood_emoji}</h1>", unsafe_allow_html=True)
            
            emotions = st.multiselect(
                "What emotions are you experiencing?",
                ["Happy", "Sad", "Anxious", "Calm", "Angry", "Excited", "Tired", "Energetic", "Stressed", "Peaceful"]
            )
            
            activities = st.multiselect(
                "What activities did you do today?",
                ["Exercise", "Work", "Socializing", "Hobbies", "Rest", "Study", "Family Time", "Meditation", "Entertainment"]
            )
            
            notes = st.text_area("How are you feeling? (Your words will be analyzed)", 
                                placeholder="Describe your day, feelings, or anything on your mind...")
            
            # Text Sentiment Analysis
            if notes and SENTIMENT_AVAILABLE:
                sentiment_result = analyze_sentiment(notes)
                
                st.markdown("###   Text Analysis")
                col_sent1, col_sent2, col_sent3 = st.columns(3)
                
                with col_sent1:
                    emoji = get_sentiment_emoji(sentiment_result['sentiment'])
                    st.metric("Sentiment", f"{emoji} {sentiment_result['sentiment']}")
                
                with col_sent2:
                    polarity_pct = (sentiment_result['polarity'] + 1) * 50
                    st.metric("Positivity", f"{polarity_pct:.0f}%")
                
                with col_sent3:
                    suggested_mood = int(sentiment_result['score'])
                    st.metric("Suggested Mood", f"{suggested_mood}/10")
                
                if abs(mood_score - suggested_mood) > 2:
                    st.info(f"💡 Your text suggests a mood of {suggested_mood}/10, but you rated {mood_score}/10. Consider if this reflects how you truly feel.")
            
            if st.button("💾 Save Mood Entry", use_container_width=True):
                entry = {
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'mood': mood_score,
                    'emotions': emotions,
                    'activities': activities,
                    'notes': notes,
                    'sentiment': analyze_sentiment(notes) if notes and SENTIMENT_AVAILABLE else None,
                    'entry_type': 'manual'
                }
                st.session_state.mood_history.append(entry)
                save_all_data()  # Auto-save
                st.success("✅ Mood entry saved with sentiment analysis!")
                st.balloons()
        
        with col2:
            st.markdown("### 📅 Recent Entries")
            if st.session_state.mood_history:
                for entry in reversed(st.session_state.mood_history[-5:]):
                    with st.expander(f"{entry['date']} - Mood: {entry['mood']}/10"):
                        st.write(f"**Emotions:** {', '.join(entry['emotions'][:3])}")
                        if entry.get('sentiment'):
                            sent_emoji = get_sentiment_emoji(entry['sentiment']['sentiment'])
                            st.write(f"**Sentiment:** {sent_emoji} {entry['sentiment']['sentiment']}")
                        if entry['notes']:
                            st.write(f"**Notes:** {entry['notes'][:100]}...")
            else:
                st.info("No entries yet")
    
    with input_tab2:
        st.markdown("### 🎤 Voice Mood Entry")
        st.info("🎙️ Record your voice or type your thoughts - AI will analyze your emotions")
        
        # Initialize session state for voice transcription
        if 'voice_transcription' not in st.session_state:
            st.session_state.voice_transcription = ''
        
        # Create recording section
        st.markdown("####  ️ Record Your Voice")
        
        if AUDIO_RECORDER_AVAILABLE:
            st.markdown("**Click the microphone button below to start/stop recording:**")
            
            audio_bytes = audio_recorder(
                text="Click to record",
                recording_color="#26a69a",
                neutral_color="#80cbc4",
                icon_name="microphone",
                icon_size="3x"
            )
            
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                st.success("✅ Audio recorded!")
                
                # Try to transcribe
                if SPEECH_RECOGNITION_AVAILABLE:
                    try:
                        # Save audio temporarily
                        with open("temp_audio.wav", "wb") as f:
                            f.write(audio_bytes)
                        
                        # Transcribe
                        recognizer = sr.Recognizer()
                        with sr.AudioFile("temp_audio.wav") as source:
                            audio_data = recognizer.record(source)
                            transcribed_text = recognizer.recognize_google(audio_data)
                            st.session_state.voice_transcription = transcribed_text
                            st.success(f"📝 Transcribed: {transcribed_text}")
                    except sr.UnknownValueError:
                        st.warning("⚠️ Could not understand audio. Please try again or use text input.")
                    except sr.RequestError:
                        st.error("⚠️ Could not connect to speech recognition service. Please use text input.")
                    except Exception as e:
                        st.warning(f"⚠️ Transcription error. Please use text input below.")
                else:
                    st.warning("⚠️ Install SpeechRecognition for transcription: pip install SpeechRecognition")
        else:
            st.warning("⚠️ Install audio recorder to enable voice recording:")
            st.code("pip install streamlit-audio-recorder", language="bash")
            st.info("💡 For now, use the text input below - it works just as well!")
        
        st.markdown("---")
        st.markdown("#### ✍️ Or Type Your Thoughts")
        
        voice_text = st.text_area("Type or edit transcribed text:", 
                                  placeholder="I feel really good today. Work went well and I exercised...",
                                  height=150,
                                  key="voice_input",
                                  value=st.session_state.voice_transcription)
        
        if voice_text:
            # Analyze the voice/text input
            if SENTIMENT_AVAILABLE:
                voice_sentiment = analyze_sentiment(voice_text)
                suggested_mood_voice = int(voice_sentiment['score'])
                
                st.markdown("### 🔍 Voice Analysis Results")
                
                col_v1, col_v2, col_v3, col_v4 = st.columns(4)
                
                with col_v1:
                    emoji = get_sentiment_emoji(voice_sentiment['sentiment'])
                    st.metric("Detected Sentiment", f"{emoji} {voice_sentiment['sentiment']}")
                
                with col_v2:
                    st.metric("Suggested Mood", f"{suggested_mood_voice}/10")
                
                with col_v3:
                    positivity = (voice_sentiment['polarity'] + 1) * 50
                    st.metric("Positivity", f"{positivity:.0f}%")
                
                with col_v4:
                    word_count = len(voice_text.split())
                    st.metric("Words Spoken", word_count)
                
                # Auto-suggest emotions based on text
                st.markdown("### 🎭 Detected Emotions")
                detected_emotions = []
                text_lower = voice_text.lower()
                
                emotion_keywords = {
                    'Happy': ['happy', 'joy', 'great', 'wonderful', 'excellent', 'good', 'pleased'],
                    'Sad': ['sad', 'down', 'depressed', 'unhappy', 'miserable'],
                    'Anxious': ['anxious', 'worried', 'nervous', 'stressed', 'tense'],
                    'Calm': ['calm', 'peaceful', 'relaxed', 'serene', 'tranquil'],
                    'Angry': ['angry', 'mad', 'furious', 'irritated', 'annoyed'],
                    'Excited': ['excited', 'thrilled', 'enthusiastic', 'eager'],
                    'Tired': ['tired', 'exhausted', 'fatigued', 'sleepy', 'weary'],
                    'Energetic': ['energetic', 'energized', 'active', 'lively']
                }
                
                for emotion, keywords in emotion_keywords.items():
                    if any(keyword in text_lower for keyword in keywords):
                        detected_emotions.append(emotion)
                
                if detected_emotions:
                    st.success(f"Detected: {', '.join(detected_emotions)}")
                else:
                    st.info("No specific emotions detected. You can select manually below.")
                
                # Allow user to confirm or modify
                st.markdown("### ✏️ Confirm Your Entry")
                
                final_mood = st.slider("Confirm your mood", 1, 10, suggested_mood_voice, key="voice_mood")
                final_emotions = st.multiselect("Confirm emotions", 
                                               ["Happy", "Sad", "Anxious", "Calm", "Angry", "Excited", "Tired", "Energetic", "Stressed", "Peaceful"],
                                               default=detected_emotions[:3])
                final_activities = st.multiselect("What did you do?",
                                                 ["Exercise", "Work", "Socializing", "Hobbies", "Rest", "Study", "Family Time", "Meditation", "Entertainment"])
                
                if st.button("💾 Save Voice Entry", use_container_width=True):
                    entry = {
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'mood': final_mood,
                        'emotions': final_emotions,
                        'activities': final_activities,
                        'notes': voice_text,
                        'sentiment': voice_sentiment,
                        'entry_type': 'voice'
                    }
                    st.session_state.mood_history.append(entry)
                    save_all_data()  # Auto-save
                    st.success("✅ Voice entry saved with AI analysis!")
                    st.balloons()
            else:
                st.warning("Install textblob for sentiment analysis: pip install textblob")

    next_page_button("📊 Daily Mood Tracker")

# Page: Journal
elif page == "📝 Journal":
    st.title("📝 Reflection Journal")
    
    st.info("Express your thoughts and feelings. AI will analyze your emotional state from your writing")
    
    tab1, tab2 = st.tabs(["✍️ New Entry", "📖 Past Entries"])
    
    with tab1:
        journal_title = st.text_input("Entry Title (optional)")
        journal_content = st.text_area("Write your thoughts...", 
                                       height=300,
                                       placeholder="Today I felt... I'm grateful for... I'm worried about...")
        
        # Real-time sentiment analysis as user types
        if journal_content and SENTIMENT_AVAILABLE:
            sentiment_analysis = analyze_sentiment(journal_content)
            
            st.markdown("### 🔍 Live Text Analysis")
            
            col_analysis1, col_analysis2, col_analysis3, col_analysis4 = st.columns(4)
            
            with col_analysis1:
                emoji = get_sentiment_emoji(sentiment_analysis['sentiment'])
                st.metric("Overall Tone", f"{emoji} {sentiment_analysis['sentiment']}")
            
            with col_analysis2:
                polarity_pct = (sentiment_analysis['polarity'] + 1) * 50
                color = "🟢" if polarity_pct > 60 else "🟡" if polarity_pct > 40 else "🔴"
                st.metric("Positivity", f"{color} {polarity_pct:.0f}%")
            
            with col_analysis3:
                subjectivity_pct = sentiment_analysis['subjectivity'] * 100
                st.metric("Emotional Depth", f"{subjectivity_pct:.0f}%")
            
            with col_analysis4:
                word_count = len(journal_content.split())
                st.metric("Word Count", word_count)
            
            # Provide writing insights
            if sentiment_analysis['polarity'] < -0.5:
                st.warning("💙 Your writing shows you're going through a difficult time. Consider reaching out to someone you trust.")
            elif sentiment_analysis['polarity'] > 0.5:
                st.success("😊 Your writing reflects positive emotions. That's wonderful!")
            
            if word_count < 50:
                st.info("💡 Tip: Writing more (100+ words) can help process emotions better")
        
        col1, col2 = st.columns(2)
        with col1:
            journal_mood = st.select_slider(
                "How do you feel after writing?",
                options=["Much Worse", "Worse", "Same", "Better", "Much Better"]
            )
        with col2:
            journal_tags = st.multiselect(
                "Tags",
                ["Gratitude", "Anxiety", "Goals", "Relationships", "Work", "Health", "Personal Growth"]
            )
        
        if st.button("💾 Save Journal Entry", use_container_width=True):
            if journal_content:
                entry = {
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'title': journal_title or "Untitled",
                    'content': journal_content,
                    'mood_after': journal_mood,
                    'tags': journal_tags,
                    'sentiment': analyze_sentiment(journal_content) if SENTIMENT_AVAILABLE else None,
                    'word_count': len(journal_content.split())
                }
                st.session_state.journal_entries.append(entry)
                save_all_data()  # Auto-save
                st.success("✅ Journal entry saved with sentiment analysis!")
                st.balloons()
            else:
                st.warning("Please write something before saving")
    
    with tab2:
        if st.session_state.journal_entries:
            # Show sentiment summary
            if SENTIMENT_AVAILABLE:
                st.markdown("### 📊 Journal Sentiment Overview")
                
                sentiments = [e.get('sentiment', {}) for e in st.session_state.journal_entries if e.get('sentiment')]
                if sentiments:
                    positive_count = sum(1 for s in sentiments if s.get('sentiment') == 'Positive')
                    neutral_count = sum(1 for s in sentiments if s.get('sentiment') == 'Neutral')
                    negative_count = sum(1 for s in sentiments if s.get('sentiment') == 'Negative')
                    total = len(sentiments)
                    
                    col_sum1, col_sum2, col_sum3 = st.columns(3)
                    
                    with col_sum1:
                        st.metric("😊 Positive Entries", f"{positive_count} ({positive_count/total*100:.0f}%)")
                    with col_sum2:
                        st.metric("😐 Neutral Entries", f"{neutral_count} ({neutral_count/total*100:.0f}%)")
                    with col_sum3:
                        st.metric("😔 Negative Entries", f"{negative_count} ({negative_count/total*100:.0f}%)")
            
            st.markdown("---")
            st.markdown("### 📖 All Entries")
            
            for idx, entry in enumerate(reversed(st.session_state.journal_entries)):
                # Add sentiment badge to title
                title_display = entry['title']
                if entry.get('sentiment'):
                    emoji = get_sentiment_emoji(entry['sentiment']['sentiment'])
                    title_display = f"{emoji} {entry['title']}"
                
                with st.expander(f"📄 {title_display} - {entry['date']}"):
                    st.write(entry['content'])
                    st.markdown(f"**Mood After:** {entry['mood_after']}")
                    st.markdown(f"**Tags:** {', '.join(entry['tags'])}")
                    
                    if entry.get('sentiment'):
                        st.markdown("---")
                        st.markdown("**Sentiment Analysis:**")
                        col_e1, col_e2, col_e3 = st.columns(3)
                        with col_e1:
                            st.write(f"Tone: {entry['sentiment']['sentiment']}")
                        with col_e2:
                            polarity_pct = (entry['sentiment']['polarity'] + 1) * 50
                            st.write(f"Positivity: {polarity_pct:.0f}%")
                        with col_e3:
                            st.write(f"Words: {entry.get('word_count', 0)}")
        else:
            st.info("No journal entries yet. Start writing!")

    next_page_button("📝 Journal")

# Page: Screening Modules
elif page == "🔍 Screening Modules":
    st.title("🔍 Comprehensive Mental Health Screening")
    
    # Initialize session state for comprehensive screening
    if 'comprehensive_screening' not in st.session_state:
        st.session_state.comprehensive_screening = {
            'phq9_responses': None,
            'gad7_responses': None,
            'stress_responses': None,
            'current_step': 1
        }
    
    screening_mode = st.radio(
        "Choose Screening Mode",
        ["📊 Comprehensive Assessment (All 3 Tests)", "🎯 Individual Test"],
        horizontal=True
    )
    
    if screening_mode == "📊 Comprehensive Assessment (All 3 Tests)":
        st.markdown("---")
        st.markdown("### Complete all three assessments for a comprehensive mental health profile")
        
        # Progress indicator
        progress = (st.session_state.comprehensive_screening['current_step'] - 1) / 3
        st.progress(progress)
        st.caption(f"Step {st.session_state.comprehensive_screening['current_step']} of 3")
        
        # Step 1: PHQ-9 Depression Screening
        if st.session_state.comprehensive_screening['current_step'] == 1:
            st.markdown("### 📋 Step 1: Depression Assessment (PHQ-9)")
            st.info("Over the last 2 weeks, how often have you been bothered by any of the following problems?")
            
            responses = []
            for i, question in enumerate(PHQ9_QUESTIONS):
                response = st.radio(
                    f"{i+1}. {question}",
                    ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"],
                    key=f"comp_phq9_{i}"
                )
                responses.append(int(response.split("(")[1].split(")")[0]))
            
            if st.button("Continue to Anxiety Assessment →", type="primary"):
                st.session_state.comprehensive_screening['phq9_responses'] = responses
                st.session_state.comprehensive_screening['current_step'] = 2
                st.rerun()
        
        # Step 2: GAD-7 Anxiety Screening
        elif st.session_state.comprehensive_screening['current_step'] == 2:
            st.markdown("### 😰 Step 2: Anxiety Assessment (GAD-7)")
            st.info("Over the last 2 weeks, how often have you been bothered by the following problems?")
            
            responses = []
            for i, question in enumerate(GAD7_QUESTIONS):
                response = st.radio(
                    f"{i+1}. {question}",
                    ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"],
                    key=f"comp_gad7_{i}"
                )
                responses.append(int(response.split("(")[1].split(")")[0]))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back to Depression"):
                    st.session_state.comprehensive_screening['current_step'] = 1
                    st.rerun()
            with col2:
                if st.button("Continue to Stress Assessment →", type="primary"):
                    st.session_state.comprehensive_screening['gad7_responses'] = responses
                    st.session_state.comprehensive_screening['current_step'] = 3
                    st.rerun()
        
        # Step 3: Perceived Stress Scale
        elif st.session_state.comprehensive_screening['current_step'] == 3:
            st.markdown("### 😓 Step 3: Stress Assessment (Perceived Stress Scale)")
            st.info("In the last month, how often have you experienced the following?")
            
            responses = []
            for i, question in enumerate(STRESS_QUESTIONS):
                response = st.radio(
                    f"{i+1}. {question}",
                    ["Never (0)", "Almost Never (1)", "Sometimes (2)", "Fairly Often (3)", "Very Often (4)"],
                    key=f"comp_stress_{i}"
                )
                responses.append(int(response.split("(")[1].split(")")[0]))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back to Anxiety"):
                    st.session_state.comprehensive_screening['current_step'] = 2
                    st.rerun()
            with col2:
                if st.button("📊 View Comprehensive Report →", type="primary"):
                    st.session_state.comprehensive_screening['stress_responses'] = responses
                    
                    # Calculate all scores
                    phq9_score = sum(st.session_state.comprehensive_screening['phq9_responses'])
                    gad7_score = sum(st.session_state.comprehensive_screening['gad7_responses'])
                    
                    # Reverse scoring for stress positive items
                    stress_resp = responses.copy()
                    stress_resp[3] = 4 - stress_resp[3]
                    stress_resp[4] = 4 - stress_resp[4]
                    stress_resp[6] = 4 - stress_resp[6]
                    stress_resp[7] = 4 - stress_resp[7]
                    stress_score = sum(stress_resp)
                    
                    # Determine severities
                    if phq9_score <= 4:
                        phq9_severity = "Minimal"
                        phq9_color = "🟢"
                    elif phq9_score <= 9:
                        phq9_severity = "Mild"
                        phq9_color = "🟡"
                    elif phq9_score <= 14:
                        phq9_severity = "Moderate"
                        phq9_color = "🟠"
                    elif phq9_score <= 19:
                        phq9_severity = "Moderately Severe"
                        phq9_color = "🔴"
                    else:
                        phq9_severity = "Severe"
                        phq9_color = "🔴"
                    
                    if gad7_score <= 4:
                        gad7_severity = "Minimal"
                        gad7_color = "🟢"
                    elif gad7_score <= 9:
                        gad7_severity = "Mild"
                        gad7_color = "🟡"
                    elif gad7_score <= 14:
                        gad7_severity = "Moderate"
                        gad7_color = "🟠"
                    else:
                        gad7_severity = "Severe"
                        gad7_color = "🔴"
                    
                    if stress_score <= 13:
                        stress_severity = "Low"
                        stress_color = "🟢"
                    elif stress_score <= 26:
                        stress_severity = "Moderate"
                        stress_color = "🟠"
                    else:
                        stress_severity = "High"
                        stress_color = "🔴"
                    
                    # Calculate overall index
                    overall_index = ((phq9_score/27) + (gad7_score/21) + (stress_score/40)) / 3 * 100
                    
                    if overall_index < 20:
                        overall_status = "Excellent"
                        overall_color = "🟢"
                    elif overall_index < 40:
                        overall_status = "Good"
                        overall_color = "🟡"
                    elif overall_index < 60:
                        overall_status = "Fair - Attention Needed"
                        overall_color = "🟠"
                    else:
                        overall_status = "Concerning - Seek Support"
                        overall_color = "🔴"
                    
                    # Save comprehensive results to session state
                    st.session_state.comprehensive_screening['calculated_results'] = {
                        'phq9_score': phq9_score,
                        'phq9_severity': phq9_severity,
                        'phq9_color': phq9_color,
                        'gad7_score': gad7_score,
                        'gad7_severity': gad7_severity,
                        'gad7_color': gad7_color,
                        'stress_score': stress_score,
                        'stress_severity': stress_severity,
                        'stress_color': stress_color,
                        'overall_index': overall_index,
                        'overall_status': overall_status,
                        'overall_color': overall_color,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    
                    # Save to screening results history
                    st.session_state.screening_results[f"Comprehensive_{datetime.now().strftime('%Y-%m-%d_%H%M')}"] = {
                        'type': 'Comprehensive',
                        'phq9_score': phq9_score,
                        'phq9_severity': phq9_severity,
                        'gad7_score': gad7_score,
                        'gad7_severity': gad7_severity,
                        'stress_score': stress_score,
                        'stress_severity': stress_severity,
                        'overall_index': round(overall_index, 1),
                        'overall_status': overall_status,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    save_all_data()  # Auto-save
                    
                    # Navigate to report page
                    st.session_state.nav_to = "📋 Comprehensive Report"
                    st.rerun()
    
    else:  # Individual Test Mode
        st.markdown("---")
        screening_type = st.selectbox(
            "Select Screening Tool",
            ["PHQ-9 (Depression)", "GAD-7 (Anxiety)", "Perceived Stress Scale"]
        )
        
        if screening_type == "PHQ-9 (Depression)":
            st.info("Over the last 2 weeks, how often have you been bothered by any of the following problems?")
            
            responses = []
            for i, question in enumerate(PHQ9_QUESTIONS):
                response = st.radio(
                    f"{i+1}. {question}",
                    ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"],
                    key=f"ind_phq9_{i}"
                )
                responses.append(int(response.split("(")[1].split(")")[0]))
            
            if st.button("Calculate PHQ-9 Score"):
                total_score = sum(responses)
                
                if total_score <= 4:
                    severity = "Minimal Depression"
                    color = "🟢"
                    recommendation = "Your symptoms suggest minimal or no depression. Continue healthy habits!"
                elif total_score <= 9:
                    severity = "Mild Depression"
                    color = "🟡"
                    recommendation = "Mild depression detected. Consider lifestyle changes and monitoring symptoms."
                elif total_score <= 14:
                    severity = "Moderate Depression"
                    color = "🟠"
                    recommendation = "Moderate depression detected. Consider speaking with a mental health professional."
                elif total_score <= 19:
                    severity = "Moderately Severe Depression"
                    color = "🔴"
                    recommendation = "Moderately severe depression detected. Professional help is recommended."
                else:
                    severity = "Severe Depression"
                    color = "🔴"
                    recommendation = "Severe depression detected. Please seek professional help immediately."
                
                st.success(f"{color} **PHQ-9 Score: {total_score}/27**")
                st.info(f"**Severity: {severity}**")
                st.warning(f"**Recommendation:** {recommendation}")
                
                if responses[8] > 0:
                    st.error("⚠️ **Important:** You indicated thoughts of self-harm. Please call immediately:\n\n🇮🇳 India: 1860-2662-345 | 91-9820466726\n🌍 International: 988 (US) | 116 123 (UK)\n🚨 Or go to your nearest emergency room.")
                
                st.session_state.screening_results[f"PHQ-9_{datetime.now().strftime('%Y-%m-%d')}"] = {
                    'type': 'PHQ-9',
                    'score': total_score,
                    'severity': severity,
                    'date': datetime.now().strftime("%Y-%m-%d")
                }
                save_all_data()  # Auto-save
                
                if st.session_state.user_age:
                    if st.session_state.user_age < 18:
                        st.info("💡 For teens: Talk to a parent, school counselor, or trusted adult about how you're feeling")
                    elif st.session_state.user_age < 30:
                        st.info("💡 For young adults: Campus counseling services or online therapy platforms can be helpful")
                    elif st.session_state.user_age < 65:
                        st.info("💡 For adults: Consider professional therapy, support groups, and lifestyle modifications")
                    else:
                        st.info("💡 For seniors: Senior-specific mental health services and community support groups are available")
        
        elif screening_type == "GAD-7 (Anxiety)":
            st.info("Over the last 2 weeks, how often have you been bothered by the following problems?")
            
            responses = []
            for i, question in enumerate(GAD7_QUESTIONS):
                response = st.radio(
                    f"{i+1}. {question}",
                    ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"],
                    key=f"ind_gad7_{i}"
                )
                responses.append(int(response.split("(")[1].split(")")[0]))
            
            if st.button("Calculate GAD-7 Score"):
                total_score = sum(responses)
                
                if total_score <= 4:
                    severity = "Minimal Anxiety"
                    color = "🟢"
                elif total_score <= 9:
                    severity = "Mild Anxiety"
                    color = "🟡"
                elif total_score <= 14:
                    severity = "Moderate Anxiety"
                    color = "🟠"
                else:
                    severity = "Severe Anxiety"
                    color = "🔴"
                
                st.success(f"{color} **GAD-7 Score: {total_score}/21**")
                st.info(f"**Severity: {severity}**")
                
                st.session_state.screening_results[f"GAD-7_{datetime.now().strftime('%Y-%m-%d')}"] = {
                    'type': 'GAD-7',
                    'score': total_score,
                    'severity': severity,
                    'date': datetime.now().strftime("%Y-%m-%d")
                }
                save_all_data()  # Auto-save
                
                if st.session_state.user_age:
                    if st.session_state.user_age < 18:
                        st.info("💡 For teens: Consider talking to a school counselor or trusted adult")
                    elif st.session_state.user_age < 30:
                        st.info("💡 For young adults: Campus counseling or online therapy can be helpful")
                    elif st.session_state.user_age < 65:
                        st.info("💡 For adults: Consider professional therapy and stress management techniques")
                    else:
                        st.info("💡 For seniors: Community support groups and specialized senior mental health services available")
        
        elif screening_type == "Perceived Stress Scale":
            st.info("In the last month, how often have you experienced the following?")
            
            responses = []
            for i, question in enumerate(STRESS_QUESTIONS):
                response = st.radio(
                    f"{i+1}. {question}",
                    ["Never (0)", "Almost Never (1)", "Sometimes (2)", "Fairly Often (3)", "Very Often (4)"],
                    key=f"ind_stress_{i}"
                )
                responses.append(int(response.split("(")[1].split(")")[0]))
            
            if st.button("Calculate Stress Score"):
                # Reverse scoring for positive items (4, 5, 7, 8)
                responses[3] = 4 - responses[3]
                responses[4] = 4 - responses[4]
                responses[6] = 4 - responses[6]
                responses[7] = 4 - responses[7]
                
                total_score = sum(responses)
                
                if total_score <= 13:
                    severity = "Low Stress"
                    color = "🟢"
                elif total_score <= 26:
                    severity = "Moderate Stress"
                    color = "🟠"
                else:
                    severity = "High Stress"
                    color = "🔴"
                
                st.success(f"{color} **Stress Score: {total_score}/40**")
                st.info(f"**Level: {severity}**")
                
                st.session_state.screening_results[f"Stress_{datetime.now().strftime('%Y-%m-%d')}"] = {
                    'type': 'Stress',
                    'score': total_score,
                    'severity': severity,
                    'date': datetime.now().strftime("%Y-%m-%d")
                }
                save_all_data()  # Auto-save

    next_page_button("🔍 Screening Modules")

# Page: Comprehensive Report
elif page == "📋 Comprehensive Report":
    st.title("📋 Your Comprehensive Mental Health Report")
    
    # Check if there's a report to display
    if 'calculated_results' not in st.session_state.comprehensive_screening or st.session_state.comprehensive_screening['calculated_results'] is None:
        st.warning("⚠️ No comprehensive assessment results found.")
        st.info("Please complete the Comprehensive Assessment in the Screening Modules page first.")
        if st.button("Go to Screening Modules"):
            st.session_state.nav_to = "🔍 Screening Modules"
            st.rerun()
    else:
        results = st.session_state.comprehensive_screening['calculated_results']
        phq9_score = results['phq9_score']
        phq9_severity = results['phq9_severity']
        phq9_color = results['phq9_color']
        gad7_score = results['gad7_score']
        gad7_severity = results['gad7_severity']
        gad7_color = results['gad7_color']
        stress_score = results['stress_score']
        stress_severity = results['stress_severity']
        stress_color = results['stress_color']
        overall_index = results['overall_index']
        overall_status = results['overall_status']
        overall_color = results['overall_color']
        
        st.info(f"📅 Report Generated: {results['timestamp']}")
        
        # Display comprehensive results
        st.markdown("---")
        st.markdown("## 📊 Your Comprehensive Mental Health Profile")
        
        # Score cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Depression (PHQ-9)", f"{phq9_score}/27", f"{phq9_severity}")
            st.markdown(f"{phq9_color} {phq9_severity} Depression")
        with col2:
            st.metric("Anxiety (GAD-7)", f"{gad7_score}/21", f"{gad7_severity}")
            st.markdown(f"{gad7_color} {gad7_severity} Anxiety")
        with col3:
            st.metric("Stress (PSS)", f"{stress_score}/40", f"{stress_severity}")
            st.markdown(f"{stress_color} {stress_severity} Stress")
        
        # Overall Mental Health Index
        st.markdown("---")
        st.markdown(f"### {overall_color} Overall Mental Health Index: {overall_index:.1f}/100")
        st.markdown(f"**Status:** {overall_status}")
        st.progress(overall_index/100)
        
        # Visual dashboard
        st.markdown("---")
        st.markdown("### 📈 Visual Profile")
        
        # Create comparison chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Depression', 'Anxiety', 'Stress'],
            y=[phq9_score/27*100, gad7_score/21*100, stress_score/40*100],
            marker_color=['#FF6B6B', '#4ECDC4', '#FFE66D'],
            text=[f"{phq9_score}/27", f"{gad7_score}/21", f"{stress_score}/40"],
            textposition='auto',
        ))
        fig.update_layout(
            title='Mental Health Scores (Percentage)',
            yaxis_title='Severity (%)',
            yaxis_range=[0, 100],
            template='plotly_white',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Early Risk Detection System
        st.markdown("---")
        st.markdown("### 🚨 Early Risk Detection System")
        
        risk_factors = []
        risk_level = "Low"
        risk_color_risk = "🟢"
        risk_score = 0
        
        # Check individual risk factors
        
        # 1. Suicidal ideation (CRITICAL)
        if st.session_state.comprehensive_screening['phq9_responses'][8] > 0:
            risk_factors.append({
                'severity': 'CRITICAL',
                'factor': 'Suicidal Thoughts',
                'description': 'You indicated thoughts of self-harm',
                'action': 'Call immediately - India: 1860-2662-345 | International: 988 | Emergency: 112'
            })
            risk_score += 50
        
        # 2. Severe depression symptoms
        if phq9_score >= 20:
            risk_factors.append({
                'severity': 'HIGH',
                'factor': 'Severe Depression',
                'description': f'PHQ-9 score of {phq9_score} indicates severe depression',
                'action': 'Urgent professional evaluation recommended within 24-48 hours'
            })
            risk_score += 15
        elif phq9_score >= 15:
            risk_factors.append({
                'severity': 'MODERATE',
                'factor': 'Moderately Severe Depression',
                'description': f'PHQ-9 score of {phq9_score} shows significant depression symptoms',
                'action': 'Schedule appointment with mental health professional within 1 week'
            })
            risk_score += 10
        elif phq9_score >= 10:
            risk_factors.append({
                'severity': 'LOW',
                'factor': 'Moderate Depression',
                'description': f'PHQ-9 score of {phq9_score} indicates moderate depression',
                'action': 'Consider therapy or counseling services'
            })
            risk_score += 5
        
        # 3. Severe anxiety symptoms
        if gad7_score >= 15:
            risk_factors.append({
                'severity': 'HIGH',
                'factor': 'Severe Anxiety',
                'description': f'GAD-7 score of {gad7_score} indicates severe anxiety',
                'action': 'Professional evaluation recommended within 1 week'
            })
            risk_score += 12
        elif gad7_score >= 10:
            risk_factors.append({
                'severity': 'MODERATE',
                'factor': 'Moderate Anxiety',
                'description': f'GAD-7 score of {gad7_score} shows significant anxiety',
                'action': 'Consider anxiety management strategies and professional support'
            })
            risk_score += 8
        
        # 4. High stress levels
        if stress_score >= 27:
            risk_factors.append({
                'severity': 'HIGH',
                'factor': 'High Perceived Stress',
                'description': f'Stress score of {stress_score} indicates very high stress',
                'action': 'Implement immediate stress reduction techniques'
            })
            risk_score += 10
        elif stress_score >= 20:
            risk_factors.append({
                'severity': 'MODERATE',
                'factor': 'Elevated Stress',
                'description': f'Stress score of {stress_score} shows elevated stress levels',
                'action': 'Practice stress management and self-care'
            })
            risk_score += 6
        
        # 5. Comorbidity (multiple conditions)
        if phq9_score >= 10 and gad7_score >= 10:
            risk_factors.append({
                'severity': 'MODERATE',
                'factor': 'Depression-Anxiety Comorbidity',
                'description': 'Both depression and anxiety are elevated',
                'action': 'Comprehensive treatment addressing both conditions recommended'
            })
            risk_score += 8
        
        # 6. Stress-induced mental health issues
        if stress_score >= 20 and (phq9_score >= 10 or gad7_score >= 10):
            risk_factors.append({
                'severity': 'MODERATE',
                'factor': 'Stress-Related Mental Health Impact',
                'description': 'High stress may be triggering or worsening mental health symptoms',
                'action': 'Address stress as primary intervention target'
            })
            risk_score += 7
        
        # 7. Sleep disturbances (PHQ-9 question 3)
        if st.session_state.comprehensive_screening['phq9_responses'][2] >= 2:
            risk_factors.append({
                'severity': 'LOW',
                'factor': 'Sleep Disturbances',
                'description': 'Significant sleep problems detected',
                'action': 'Improve sleep hygiene; consider sleep evaluation'
            })
            risk_score += 4
        
        # 8. Concentration problems (PHQ-9 question 7)
        if st.session_state.comprehensive_screening['phq9_responses'][6] >= 2:
            risk_factors.append({
                'severity': 'LOW',
                'factor': 'Cognitive Impairment',
                'description': 'Difficulty concentrating affecting daily function',
                'action': 'Monitor cognitive symptoms; may indicate worsening condition'
            })
            risk_score += 3
        
        # 9. Psychomotor changes (PHQ-9 question 8)
        if st.session_state.comprehensive_screening['phq9_responses'][7] >= 2:
            risk_factors.append({
                'severity': 'MODERATE',
                'factor': 'Psychomotor Changes',
                'description': 'Noticeable changes in movement or speech',
                'action': 'Medical evaluation recommended to rule out other conditions'
            })
            risk_score += 6
        
        # 10. Inability to control worry (GAD-7 question 2)
        if st.session_state.comprehensive_screening['gad7_responses'][1] >= 2:
            risk_factors.append({
                'severity': 'LOW',
                'factor': 'Uncontrollable Worry',
                'description': 'Difficulty stopping or controlling worrying',
                'action': 'Learn worry management techniques; consider CBT'
            })
            risk_score += 4
        
        # Determine overall risk level
        if risk_score >= 40:
            risk_level = "CRITICAL"
            risk_color_risk = "🔴"
        elif risk_score >= 25:
            risk_level = "HIGH"
            risk_color_risk = "🟠"
        elif risk_score >= 15:
            risk_level = "MODERATE"
            risk_color_risk = "🟡"
        else:
            risk_level = "LOW"
            risk_color_risk = "🟢"
        
        # Display risk level
        if risk_level == "CRITICAL":
            st.error(f"{risk_color_risk} **Overall Risk Level: {risk_level}** (Risk Score: {risk_score})")
            st.error("⚠️ **IMMEDIATE ACTION REQUIRED** - Please seek professional help immediately")
        elif risk_level == "HIGH":
            st.warning(f"{risk_color_risk} **Overall Risk Level: {risk_level}** (Risk Score: {risk_score})")
            st.warning("⚠️ Professional evaluation strongly recommended within 1 week")
        elif risk_level == "MODERATE":
            st.warning(f"{risk_color_risk} **Overall Risk Level: {risk_level}** (Risk Score: {risk_score})")
            st.info("💡 Consider scheduling appointment with mental health professional")
        else:
            st.success(f"{risk_color_risk} **Overall Risk Level: {risk_level}** (Risk Score: {risk_score})")
            st.success("✅ No immediate risk factors detected. Continue monitoring your mental health")
        
        # Display detected risk factors
        if risk_factors:
            st.markdown("#### 🔍 Detected Risk Factors:")
            
            # Sort by severity
            severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MODERATE': 2, 'LOW': 3}
            risk_factors.sort(key=lambda x: severity_order[x['severity']])
            
            for rf in risk_factors:
                if rf['severity'] == 'CRITICAL':
                    with st.expander(f"🔴 **{rf['severity']}** - {rf['factor']}", expanded=True):
                        st.error(f"**Issue:** {rf['description']}")
                        st.error(f"**Action:** {rf['action']}")
                elif rf['severity'] == 'HIGH':
                    with st.expander(f"🟠 **{rf['severity']}** - {rf['factor']}"):
                        st.warning(f"**Issue:** {rf['description']}")
                        st.warning(f"**Action:** {rf['action']}")
                elif rf['severity'] == 'MODERATE':
                    with st.expander(f"🟡 **{rf['severity']}** - {rf['factor']}"):
                        st.info(f"**Issue:** {rf['description']}")
                        st.info(f"**Action:** {rf['action']}")
                else:
                    with st.expander(f"🟢 **{rf['severity']}** - {rf['factor']}"):
                        st.info(f"**Issue:** {rf['description']}")
                        st.info(f"**Action:** {rf['action']}")
        
        # Risk trajectory prediction
        st.markdown("#### 📊 Risk Trajectory")
        if risk_score >= 25:
            st.warning("📈 **Increasing Risk:** Your current symptoms suggest risk may escalate without intervention. Early action can prevent worsening.")
        elif risk_score >= 15:
            st.info("➡️ **Stable but Elevated:** Monitor symptoms closely. Seek help if symptoms worsen or persist beyond 2 weeks.")
        else:
            st.success("📉 **Low Risk Trajectory:** Continue healthy habits and regular self-monitoring.")
        
        # Relationship analysis
        st.markdown("---")
        st.markdown("### 🔍 Relationship Analysis")
        
        analysis_found = False
        
        # Analyze correlations
        if phq9_score > 9 and gad7_score > 9:
            st.warning("⚠️ **Depression-Anxiety Comorbidity Detected:** You're experiencing elevated levels of both depression and anxiety. This is common and treatable with professional support.")
            analysis_found = True
        
        if stress_score > 20 and (phq9_score > 9 or gad7_score > 9):
            st.warning("⚠️ **Stress-Related Mental Health Impact:** High stress levels may be contributing to your depression/anxiety symptoms. Stress management techniques are recommended.")
            analysis_found = True
        
        if phq9_score > 14 or gad7_score > 14 or stress_score > 26:
            st.error("🚨 **Professional Support Recommended:** Your scores indicate significant distress. Please consider reaching out to a mental health professional.")
            analysis_found = True
        
        # Check for suicidal ideation
        if st.session_state.comprehensive_screening['phq9_responses'][8] > 0:
            st.error("⚠️ **URGENT:** You indicated thoughts of self-harm. Please call immediately:\n\n🇮🇳 India: 1860-2662-345 | 91-9820466726\n🌍 International: 988 (US) | 116 123 (UK)\n🚨 Or go to your nearest emergency room.")
            analysis_found = True
        
        # If no specific patterns detected, show positive message
        if not analysis_found:
            st.success("✅ **Good News:** Your scores don't show concerning patterns or comorbidity. Continue monitoring your mental health and practicing self-care.")
        
        # Comprehensive recommendations
        st.markdown("---")
        st.markdown("### 💡 Personalized Recommendations")
        
        recommendations = []
        
        # Depression-specific
        if phq9_score > 9:
            recommendations.append("🧠 **For Depression:** Consider behavioral activation (scheduling pleasant activities), cognitive therapy, and regular exercise")
        
        # Anxiety-specific
        if gad7_score > 9:
            recommendations.append("😌 **For Anxiety:** Practice deep breathing, progressive muscle relaxation, and challenge anxious thoughts")
        
        # Stress-specific
        if stress_score > 20:
            recommendations.append("🧘 **For Stress:** Implement time management strategies, set boundaries, and practice mindfulness meditation")
        
        # Combined recommendations
        if phq9_score > 9 and gad7_score > 9:
            recommendations.append("🤝 **Combined Approach:** Consider therapy modalities like CBT that address both depression and anxiety")
        
        if overall_index > 40:
            recommendations.append("👨‍⚕️ **Professional Support:** Your scores suggest you would benefit from professional mental health services")
            recommendations.append("💊 **Medical Evaluation:** Consider discussing medication options with a psychiatrist if symptoms persist")
        
        # General wellness recommendations if scores are low
        if overall_index < 40:
            recommendations.append("🌟 **Maintain Wellness:** Continue healthy habits like regular exercise, good sleep, social connections, and stress management")
            recommendations.append("📊 **Monitor Progress:** Retake this assessment monthly to track your mental health over time")
        
        # Age-specific recommendations
        if st.session_state.user_age:
            if st.session_state.user_age < 18:
                recommendations.append("👨‍👩‍👧 **For Teens:** Talk to parents, school counselor, or trusted adult. Teen-specific therapy can be very effective")
            elif st.session_state.user_age < 30:
                recommendations.append("🎓 **For Young Adults:** Campus counseling, online therapy platforms, and peer support groups are accessible options")
            elif st.session_state.user_age < 65:
                recommendations.append("💼 **For Adults:** Consider EAP programs through work, community mental health centers, and support groups")
            else:
                recommendations.append("👴 **For Seniors:** Senior-specific mental health services, community centers, and geriatric psychiatry available")
        
        # Always show at least basic recommendations
        if not recommendations:
            recommendations.append("✅ **Keep Up the Good Work:** Your scores are in healthy ranges. Continue practicing self-care and monitoring your mental health")
            recommendations.append("🧘 **Preventive Care:** Regular exercise, mindfulness, social connections, and good sleep hygiene support mental wellness")
        
        for rec in recommendations:
            st.info(rec)
        
        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Take New Assessment"):
                st.session_state.comprehensive_screening = {
                    'phq9_responses': None,
                    'gad7_responses': None,
                    'stress_responses': None,
                    'current_step': 1,
                    'calculated_results': None
                }
                st.session_state.nav_to = "🔍 Screening Modules"
                st.rerun()
        with col2:
            if st.button("📈 View Trends"):
                st.session_state.nav_to = "📈 Trend Analysis"
                st.rerun()
        with col3:
            if st.button("📞 Get Resources"):
                st.session_state.nav_to = "📞 Resources"
                st.rerun()

        # Download Report
        st.markdown("---")
        st.markdown("### 📥 Download Your Report")

        def generate_pdf_report(results, risk_factors, recommendations, username):
            from fpdf import FPDF
            import re

            def clean(text):
                # Strip emojis and non-latin chars for fpdf compatibility
                return re.sub(r'[^\x00-\x7F]+', '', str(text)).strip()

            pdf = FPDF()
            pdf.add_page()
            pdf.set_margins(10, 10, 10)
            pdf.set_auto_page_break(auto=True, margin=15)

            # Title
            pdf.set_font("Helvetica", "B", 20)
            pdf.set_text_color(44, 122, 123)
            pdf.cell(0, 12, "Comprehensive Mental Health Report", ln=True, align="C")
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 6, f"Generated: {results['timestamp']}   |   User: {username}", ln=True, align="C")
            pdf.ln(6)

            # Scores
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(44, 122, 123)
            pdf.cell(0, 10, "Assessment Scores", ln=True)
            pdf.set_draw_color(44, 122, 123)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)

            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(50, 50, 50)
            col_w = 60
            pdf.set_fill_color(240, 253, 250)
            for label, score, severity in [
                ("Depression (PHQ-9)", f"{results['phq9_score']}/27", results['phq9_severity']),
                ("Anxiety (GAD-7)",    f"{results['gad7_score']}/21", results['gad7_severity']),
                ("Stress (PSS)",       f"{results['stress_score']}/40", results['stress_severity']),
            ]:
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(col_w, 8, clean(label), border=1, fill=True)
                pdf.set_font("Helvetica", "", 11)
                pdf.cell(col_w, 8, clean(score), border=1)
                pdf.cell(col_w, 8, clean(severity), border=1, ln=True)
            pdf.ln(5)

            # Overall index
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(44, 122, 123)
            pdf.cell(0, 9, f"Overall Mental Health Index: {results['overall_index']:.1f}/100", ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(0, 7, f"Status: {clean(results['overall_status'])}   |   Risk Level: {clean(risk_level)} (Score: {risk_score})", ln=True)
            pdf.ln(5)

            # Risk factors
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(44, 122, 123)
            pdf.cell(0, 10, "Risk Factors Detected", ln=True)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)

            if not risk_factors:
                pdf.set_font("Helvetica", "", 11)
                pdf.set_text_color(50, 50, 50)
                pdf.cell(0, 7, "No significant risk factors detected.", ln=True)
            else:
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_fill_color(44, 122, 123)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(30, 7, "Severity", border=1, fill=True)
                pdf.cell(50, 7, "Factor", border=1, fill=True)
                pdf.cell(110, 7, "Recommended Action", border=1, fill=True, ln=True)
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(50, 50, 50)
                for rf in risk_factors:
                    pdf.set_fill_color(249, 249, 249)
                    pdf.cell(30, 7, clean(rf['severity']), border=1, fill=True)
                    pdf.cell(50, 7, clean(rf['factor']), border=1, fill=True)
                    pdf.multi_cell(110, 7, clean(rf['action']), border=1)
            pdf.ln(5)

            # Recommendations
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(44, 122, 123)
            pdf.cell(0, 10, "Personalized Recommendations", ln=True)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            for rec in recommendations:
                pdf.multi_cell(190, 7, f"- {clean(rec)}")
            pdf.ln(5)

            # Footer
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(150, 150, 150)
            pdf.multi_cell(190, 6, "This report is for screening purposes only and does not replace professional medical advice. Always consult with a qualified mental health professional for diagnosis and treatment.")

            return bytes(pdf.output())

        pdf_bytes = generate_pdf_report(results, risk_factors, recommendations, st.session_state.current_user)
        st.download_button(
            label="📄 Download Report (PDF)",
            data=pdf_bytes,
            file_name=f"mental_health_report_{results['timestamp'][:10]}.pdf",
            mime="application/pdf",
            use_container_width=False
        )

    next_page_button("📋 Comprehensive Report")

# Page: Trend Analysis
elif page == "📈 Trend Analysis":
    st.title("📈 Emotional Trend Dashboard")
    
    if not st.session_state.mood_history:
        st.info("Start tracking your mood to see trends and insights!")
    else:
        # Mood over time
        df_moods = pd.DataFrame(st.session_state.mood_history)
        df_moods['date'] = pd.to_datetime(df_moods['date'])
        
        fig1 = px.line(df_moods, x='date', y='mood', 
                      title='Mood Trend Over Time',
                      labels={'mood': 'Mood Score (1-10)', 'date': 'Date'})
        fig1.update_layout(
            template='plotly_white',
            plot_bgcolor='rgba(255, 255, 255, 0.9)',
            paper_bgcolor='rgba(255, 255, 255, 0.9)'
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Most common emotions
            all_emotions = []
            for entry in st.session_state.mood_history:
                all_emotions.extend(entry['emotions'])
            
            if all_emotions:
                emotion_counts = pd.Series(all_emotions).value_counts()
                fig2 = px.bar(x=emotion_counts.index, y=emotion_counts.values,
                            title='Most Common Emotions',
                            labels={'x': 'Emotion', 'y': 'Frequency'},
                            color=emotion_counts.values,
                            color_continuous_scale='Teal')
                fig2.update_layout(
                    template='plotly_white',
                    plot_bgcolor='rgba(255, 255, 255, 0.9)',
                    paper_bgcolor='rgba(255, 255, 255, 0.9)'
                )
                st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            # Activities correlation
            all_activities = []
            for entry in st.session_state.mood_history:
                all_activities.extend(entry['activities'])
            
            if all_activities:
                activity_counts = pd.Series(all_activities).value_counts()
                fig3 = px.pie(values=activity_counts.values, names=activity_counts.index,
                            title='Activity Distribution',
                            color_discrete_sequence=px.colors.sequential.Teal)
                fig3.update_layout(
                    template='plotly_white',
                    plot_bgcolor='rgba(255, 255, 255, 0.9)',
                    paper_bgcolor='rgba(255, 255, 255, 0.9)'
                )
                st.plotly_chart(fig3, use_container_width=True)
        
        # Screening history
        if st.session_state.screening_results:
            st.markdown("### 🔍 Screening History")
            screening_df = pd.DataFrame(st.session_state.screening_results.values())
            st.dataframe(screening_df, use_container_width=True)

    next_page_button("📈 Trend Analysis")

# Page: Stress Relief Games
elif page == "🎮 Stress Relief Games":
    st.title("🎮 Stress Relief Games & Activities")
    
    st.info("Take a break and relax with these calming interactive activities designed to reduce stress and anxiety")
    
    # Game selection tabs
    game_tab1, game_tab2, game_tab3, game_tab4, game_tab5 = st.tabs([
        "🫧 Breathing Exercise", 
        "🎨 Color Matching Game", 
        "🧩 Memory Game",
        "🎯 Focus Game",
        "🌊 Relaxation Sounds"
    ])
    
    # Tab 1: Breathing Exercise
    with game_tab1:
        st.markdown("### 🫧 Guided Breathing Exercise")
        st.write("Follow the breathing pattern to calm your mind and reduce stress")
        
        col_breath1, col_breath2 = st.columns([2, 1])
        
        with col_breath1:
            breathing_type = st.selectbox(
                "Choose breathing technique:",
                ["4-7-8 Breathing (Relaxation)", "Box Breathing (Focus)", "4-4-4 Breathing (Quick Calm)"]
            )
            
            if breathing_type == "4-7-8 Breathing (Relaxation)":
                st.markdown("""
                **4-7-8 Breathing Technique:**
                - Inhale through nose for 4 seconds
                - Hold breath for 7 seconds
                - Exhale through mouth for 8 seconds
                - Repeat 4 times
                
                **Benefits:** Reduces anxiety, helps with sleep
                """)
                inhale, hold, exhale = 4, 7, 8
            elif breathing_type == "Box Breathing (Focus)":
                st.markdown("""
                **Box Breathing Technique:**
                - Inhale for 4 seconds
                - Hold for 4 seconds
                - Exhale for 4 seconds
                - Hold for 4 seconds
                - Repeat 4 times
                
                **Benefits:** Improves focus, reduces stress
                """)
                inhale, hold, exhale = 4, 4, 4
            else:
                st.markdown("""
                **4-4-4 Breathing Technique:**
                - Inhale for 4 seconds
                - Hold for 4 seconds
                - Exhale for 4 seconds
                - Repeat 5 times
                
                **Benefits:** Quick stress relief
                """)
                inhale, hold, exhale = 4, 4, 4
            
            if st.button("🫁 Start Breathing Exercise", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for cycle in range(4):
                    # Inhale
                    status_text.markdown(f"### 🌬️ Breathe IN (Cycle {cycle + 1}/4)")
                    for i in range(inhale):
                        progress_bar.progress((i + 1) / inhale)
                        import time
                        time.sleep(1)
                    
                    # Hold
                    status_text.markdown(f"### 🤲 HOLD (Cycle {cycle + 1}/4)")
                    for i in range(hold):
                        progress_bar.progress((i + 1) / hold)
                        time.sleep(1)
                    
                    # Exhale
                    status_text.markdown(f"### 💨 Breathe OUT (Cycle {cycle + 1}/4)")
                    for i in range(exhale):
                        progress_bar.progress((i + 1) / exhale)
                        time.sleep(1)
                    
                    progress_bar.progress(0)
                
                status_text.markdown("### ✅ Exercise Complete! How do you feel?")
                st.balloons()
        
        with col_breath2:
            st.markdown("### 📊 Benefits")
            st.success("✓ Reduces anxiety")
            st.success("✓ Lowers heart rate")
            st.success("✓ Improves focus")
            st.success("✓ Promotes relaxation")
            st.success("✓ Better sleep")
    
    # Tab 2: Color Therapy
    with game_tab2:
        st.markdown("### 🎨 Color Matching Game")
        st.write("Match colors to their mood descriptions - a fun way to learn color therapy!")
        
        st.info("💡 **How to Play:** Match each color with its therapeutic benefit. Learn about color therapy while having fun!")
        
        # Initialize game state
        if 'color_game_score' not in st.session_state:
            st.session_state.color_game_score = 0
        if 'color_game_round' not in st.session_state:
            st.session_state.color_game_round = 0
        if 'color_game_started' not in st.session_state:
            st.session_state.color_game_started = False
        if 'color_game_answers' not in st.session_state:
            st.session_state.color_game_answers = {}
        
        # Color therapy database
        color_therapy_data = {
            "Red": {
                "color": "#FF0000",
                "benefit": "Energizes and stimulates",
                "mood": "Passionate, Active",
                "use": "When you need energy and motivation"
            },
            "Blue": {
                "color": "#0077BE",
                "benefit": "Calms and relaxes",
                "mood": "Peaceful, Tranquil",
                "use": "When feeling anxious or stressed"
            },
            "Green": {
                "color": "#2D6A4F",
                "benefit": "Balances and heals",
                "mood": "Harmonious, Balanced",
                "use": "When seeking emotional balance"
            },
            "Yellow": {
                "color": "#FFD60A",
                "benefit": "Uplifts and cheers",
                "mood": "Happy, Optimistic",
                "use": "When feeling down or sad"
            },
            "Purple": {
                "color": "#7209B7",
                "benefit": "Inspires and soothes",
                "mood": "Creative, Spiritual",
                "use": "During meditation or creative work"
            },
            "Orange": {
                "color": "#FF6B35",
                "benefit": "Warms and encourages",
                "mood": "Friendly, Confident",
                "use": "When needing social confidence"
            },
            "Pink": {
                "color": "#FF69B4",
                "benefit": "Comforts and nurtures",
                "mood": "Loving, Gentle",
                "use": "When needing self-compassion"
            },
            "Turquoise": {
                "color": "#00CED1",
                "benefit": "Refreshes and clarifies",
                "mood": "Clear, Focused",
                "use": "When needing mental clarity"
            }
        }
        
        col_game, col_info = st.columns([2, 1])
        
        with col_game:
            if not st.session_state.color_game_started:
                st.markdown("### 🎮 Ready to Play?")
                st.write("Test your knowledge of color therapy and learn how colors affect your mood!")
                
                if st.button("🎯 Start Game", use_container_width=True, type="primary"):
                    st.session_state.color_game_started = True
                    st.session_state.color_game_score = 0
                    st.session_state.color_game_round = 0
                    st.session_state.color_game_answers = {}
                    st.rerun()
            
            else:
                # Game in progress
                st.markdown(f"### Round {st.session_state.color_game_round + 1}/5")
                st.markdown(f"**Score: {st.session_state.color_game_score} points**")
                
                if st.session_state.color_game_round < 5:
                    # Select random colors for this round
                    import random
                    if f'round_{st.session_state.color_game_round}_colors' not in st.session_state:
                        all_colors = list(color_therapy_data.keys())
                        random.shuffle(all_colors)
                        st.session_state[f'round_{st.session_state.color_game_round}_colors'] = all_colors[:4]
                        st.session_state[f'round_{st.session_state.color_game_round}_correct'] = all_colors[0]
                    
                    round_colors = st.session_state[f'round_{st.session_state.color_game_round}_colors']
                    correct_color = st.session_state[f'round_{st.session_state.color_game_round}_correct']
                    
                    # Display the question
                    st.markdown(f"### Which color {color_therapy_data[correct_color]['benefit'].lower()}?")
                    
                    # Display color options
                    cols = st.columns(4)
                    for idx, color_name in enumerate(round_colors):
                        with cols[idx]:
                            color_data = color_therapy_data[color_name]
                            
                            # Create clickable color box
                            if st.button(
                                f"",
                                key=f"color_btn_{st.session_state.color_game_round}_{idx}",
                                use_container_width=True
                            ):
                                # Check answer
                                if color_name == correct_color:
                                    st.session_state.color_game_score += 20
                                    st.success(f"✅ Correct! {color_name} {color_therapy_data[color_name]['benefit'].lower()}!")
                                else:
                                    st.error(f"❌ Not quite! The answer was {correct_color}")
                                
                                st.session_state.color_game_round += 1
                                import time
                                time.sleep(1.5)
                                st.rerun()
                            
                            # Display color box
                            st.markdown(f"""
                            <div style="
                                background: {color_data['color']};
                                height: 120px;
                                border-radius: 15px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                color: white;
                                font-weight: bold;
                                font-size: 1.2rem;
                                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                                cursor: pointer;
                                margin-bottom: 10px;
                            ">
                                {color_name}
                            </div>
                            """, unsafe_allow_html=True)
                
                else:
                    # Game over
                    st.markdown("### 🎉 Game Complete!")
                    
                    # Calculate performance
                    percentage = (st.session_state.color_game_score / 100) * 100
                    
                    if percentage == 100:
                        message = "Perfect! You're a color therapy expert! 🌟"
                        emoji = "🏆"
                    elif percentage >= 80:
                        message = "Excellent! You know your colors well! 🎯"
                        emoji = "⭐"
                    elif percentage >= 60:
                        message = "Good job! Keep learning about color therapy! 👍"
                        emoji = "😊"
                    else:
                        message = "Nice try! Play again to learn more! 💪"
                        emoji = "🎮"
                    
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 30px;
                        border-radius: 20px;
                        text-align: center;
                        color: white;
                        margin: 20px 0;
                    ">
                        <h1 style="font-size: 4rem; margin: 0;">{emoji}</h1>
                        <h2 style="margin: 10px 0;">Final Score: {st.session_state.color_game_score}/100</h2>
                        <p style="font-size: 1.2rem; margin: 10px 0;">{message}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("🔄 Play Again", use_container_width=True, type="primary"):
                            st.session_state.color_game_started = False
                            st.session_state.color_game_score = 0
                            st.session_state.color_game_round = 0
                            # Clear round data
                            for i in range(5):
                                if f'round_{i}_colors' in st.session_state:
                                    del st.session_state[f'round_{i}_colors']
                                if f'round_{i}_correct' in st.session_state:
                                    del st.session_state[f'round_{i}_correct']
                            st.rerun()
                    
                    with col_btn2:
                        if st.button("📚 Learn More", use_container_width=True):
                            st.session_state.show_color_guide = True
        
        with col_info:
            st.markdown("### 📖 Color Guide")
            
            # Show color meanings
            for color_name, data in color_therapy_data.items():
                with st.expander(f"{color_name}"):
                    st.markdown(f"""
                    <div style="
                        background: {data['color']};
                        height: 60px;
                        border-radius: 10px;
                        margin-bottom: 10px;
                    "></div>
                    """, unsafe_allow_html=True)
                    
                    st.write(f"**Benefit:** {data['benefit']}")
                    st.write(f"**Mood:** {data['mood']}")
                    st.write(f"**Use:** {data['use']}")
        
        st.markdown("---")
        
        # Educational section
        st.markdown("### 🎨 About Color Therapy")
        
        col_edu1, col_edu2, col_edu3 = st.columns(3)
        
        with col_edu1:
            st.markdown("""
            **🌈 What is Color Therapy?**
            
            Color therapy (chromotherapy) uses colors to adjust body vibrations to frequencies that result in health and harmony.
            """)
        
        with col_edu2:
            st.markdown("""
            **🧠 How It Works**
            
            Different colors have different wavelengths and frequencies that can affect our mood, emotions, and even physical health.
            """)
        
        with col_edu3:
            st.markdown("""
            **💡 Daily Use**
            
            Surround yourself with colors that match your needs - wear them, decorate with them, or simply visualize them!
            """)
        
        st.info("💡 **Tip:** Use this game to learn which colors can help you in different situations. Apply this knowledge in your daily life!")
    
    # Tab 3: Memory Game
    with game_tab3:
        st.markdown("### 🧩 Memory Matching Game")
        st.write("Match the emoji pairs to improve focus and reduce stress")
        
        # Initialize game state
        if 'memory_game' not in st.session_state:
            emojis = ["😊", "🌟", "🌈", "🦋", "🌸", "🎨", "🎵", "☀️"]
            cards = emojis + emojis
            import random
            random.shuffle(cards)
            st.session_state.memory_game = {
                'cards': cards,
                'revealed': [False] * 16,
                'matched': [False] * 16,
                'first_card': None,
                'moves': 0,
                'matches': 0
            }
        
        game = st.session_state.memory_game
        
        col_game1, col_game2 = st.columns([3, 1])
        
        with col_game1:
            # Display cards in 4x4 grid
            for row in range(4):
                cols = st.columns(4)
                for col_idx, col in enumerate(cols):
                    card_idx = row * 4 + col_idx
                    
                    with col:
                        if game['matched'][card_idx]:
                            st.markdown(f"<div style='text-align: center; font-size: 40px; padding: 20px; background: #c8e6c9; border-radius: 10px;'>{game['cards'][card_idx]}</div>", unsafe_allow_html=True)
                        elif game['revealed'][card_idx]:
                            st.markdown(f"<div style='text-align: center; font-size: 40px; padding: 20px; background: #fff9c4; border-radius: 10px;'>{game['cards'][card_idx]}</div>", unsafe_allow_html=True)
                        else:
                            if st.button("❓", key=f"card_{card_idx}", use_container_width=True):
                                if game['first_card'] is None:
                                    game['first_card'] = card_idx
                                    game['revealed'][card_idx] = True
                                elif game['first_card'] != card_idx and not game['revealed'][card_idx]:
                                    game['revealed'][card_idx] = True
                                    game['moves'] += 1
                                    
                                    # Check for match
                                    if game['cards'][game['first_card']] == game['cards'][card_idx]:
                                        game['matched'][game['first_card']] = True
                                        game['matched'][card_idx] = True
                                        game['matches'] += 1
                                        st.success("✅ Match found!")
                                    else:
                                        import time
                                        time.sleep(0.5)
                                        game['revealed'][game['first_card']] = False
                                        game['revealed'][card_idx] = False
                                    
                                    game['first_card'] = None
                                
                                st.rerun()
        
        with col_game2:
            st.markdown("### 📊 Stats")
            st.metric("Moves", game['moves'])
            st.metric("Matches", f"{game['matches']}/8")
            
            if game['matches'] == 8:
                st.success("🎉 You Won!")
                st.balloons()
            
            if st.button("🔄 New Game", use_container_width=True):
                del st.session_state.memory_game
                st.rerun()
    
    # Tab 4: Focus Game
    with game_tab4:
        st.markdown("### 🎯 Focus & Mindfulness Game")
        st.write("Follow the moving dot with your eyes to practice mindfulness")
        
        col_focus1, col_focus2 = st.columns([2, 1])
        
        with col_focus1:
            focus_duration = st.slider("Duration (seconds)", 10, 60, 30)
            
            if st.button("🎯 Start Focus Exercise", use_container_width=True):
                st.markdown("### 👁️ Follow the dot with your eyes")
                st.markdown("Keep your head still and only move your eyes")
                
                placeholder = st.empty()
                
                import time
                import math
                
                for i in range(focus_duration * 2):
                    angle = (i / 10) * 2 * math.pi
                    x = 50 + 40 * math.cos(angle)
                    y = 50 + 40 * math.sin(angle)
                    
                    html = f"""
                    <div style="position: relative; width: 100%; height: 400px; background: linear-gradient(135deg, #e0f2f1, #b2dfdb); border-radius: 20px;">
                        <div style="position: absolute; left: {x}%; top: {y}%; width: 30px; height: 30px; background: #26a69a; border-radius: 50%; transform: translate(-50%, -50%); box-shadow: 0 4px 15px rgba(38, 166, 154, 0.5);"></div>
                    </div>
                    """
                    
                    placeholder.markdown(html, unsafe_allow_html=True)
                    time.sleep(0.5)
                
                placeholder.markdown("### ✅ Exercise Complete!")
                st.success("Great job! You practiced mindfulness for " + str(focus_duration) + " seconds")
        
        with col_focus2:
            st.markdown("### 💡 Benefits")
            st.info("✓ Improves concentration")
            st.info("✓ Reduces mind wandering")
            st.info("✓ Practices mindfulness")
            st.info("✓ Calms racing thoughts")
    
    # Tab 5: Relaxation Sounds
    with game_tab5:
        st.markdown("### 🌊 Relaxation Sounds")
        st.write("Listen to calming sounds to reduce stress and anxiety")
        
        st.info("💡 **Tip:** Use headphones for the best experience. Close your eyes and focus on the sounds.")
        
        # Check for local audio files first
        import os
        from pathlib import Path
        
        audio_dir = Path("audio")
        use_local_audio = audio_dir.exists()
        
        # Sound selection
        sound_category = st.radio(
            "Choose sound category:",
            ["🌊 Nature Sounds", "🎵 Ambient Sounds", "🧘 Meditation Sounds"],
            horizontal=True
        )
        
        if sound_category == "🌊 Nature Sounds":
            st.markdown("#### 🌊 Nature Sounds")
            st.write("Immerse yourself in the calming sounds of nature")
            
            # Ocean Waves
            st.markdown("##### 🌊 Ocean Waves")
            st.write("Gentle waves lapping at the shore - perfect for relaxation and sleep")
            
            if use_local_audio and (audio_dir / "Ocean Waves.mp3").exists():
                st.audio(str(audio_dir / "Ocean Waves.mp3"))
            else:
                st.audio("https://cdn.pixabay.com/download/audio/2022/03/10/audio_4a1ad0b93c.mp3")
            
            st.caption("🎧 Benefits: Reduces anxiety, promotes sleep, lowers heart rate")
            st.markdown("---")
            
            # Rain Sounds
            st.markdown("##### 🌧️ Gentle Rain")
            st.write("Soft rain falling - creates peaceful white noise")
            
            if use_local_audio and (audio_dir / "Gentle Rain.mp3").exists():
                st.audio(str(audio_dir / "Gentle Rain.mp3"))
            else:
                st.audio("https://cdn.pixabay.com/download/audio/2022/05/13/audio_2b1d1a6e5e.mp3")
            
            st.caption("🎧 Benefits: Improves focus, masks distracting noises, promotes calm")
            st.markdown("---")
            
            # Forest Sounds
            st.markdown("##### 🌲 Forest Ambience")
            st.write("Birds chirping and leaves rustling - connect with nature")
            
            if use_local_audio and (audio_dir / "Forest Birds.mp3").exists():
                st.audio(str(audio_dir / "Forest Birds.mp3"))
            else:
                st.audio("https://cdn.pixabay.com/download/audio/2022/03/15/audio_c610232532.mp3")
            
            st.caption("🎧 Benefits: Reduces stress, improves mood, enhances creativity")
        
        elif sound_category == "🎵 Ambient Sounds":
            st.markdown("#### 🎵 Ambient Sounds")
            st.write("Soothing ambient sounds for deep relaxation")
            
            # Crackling Fire
            st.markdown("##### 🔥 Crackling Fireplace")
            st.write("Warm fireplace crackling - creates cozy atmosphere")
            
            if use_local_audio and (audio_dir / "Crackling Fire.mp3").exists():
                st.audio(str(audio_dir / "Crackling Fire.mp3"))
            else:
                st.audio("https://cdn.pixabay.com/download/audio/2022/03/10/audio_9b0073c0c5.mp3")
            
            st.caption("🎧 Benefits: Promotes relaxation, reduces tension, improves sleep")
            st.markdown("---")
            
            # Wind Chimes
            st.markdown("##### 🎐 Wind Chimes")
            st.write("Gentle wind chimes tinkling - peaceful and meditative")
            st.audio("https://cdn.pixabay.com/download/audio/2021/08/04/audio_12b0c7443c.mp3")
            st.caption("🎧 Benefits: Enhances mindfulness, promotes peace, reduces anxiety")
            st.markdown("---")
            
            # Soft Piano
            st.markdown("##### 🎹 Soft Piano")
            st.write("Gentle piano melody - calming and beautiful")
            
            if use_local_audio and (audio_dir / "Soft Piano.mp3").exists():
                st.audio(str(audio_dir / "Soft Piano.mp3"))
            else:
                st.audio("https://cdn.pixabay.com/download/audio/2022/08/02/audio_0625c1539c.mp3")
            
            st.caption("🎧 Benefits: Reduces stress, improves mood, aids concentration")
        
        else:  # Meditation Sounds
            st.markdown("#### 🧘 Meditation Sounds")
            st.write("Sounds specifically designed for meditation and mindfulness")
            
            # Singing Bowl
            st.markdown("##### 🎵 Tibetan Singing Bowl")
            st.write("Deep resonant tones - perfect for meditation")
            
            if use_local_audio and (audio_dir / "Tibetan Singing Bowl.mp3").exists():
                st.audio(str(audio_dir / "Tibetan Singing Bowl.mp3"))
            else:
                st.audio("https://cdn.pixabay.com/download/audio/2022/03/15/audio_4dedf2bf94.mp3")
            
            st.caption("🎧 Benefits: Deepens meditation, balances energy, promotes healing")
            st.markdown("---")
            
            # Meditation Bell
            st.markdown("##### 🔔 Meditation Bell")
            st.write("Clear bell tones - marks meditation intervals")
            
            if use_local_audio and (audio_dir / "Meditation Bell.mp3").exists():
                st.audio(str(audio_dir / "Meditation Bell.mp3"))
            else:
                st.audio("https://cdn.pixabay.com/download/audio/2021/08/04/audio_d1718ab41b.mp3")
            
            st.caption("🎧 Benefits: Enhances focus, marks time, brings awareness")
            st.markdown("---")
            
            # Om Chanting
            st.markdown("##### 🕉️ Peaceful Meditation Music")
            st.write("Calming meditation music - for deep relaxation")
            st.audio("https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3")
            st.caption("🎧 Benefits: Deepens meditation, reduces stress, promotes inner peace")
        
        st.markdown("---")
        st.markdown("### 🧘 Guided Visualization")
        st.write("Combine sounds with visualization for maximum relaxation")
        
        visualization = st.selectbox(
            "Choose a visualization:",
            ["Beach Sunset", "Mountain Peak", "Peaceful Garden", "Starry Night"]
        )
        
        if visualization == "Beach Sunset":
            st.markdown("""
            **🌅 Beach Sunset Visualization:**
            
            Close your eyes and imagine...
            - You're sitting on a warm, sandy beach
            - The sun is setting, painting the sky in oranges and pinks
            - Gentle waves roll in and out with a soothing rhythm
            - A warm breeze touches your skin
            - You feel completely peaceful and relaxed
            - All your worries drift away with the tide
            
            💡 **Tip:** Play Ocean Waves sound while visualizing
            """)
        elif visualization == "Mountain Peak":
            st.markdown("""
            **⛰️ Mountain Peak Visualization:**
            
            Close your eyes and imagine...
            - You're standing on a peaceful mountain peak
            - Fresh, crisp air fills your lungs
            - You can see for miles in every direction
            - Clouds drift slowly below you
            - You feel strong, calm, and centered
            - Your mind is clear and focused
            
            💡 **Tip:** Play Forest Ambience while visualizing
            """)
        elif visualization == "Peaceful Garden":
            st.markdown("""
            **🌸 Peaceful Garden Visualization:**
            
            Close your eyes and imagine...
            - You're in a beautiful, tranquil garden
            - Colorful flowers bloom all around you
            - Butterflies dance from flower to flower
            - A gentle fountain bubbles nearby
            - The air smells sweet and fresh
            - You feel safe, calm, and content
            
            💡 **Tip:** Play Wind Chimes while visualizing
            """)
        else:
            st.markdown("""
            **✨ Starry Night Visualization:**
            
            Close your eyes and imagine...
            - You're lying on soft grass under a starry sky
            - Countless stars twinkle above you
            - The Milky Way stretches across the darkness
            - A gentle breeze keeps you comfortable
            - You feel small yet connected to the universe
            - All your stress melts into the vastness of space
            
            💡 **Tip:** Play Meditation Music while visualizing
            """)
        
        st.markdown("---")
        st.markdown("### ⏱️ Timed Meditation Session")
        
        col_med1, col_med2 = st.columns([2, 1])
        
        with col_med1:
            meditation_duration = st.slider("Meditation Duration (minutes)", 1, 20, 5)
            
            if st.button("🧘 Start Timed Meditation", use_container_width=True):
                st.info(f"🧘 Starting {meditation_duration}-minute meditation...")
                st.write("💡 Play a sound above, close your eyes, and focus on your breath")
                
                progress = st.progress(0)
                status = st.empty()
                
                import time
                total_seconds = meditation_duration * 60
                
                for i in range(total_seconds):
                    progress.progress((i + 1) / total_seconds)
                    remaining = total_seconds - i - 1
                    mins = remaining // 60
                    secs = remaining % 60
                    status.write(f"⏱️ Time remaining: {mins}:{secs:02d}")
                    time.sleep(1)
                
                status.write("✅ Meditation complete!")
                st.success(f"🎉 You meditated for {meditation_duration} minutes! Notice how you feel now.")
                st.balloons()
        
        with col_med2:
            st.markdown("### 💡 Tips")
            st.info("✓ Use headphones")
            st.info("✓ Find quiet space")
            st.info("✓ Sit comfortably")
            st.info("✓ Close your eyes")
            st.info("✓ Focus on breath")
            st.info("✓ Let thoughts pass")
    
    # Track game usage
    st.markdown("---")
    st.markdown("### 📊 Your Wellness Activity")
    
    col_track1, col_track2, col_track3 = st.columns(3)
    
    with col_track1:
        if st.button("😊 I Feel Better", use_container_width=True):
            st.success("Wonderful! Keep practicing these activities regularly")
            st.balloons()
    
    with col_track2:
        if st.button("😌 I Feel Calm", use_container_width=True):
            st.success("Great! You're building healthy stress management habits")
    
    with col_track3:
        if st.button("🔄 Try Another", use_container_width=True):
            st.info("Explore different activities to find what works best for you")

    next_page_button("🎮 Stress Relief Games")

# Page: Healthy Nutrition
elif page == "🥗 Healthy Nutrition":
    st.title("🥗 Healthy Nutrition & Wellness")
    st.markdown("*Nourish your body and mind with healthy food choices*")
    st.markdown("---")
    
    # Motivational Quote Section
    import random
    
    motivational_quotes = [
        ("Let food be thy medicine and medicine be thy food.", "— Hippocrates"),
        ("Take care of your body. It's the only place you have to live.", "— Jim Rohn"),
        ("Eating well is a form of self-respect.", "— Unknown"),
        ("Your body is a temple, but only if you treat it right.", "— Astrid Alauda"),
        ("Health is a state of complete physical, mental and social well-being.", "— WHO"),
        ("An apple a day keeps the doctor away.", "— Traditional Proverb"),
        ("Wellness is a connection of paths: it's physical, it's mental, it's spiritual.", "— Donna Karan"),
        ("The greatest wealth is health.", "— Virgil"),
        ("To eat is a necessity, but to eat intelligently is an art.", "— La Rochefoucauld"),
        ("Nutrition is the foundation upon which all our health, strength and character is built.", "— Unknown"),
        ("You don't have to see the whole staircase, just take the first step.", "— Martin Luther King Jr."),
        ("Every accomplishment starts with the decision to try.", "— Unknown"),
        ("Your health is an investment, not an expense.", "— Unknown"),
        ("Believe you can and you're halfway there.", "— Theodore Roosevelt"),
        ("The only impossible journey is the one you never begin.", "— Tony Robbins"),
    ]
    
    emotional_support_quotes = [
        "You are stronger than you think. 💪",
        "Progress, not perfection. Every small step counts. 🌱",
        "Be kind to yourself. You deserve it. 💝",
        "Your mental health matters. Take care of it. 🧠",
        "You are not alone in this journey. 🤝",
        "Healing is not linear, and that's okay. 🌈",
        "You've survived 100% of your worst days. 🌟",
        "Your body is listening to what your mind is saying. 🎯",
        "Nourish yourself like you would a loved one. 💕",
        "Small changes lead to big results. 🚀",
        "You are worthy of good health and happiness. ✨",
        "Today is a new opportunity to take care of yourself. 🌅",
        "Your wellness journey is unique and valid. 🌸",
        "Celebrate every victory, no matter how small. 🎉",
        "You are doing better than you think. 💫",
    ]
    
    # Display random quotes
    col1, col2 = st.columns(2)
    
    with col1:
        quote, author = random.choice(motivational_quotes)
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px; border-radius: 15px; margin-bottom: 20px;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
            <p style="color: white; font-size: 18px; font-style: italic; margin: 0 0 15px 0;">
                💭 "{quote}"
            </p>
            <p style="color: rgba(255,255,255,0.9); font-size: 14px; margin: 0; text-align: right;">
                {author}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        support_quote = random.choice(emotional_support_quotes)
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 25px; border-radius: 15px; margin-bottom: 20px;
                    box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);">
            <p style="color: white; font-size: 18px; font-weight: 600; margin: 0;">
                {support_quote}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Healthy Food Categories
    st.markdown("## 🍎 Healthy Food Categories")
    
    food_categories = {
        "🥬 Leafy Greens": {
            "foods": ["Spinach", "Kale", "Lettuce", "Arugula", "Swiss Chard"],
            "benefits": "Rich in Vitamin K, folate, and antioxidants. Research shows 1+ serving daily slows cognitive decline and supports memory. (Neurology, 2018)",
            "color": "#43e97b",
            "source": "NIH/Neurology Study",
            "servings": "1-2 cups raw or ½-1 cup cooked daily"
        },
        "🥕 Colorful Vegetables": {
            "foods": ["Carrots", "Bell Peppers", "Broccoli", "Tomatoes", "Cauliflower"],
            "benefits": "Rich in vitamins A, C, and fiber. Supports brain function and reduces inflammation. (Frontiers in Nutrition)",
            "color": "#fa709a",
            "source": "Frontiers in Nutrition",
            "servings": "2-3 cups daily (variety of colors)"
        },
        "🍎 Fresh Fruits": {
            "foods": ["Berries", "Apples", "Bananas", "Oranges", "Avocados"],
            "benefits": "Antioxidants and natural sugars. Berries linked to improved mood and cognitive function.",
            "color": "#fee140",
            "source": "Nutritional Research",
            "servings": "2-3 servings daily (1 serving = 1 medium fruit or ½ cup berries)"
        },
        "🥜 Proteins & Nuts": {
            "foods": ["Almonds", "Walnuts", "Chickpeas", "Lentils", "Tofu"],
            "benefits": "Omega-3s in walnuts support depression prevention. APA recommends omega-3 for mental health. (American Psychiatric Association)",
            "color": "#4facfe",
            "source": "APA Guidelines",
            "servings": "1 oz nuts daily (23 almonds or 14 walnut halves) + 1 serving protein per meal"
        },
        "🌾 Whole Grains": {
            "foods": ["Oats", "Brown Rice", "Quinoa", "Whole Wheat", "Barley"],
            "benefits": "Complex carbs stabilize blood sugar and serotonin levels. Supports mood stability and sustained energy.",
            "color": "#43e97b",
            "source": "Nutritional Psychiatry",
            "servings": "3-6 servings daily (1 serving = 1 slice bread OR ½ cup cooked grain)"
        },
        "🥛 Dairy & Alternatives": {
            "foods": ["Yogurt", "Milk", "Cheese", "Almond Milk", "Oat Milk"],
            "benefits": "Probiotics support gut-brain axis. Calcium supports neurotransmitter function and mood regulation.",
            "color": "#b39ddb",
            "source": "Gut-Brain Research",
            "servings": "2-3 servings daily (1 serving = 1 cup milk/yogurt or 1.5 oz cheese)"
        }
    }
    
    # Display food categories in grid
    cols = st.columns(2)
    for idx, (category, info) in enumerate(food_categories.items()):
        with cols[idx % 2]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {info['color']} 0%, {info['color']}dd 100%); 
                        padding: 20px; border-radius: 12px; margin-bottom: 15px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h4 style="color: white; margin: 0 0 10px 0;">{category}</h4>
                <p style="color: white; font-size: 13px; margin: 0 0 10px 0;">
                    <strong>Examples:</strong> {', '.join(info['foods'])}
                </p>
                <p style="color: rgba(255,255,255,0.95); font-size: 13px; margin: 0 0 8px 0;">
                    ✨ {info['benefits']}
                </p>
                <p style="color: rgba(255,255,255,0.9); font-size: 12px; margin: 0 0 8px 0; font-weight: 600;">
                    � Daily Serving: {info['servings']}
                </p>
                <p style="color: rgba(255,255,255,0.8); font-size: 11px; margin: 0; font-style: italic;">
                    📚 Source: {info['source']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Daily Nutrition Tracker
    st.markdown("## 📊 Daily Nutrition Tracker")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Track Your Healthy Eating")
        
        # Initialize session state for nutrition tracking
        if 'nutrition_log' not in st.session_state:
            st.session_state.nutrition_log = []
        
        with st.form("nutrition_form"):
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
            food_item = st.text_input("Food Item", placeholder="e.g., Grilled Chicken Salad")
            servings = st.number_input("Servings", min_value=0.5, max_value=5.0, step=0.5, value=1.0)
            mood_after = st.slider("Mood After Eating (1-10)", 1, 10, 7)
            notes = st.text_area("Notes", placeholder="How did you feel? Any observations?", height=80)
            
            if st.form_submit_button("✅ Log Meal", use_container_width=True):
                from datetime import datetime
                entry = {
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'meal_type': meal_type,
                    'food': food_item,
                    'servings': servings,
                    'mood': mood_after,
                    'notes': notes
                }
                st.session_state.nutrition_log.append(entry)
                st.success(f"✅ {meal_type} logged! Great job taking care of yourself! 🌟")
    
    with col2:
        st.markdown("### 📈 Today's Summary")
        if st.session_state.nutrition_log:
            today_meals = [m for m in st.session_state.nutrition_log if m['date'].startswith(datetime.now().strftime("%Y-%m-%d"))]
            st.metric("Meals Logged", len(today_meals))
            if today_meals:
                avg_mood = sum(m['mood'] for m in today_meals) / len(today_meals)
                st.metric("Avg Mood", f"{avg_mood:.1f}/10")
        else:
            st.info("Start logging meals to see your summary!")
    
    # Display recent logs
    if st.session_state.nutrition_log:
        st.markdown("---")
        st.markdown("### 📋 Recent Meals")
        
        for entry in reversed(st.session_state.nutrition_log[-5:]):
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(224,242,241,0.9)); 
                        padding: 15px; border-radius: 10px; margin-bottom: 10px;
                        border-left: 4px solid #26a69a;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <p style="margin: 0; font-weight: 600; color: #2c3e50;">
                            {entry['meal_type']} - {entry['food']} ({entry['servings']} servings)
                        </p>
                        <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">
                            {entry['date']}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <p style="margin: 0; font-size: 18px; font-weight: 600; color: #26a69a;">
                            😊 {entry['mood']}/10
                        </p>
                    </div>
                </div>
                {f'<p style="margin: 10px 0 0 0; font-size: 13px; color: #555; font-style: italic;">{entry["notes"]}</p>' if entry['notes'] else ''}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Nutrition Tips
    st.markdown("## 💡 Nutrition & Mental Health Tips")
    
    tips = [
        ("🥤 Stay Hydrated", "Drink at least 8 glasses of water daily. Dehydration can affect mood and energy."),
        ("⏰ Eat Regular Meals", "Don't skip meals. Regular eating stabilizes blood sugar and mood."),
        ("🌈 Eat the Rainbow", "Different colored foods have different nutrients. Variety is key!"),
        ("🍫 Limit Sugar & Caffeine", "Excessive sugar and caffeine can increase anxiety and mood swings."),
        ("🧘 Mindful Eating", "Eat slowly and without distractions. Notice flavors and textures."),
        ("🥗 Include Omega-3s", "Fish, flaxseeds, and walnuts support brain health and mood."),
        ("🍽️ Portion Control", "Listen to your body's hunger and fullness cues."),
        ("🌱 Choose Whole Foods", "Minimize processed foods. Natural foods are better for mental health."),
    ]
    
    cols = st.columns(2)
    for idx, (tip_title, tip_desc) in enumerate(tips):
        with cols[idx % 2]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(165,214,167,0.3), rgba(128,203,196,0.3)); 
                        padding: 15px; border-radius: 10px; margin-bottom: 15px;
                        border-left: 4px solid #26a69a;">
                <p style="margin: 0 0 8px 0; font-weight: 600; color: #2c3e50; font-size: 15px;">
                    {tip_title}
                </p>
                <p style="margin: 0; font-size: 13px; color: #555;">
                    {tip_desc}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Affirmations
    st.markdown("## 🌟 Daily Affirmations for Wellness")
    
    affirmations = [
        "I am committed to nourishing my body and mind.",
        "Every healthy choice I make is an act of self-love.",
        "I deserve to feel energized and healthy.",
        "My body is strong and capable.",
        "I am building healthy habits that will last a lifetime.",
        "I choose foods that make me feel good.",
        "My wellness journey is unique and valid.",
        "I am proud of the progress I'm making.",
    ]
    
    selected_affirmation = random.choice(affirmations)
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 15px; text-align: center;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
        <p style="color: white; font-size: 20px; font-weight: 600; margin: 0;">
            ✨ {selected_affirmation}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Credible Sources
    st.markdown("## 📚 Research & Sources")
    st.markdown("""
    This page is based on peer-reviewed scientific research and clinical guidelines:
    
    **Key Research Sources:**
    - **Neurology (2018)**: Study on leafy greens and cognitive decline - [NIH/PubMed](https://pmc.ncbi.nlm.nih.gov/articles/PMC5772164/)
    - **Frontiers in Nutrition**: Comprehensive review on nutrition and mental health
    - **American Psychiatric Association (APA)**: Recommends omega-3 supplementation for depression and mental disorders
    - **NIH/NCBI**: Multiple studies on nutrition-psychiatry connection
    - **Frontiers in Neuroscience**: Research on gut-brain axis and probiotics
    
    **Key Findings:**
    - Omega-3 fatty acids show modest but significant benefits for depression (50+ RCTs)
    - Leafy greens consumption linked to 11-year difference in cognitive decline
    - Regular nutrient-rich diet supports mood stability and mental resilience
    - Gut microbiome (probiotics) influences mental health through gut-brain axis
    
    ⚠️ **Disclaimer:** This information is educational and not a substitute for professional medical advice. 
    Always consult with a healthcare provider or registered dietitian for personalized nutrition guidance.
    """)

    next_page_button("🥗 Healthy Nutrition")

# Page: Resources
elif page == "📞 Resources":
    st.title("📞 Mental Health Resources & Support")
    st.markdown("*Comprehensive directory of mental health support services*")
    st.markdown("---")
    
    # Crisis Alert Banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); 
                padding: 25px; border-radius: 15px; margin-bottom: 30px; 
                border-left: 6px solid #7f1d1d; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="color: white; margin: 0 0 15px 0; font-size: 24px;">🆘 IN CRISIS? GET IMMEDIATE HELP</h2>
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px;">
            <p style="color: white; margin: 0; font-size: 18px; font-weight: bold;">🇮🇳 INDIA (24/7)</p>
            <p style="color: white; margin: 5px 0 0 0; font-size: 16px;">
                📞 <strong>1860-2662-345</strong> (Vandrevala Foundation)<br>
                📞 <strong>91-9820466726</strong> (AASRA Mumbai)<br>
                📞 <strong>044-24640050</strong> (Sneha Chennai)
            </p>
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px;">
            <p style="color: white; margin: 0; font-size: 18px; font-weight: bold;">🌍 INTERNATIONAL (24/7)</p>
            <p style="color: white; margin: 5px 0 0 0; font-size: 16px;">
                📞 <strong>988</strong> (USA) | <strong>116 123</strong> (UK) | <strong>13 11 14</strong> (Australia)
            </p>
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
            <p style="color: white; margin: 0; font-size: 18px; font-weight: bold;">🚨 EMERGENCY SERVICES</p>
            <p style="color: white; margin: 5px 0 0 0; font-size: 16px;">
                📞 <strong>112</strong> (India) | <strong>911</strong> (USA) | <strong>999</strong> (UK)
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for better organization
    tab1, tab2, tab3, tab4 = st.tabs(["🇮🇳 India", "🌍 International", "💻 Online Services", "📚 Information"])
    
    with tab1:
        st.markdown("## 🇮🇳 Indian Mental Health Resources")
        
        # Crisis Helplines
        st.markdown("### 🆘 Crisis & Suicide Prevention (24/7)")
        
        crisis_helplines = [
            {"name": "Vandrevala Foundation", "phone": "1860-2662-345 / 1800-2333-330", 
             "hours": "24/7", "lang": "English, Hindi, Regional", "desc": "Mental health support and crisis intervention"},
            {"name": "AASRA (Mumbai)", "phone": "91-9820466726", 
             "hours": "24/7", "lang": "English, Hindi", "desc": "Suicide prevention helpline"},
            {"name": "Sneha Foundation (Chennai)", "phone": "044-24640050", 
             "hours": "24/7", "lang": "English, Tamil, Hindi", "desc": "Suicide prevention center"},
            {"name": "Fortis Stress Helpline", "phone": "8376804102", 
             "hours": "24/7", "lang": "English, Hindi", "desc": "Stress and anxiety support"}
        ]
        
        cols = st.columns(2)
        for idx, helpline in enumerate(crisis_helplines):
            with cols[idx % 2]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); 
                            padding: 20px; border-radius: 12px; margin-bottom: 15px;
                            border-left: 5px solid #dc2626; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h4 style="color: #991b1b; margin: 0 0 10px 0;">{helpline['name']}</h4>
                    <p style="margin: 5px 0; color: #7f1d1d;"><strong>📞 {helpline['phone']}</strong></p>
                    <p style="margin: 5px 0; color: #7f1d1d; font-size: 14px;">🕐 {helpline['hours']}</p>
                    <p style="margin: 5px 0; color: #7f1d1d; font-size: 14px;">🗣️ {helpline['lang']}</p>
                    <p style="margin: 10px 0 0 0; color: #991b1b; font-size: 13px;">{helpline['desc']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Mental Health Support
        st.markdown("### 🧠 Mental Health Support Services")
        
        support_services = [
            {"name": "NIMHANS Helpline (Bangalore)", "phone": "080-46110007", 
             "hours": "Mon-Sat, 9 AM-5:30 PM", "lang": "English, Hindi, Kannada"},
            {"name": "iCall (TISS)", "phone": "9152987821", 
             "hours": "Mon-Sat, 8 AM-10 PM", "lang": "English, Hindi, Marathi"},
            {"name": "Mann Talks", "phone": "8686139139", 
             "hours": "Mon-Sat, 10 AM-6 PM", "lang": "English, Hindi"},
            {"name": "Parivarthan Counselling", "phone": "7676602602", 
             "hours": "Mon-Sat, 10 AM-6 PM", "lang": "English, Hindi, Kannada"}
        ]
        
        cols = st.columns(2)
        for idx, service in enumerate(support_services):
            with cols[idx % 2]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); 
                            padding: 20px; border-radius: 12px; margin-bottom: 15px;
                            border-left: 5px solid #2563eb; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h4 style="color: #1e40af; margin: 0 0 10px 0;">{service['name']}</h4>
                    <p style="margin: 5px 0; color: #1e3a8a;"><strong>📞 {service['phone']}</strong></p>
                    <p style="margin: 5px 0; color: #1e3a8a; font-size: 14px;">🕐 {service['hours']}</p>
                    <p style="margin: 5px 0; color: #1e3a8a; font-size: 14px;">🗣️ {service['lang']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Specialized Support
        st.markdown("### 🎯 Specialized Support")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%); 
                        padding: 20px; border-radius: 12px; border-left: 5px solid #db2777;">
                <h4 style="color: #9f1239; margin: 0 0 10px 0;">👩 Women & Children</h4>
                <p style="margin: 5px 0; color: #831843;"><strong>Women's Helpline:</strong> 1091 / 181</p>
                <p style="margin: 5px 0; color: #831843;"><strong>Childline India:</strong> 1098</p>
                <p style="margin: 5px 0; color: #831843;"><strong>POCSO:</strong> 1098 / 155260</p>
                <p style="margin: 10px 0 0 0; color: #9f1239; font-size: 13px;">24/7 support in all regional languages</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); 
                        padding: 20px; border-radius: 12px; border-left: 5px solid #6366f1;">
                <h4 style="color: #4338ca; margin: 0 0 10px 0;">🎯 Addiction & LGBTQ+</h4>
                <p style="margin: 5px 0; color: #3730a3;"><strong>AA/NA:</strong> 9833583472</p>
                <p style="margin: 5px 0; color: #3730a3;"><strong>Connecting (LGBTQ+):</strong> 9137501393</p>
                <p style="margin: 10px 0 0 0; color: #4338ca; font-size: 13px;">Specialized support services</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("## 🌍 International Resources")
        
        countries = {
            "🇺🇸 United States": [
                {"name": "Suicide & Crisis Lifeline", "contact": "988", "hours": "24/7"},
                {"name": "Crisis Text Line", "contact": "Text HOME to 741741", "hours": "24/7"},
                {"name": "SAMHSA National Helpline", "contact": "1-800-662-4357", "hours": "24/7"}
            ],
            "🇬🇧 United Kingdom": [
                {"name": "Samaritans", "contact": "116 123", "hours": "24/7"},
                {"name": "Mind Infoline", "contact": "0300 123 3393", "hours": "Mon-Fri, 9 AM-6 PM"}
            ],
            "🇦🇺 Australia": [
                {"name": "Lifeline", "contact": "13 11 14", "hours": "24/7"},
                {"name": "Beyond Blue", "contact": "1300 22 4636", "hours": "24/7"}
            ],
            "🇨🇦 Canada": [
                {"name": "Crisis Services Canada", "contact": "1-833-456-4566", "hours": "24/7"}
            ]
        }
        
        for country, helplines in countries.items():
            with st.expander(f"### {country}", expanded=False):
                for helpline in helplines:
                    st.markdown(f"""
                    <div style="background: #f3f4f6; padding: 15px; border-radius: 10px; margin-bottom: 10px;
                                border-left: 4px solid #6b7280;">
                        <h4 style="color: #374151; margin: 0 0 8px 0;">{helpline['name']}</h4>
                        <p style="margin: 3px 0; color: #1f2937;"><strong>📞 {helpline['contact']}</strong></p>
                        <p style="margin: 3px 0; color: #4b5563; font-size: 14px;">🕐 {helpline['hours']}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("## 💻 Online Mental Health Services")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); 
                        padding: 20px; border-radius: 12px; border-left: 5px solid #059669;">
                <h4 style="color: #065f46; margin: 0 0 10px 0;">🎥 Online Therapy</h4>
                <p style="margin: 8px 0; color: #064e3b;">
                    <strong>BetterHelp</strong><br>
                    <span style="font-size: 13px;">Professional online counseling</span><br>
                    <a href="https://betterhelp.com" target="_blank" style="color: #059669;">betterhelp.com</a>
                </p>
                <p style="margin: 8px 0; color: #064e3b;">
                    <strong>Talkspace</strong><br>
                    <span style="font-size: 13px;">Text, audio, video therapy</span><br>
                    <a href="https://talkspace.com" target="_blank" style="color: #059669;">talkspace.com</a>
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
                        padding: 20px; border-radius: 12px; border-left: 5px solid #f59e0b;">
                <h4 style="color: #92400e; margin: 0 0 10px 0;">🤝 Peer Support</h4>
                <p style="margin: 8px 0; color: #78350f;">
                    <strong>7 Cups</strong><br>
                    <span style="font-size: 13px;">Free emotional support</span><br>
                    <a href="https://7cups.com" target="_blank" style="color: #f59e0b;">7cups.com</a>
                </p>
                <p style="margin: 8px 0; color: #78350f;">
                    <strong>NAMI</strong><br>
                    <span style="font-size: 13px;">Mental health organization</span><br>
                    <a href="https://nami.org" target="_blank" style="color: #f59e0b;">nami.org</a>
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("## 📚 Mental Health Information")
        
        st.info("""
        ### 🧠 Understanding Mental Health
        
        Mental health includes our emotional, psychological, and social well-being. It affects how we think, feel, and act.
        
        **Common Mental Health Conditions:**
        - Depression
        - Anxiety Disorders
        - Bipolar Disorder
        - PTSD
        - OCD
        - Eating Disorders
        """)
        
        st.success("""
        ### ✅ When to Seek Help
        
        Consider reaching out if you experience:
        - Persistent sadness or hopelessness
        - Excessive worry or fear
        - Extreme mood changes
        - Withdrawal from activities
        - Changes in sleep or appetite
        - Difficulty concentrating
        - Thoughts of self-harm
        """)
        
        st.warning("""
        ### 💡 Self-Care Tips
        
        - Maintain regular sleep schedule
        - Exercise regularly
        - Eat nutritious meals
        - Practice mindfulness/meditation
        - Stay connected with loved ones
        - Limit alcohol and avoid drugs
        - Seek professional help when needed
        """)
    
    # Age-specific resources
    st.markdown("---")
    if st.session_state.get('user_age'):
        st.markdown("## 🎯 Age-Specific Resources")
        
        if st.session_state.user_age < 18:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fef9c3 0%, #fef08a 100%); 
                        padding: 20px; border-radius: 12px; border-left: 5px solid #eab308;">
                <h4 style="color: #713f12; margin: 0 0 10px 0;">👦 Resources for Teens & Youth</h4>
                <p style="margin: 5px 0; color: #854d0e;"><strong>Teen Line:</strong> Text TEEN to 839863</p>
                <p style="margin: 5px 0; color: #854d0e;"><strong>The Trevor Project (LGBTQ+):</strong> 1-866-488-7386</p>
                <p style="margin: 5px 0; color: #854d0e;"><strong>Boys Town National Hotline:</strong> 1-800-448-3000</p>
            </div>
            """, unsafe_allow_html=True)
        elif st.session_state.user_age >= 65:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); 
                        padding: 20px; border-radius: 12px; border-left: 5px solid #0284c7;">
                <h4 style="color: #075985; margin: 0 0 10px 0;">👴 Resources for Seniors</h4>
                <p style="margin: 5px 0; color: #0c4a6e;"><strong>Eldercare Locator:</strong> 1-800-677-1116</p>
                <p style="margin: 5px 0; color: #0c4a6e;"><strong>Friendship Line:</strong> 1-800-971-0016</p>
                <p style="margin: 5px 0; color: #0c4a6e;"><strong>SAMHSA Aging & Mental Health:</strong> samhsa.gov</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.session_state.nav_to = "🏠 Dashboard"
            st.rerun()

# Footer
st.markdown("---")
st.caption("⚠️ This app is for screening purposes only and does not replace professional medical advice. Always consult with a qualified mental health professional for diagnosis and treatment.")
