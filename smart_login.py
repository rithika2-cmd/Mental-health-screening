"""
Smart Login System with Intelligent Flow
- First-time users: Show Create Account
- Returning users: Show Login
- Always available: Guest Mode
"""
import streamlit as st
import os
import json
from database import db

def check_if_users_exist():
    """Check if any user accounts exist"""
    try:
        users = db.get_connection().execute("SELECT COUNT(*) FROM users").fetchone()[0]
        return users > 0
    except:
        return False

def show_smart_login():
    """Display smart login interface based on user state"""
    
    # Check if users exist
    users_exist = check_if_users_exist()
    
    # Header
    st.markdown("<h1 style='text-align: center;'>🧠 Mental Health Screening Platform</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px;'>Your journey to better mental wellness starts here</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Smart flow based on whether users exist
    if not users_exist:
        # First-time setup - emphasize account creation
        show_first_time_setup()
    else:
        # Returning users - emphasize login
        show_returning_user_login()

def show_first_time_setup():
    """Show interface for first-time users"""
    
    st.info("👋 Welcome! Let's create your account to get started.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 Create Your Account")
        
        with st.form("create_account_form"):
            full_name = st.text_input("Full Name", placeholder="Enter your full name")
            username = st.text_input("Username", placeholder="Choose a username (min 3 characters)")
            password = st.text_input("Password", type="password", placeholder="Choose a password (min 6 characters)")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
            
            submit = st.form_submit_button("🚀 Create Account & Start", use_container_width=True)
            
            if submit:
                # Validation
                if not full_name or not username or not password:
                    st.error("❌ Please fill in all fields")
                elif len(username) < 3:
                    st.error("❌ Username must be at least 3 characters")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match")
                else:
                    # Create account
                    success, message = db.create_user(username, password, full_name)
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        # Auto-login
                        success, msg, user_id = db.authenticate_user(username, password)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.current_user = username
                            st.session_state.user_id = user_id
                            st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    with col2:
        st.markdown("### ✨ Benefits")
        st.markdown("""
        - 📊 Track your mood daily
        - 📝 Journal your thoughts
        - 📈 View progress over time
        - 🔥 Build streaks
        - 🏆 Earn achievements
        - 💾 Secure data storage
        """)
    
    st.markdown("---")
    
    # Guest mode option
    st.markdown("### 🚪 Or Try Without Account")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Continue as Guest", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.current_user = "guest"
            st.session_state.user_id = None
            st.info("ℹ️ Guest mode: Your data will not be saved permanently")
            st.rerun()

def show_returning_user_login():
    """Show interface for returning users"""
    
    # Create tabs for Login and Create Account
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "👤 Create Account", "🚪 Guest Mode"])
    
    with tab1:
        st.markdown("### Welcome Back!")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("🔓 Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("❌ Please enter username and password")
                else:
                    success, message, user_id = db.authenticate_user(username, password)
                    if success:
                        st.success(f"✅ {message}")
                        st.session_state.authenticated = True
                        st.session_state.current_user = username
                        st.session_state.user_id = user_id
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                        if st.session_state.get('login_attempts', 0) >= 2:
                            st.info("💡 Tip: Try Guest Mode if you don't have an account")
                        st.session_state.login_attempts = st.session_state.get('login_attempts', 0) + 1
    
    with tab2:
        st.markdown("### Create New Account")
        
        with st.form("new_account_form"):
            full_name = st.text_input("Full Name")
            username = st.text_input("Username (min 3 characters)")
            password = st.text_input("Password (min 6 characters)", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            submit = st.form_submit_button("✨ Create Account", use_container_width=True)
            
            if submit:
                if not full_name or not username or not password:
                    st.error("❌ Please fill in all fields")
                elif len(username) < 3:
                    st.error("❌ Username must be at least 3 characters")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match")
                else:
                    success, message = db.create_user(username, password, full_name)
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.info("👉 Now login with your new account in the Login tab")
                    else:
                        st.error(f"❌ {message}")
    
    with tab3:
        st.markdown("### 🚪 Guest Mode")
        st.info("""
        **Guest Mode allows you to:**
        - Try all features without registration
        - Use the app immediately
        - Perfect for demos or one-time use
        
        **Note:** Your data will not be saved permanently in Guest Mode.
        """)
        
        if st.button("🚀 Continue as Guest", use_container_width=True, type="primary"):
            st.session_state.authenticated = True
            st.session_state.current_user = "guest"
            st.session_state.user_id = None
            st.rerun()

def show_user_info_sidebar():
    """Show current user info in sidebar"""
    if st.session_state.get('authenticated'):
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Current User")
        
        if st.session_state.current_user == "guest":
            st.sidebar.info("🚪 Guest Mode")
            st.sidebar.caption("Data not saved permanently")
        else:
            user = db.get_user_by_username(st.session_state.current_user)
            if user:
                st.sidebar.success(f"✅ {user['full_name']}")
                st.sidebar.caption(f"@{st.session_state.current_user}")
                
                # Show streak if available
                if st.session_state.user_id:
                    try:
                        streak_stats = db.get_streak_statistics(st.session_state.user_id)
                        current_streak = streak_stats['combined']['current_streak']
                        if current_streak > 0:
                            st.sidebar.metric("🔥 Current Streak", f"{current_streak} days")
                    except:
                        pass
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.user_id = None
            st.rerun()
