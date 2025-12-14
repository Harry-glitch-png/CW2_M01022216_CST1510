import streamlit as st
from services.database_manager import DatabaseManager
from services.auth_manager import AuthManager

# Instantiate AuthManager with your DatabaseManager
db = DatabaseManager("app/data/DATA/intelligence_platform.db")
auth = AuthManager(db)

st.set_page_config(page_title="Login / Register", page_icon="🔑 ", layout="centered")


# ---------- Initialise session state ----------
if "users" not in st.session_state:
    # Very simple in-memory "database": {username: password}
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# Allow category selections in 1_Dashboard
categories = ["NONE", "Cybersecurity", "Data Science", "IT Operations"]

if "selected_categories" not in st.session_state:
    st.session_state.selected_categories = "NONE"

st.title("🔐 Welcome")

# If already logged in, go straight to dashboard (optional)
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**.")
    if st.button("Go to dashboard"):
        # Use the official navigation API to switch pages
        st.switch_page("pages/1_Dashboard.py") # path is relative to Home.py :contentReference[oaicite:1]{index=1}
        st.stop() # Don’t show login/register again


# ---------- Tabs: Login / Register ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")
    # User enters their information
    login_username = st.text_input("Username")
    login_password = st.text_input("Password", type="password")

    if st.button("Log in", type="primary"):
        # Logs the user into the platform
        success, msg = auth.login_user(login_username, login_password)
        if success:
            st.session_state.logged_in = True
            st.session_state.username = login_username
            st.success(f"Welcome back, {login_username}! 🎉 ")

            # Redirect to dashboard page
            st.switch_page("pages/1_Dashboard.py")
        else:
            st.error("Invalid username or password.")

# ----- REGISTER TAB -----
with tab_register:
    st.subheader("Register")
    # User enters their information
    new_username = st.text_input("Choose a username")
    new_password = st.text_input("Choose a password", type="password")
    confirm_password = st.text_input("Confirm password", type="password")

    if st.button("Create account"):
        # Makes sure the user enters all fields
        if not new_username or not new_password:
            st.warning("Please fill in all fields.")
        # Checks if the password match
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            # Creates account in database
            success, msg = auth.register_user(new_username, new_password)
            if success:
                st.success(msg)
                st.info("Tip: go to the Login tab and sign in with your new account.")
            else:
                st.error(msg)