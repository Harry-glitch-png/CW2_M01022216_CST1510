import streamlit as st
from app.data.db import connect_database
from app.data.incidents import get_all_incidents
from app.data.tickets import get_all_tickets
from app.data.datasets import get_all_datasets
from my_app.services.ai_assistant import AIAssistant  # import your wrapper

st.set_page_config(page_title="Gemini API", page_icon="🤖", layout="wide")

# Ensure state keys exist
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

st.subheader("Gemini API")

# Initialise assistant in session state
if "assistant" not in st.session_state:
    st.session_state.assistant = AIAssistant(api_key=st.secrets["GEMINI_API_KEY"])

categories = ["NONE", "Cybersecurity", "Data Science", "IT Operations"]

# Allow user to select a domain
with st.sidebar:
    selected_categories = st.selectbox(
        "Select a domain:",
        categories,
        index=categories.index(st.session_state.get("selected_categories", "NONE")),
        key="selected_categories"
    )

# Domain has not been selected
if st.session_state.selected_categories == "NONE":
    st.write("No domain selected.")
    # Logout button
    with st.sidebar:
        st.divider()
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.info("You have been logged out.")
            st.switch_page("Home.py")
    st.stop() # Prevent user from communicating with the API
else:
    st.write(st.session_state.selected_categories, "assistant") # Display which domain the user has selected

# Display existing messages
for message in st.session_state.assistant.get_history():
    role = "assistant" if message["role"] in ("assistant", "model") else "user"
    with st.chat_message(role):
        st.markdown(message["parts"][0]["text"])

# Show message count
with st.sidebar:
    st.title("💬 Chat Controls")
    st.metric("Messages", len(st.session_state.assistant.get_history()))
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.assistant.clear_history()
        st.rerun()

# User input
prompt = st.chat_input("Say Something")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    # Setup database
    conn = connect_database()
    if 'data_text' not in st.session_state:
        st.session_state.data_text = ""

    if st.session_state.selected_categories == "Cybersecurity":
        df = get_all_incidents(conn)
        st.session_state.data_text = df.to_csv(index=False)
    elif st.session_state.selected_categories == "Data Science":
        df = get_all_datasets(conn)
        st.session_state.data_text = df.to_csv(index=False)
    elif st.session_state.selected_categories == "IT Operations":
        df = get_all_tickets(conn)
        st.session_state.data_text = df.to_csv(index=False)

    # Send to assistant
    reply = st.session_state.assistant.send_message(
        user_message=prompt,
        category=st.session_state.selected_categories,
        data_text=st.session_state.data_text
    )

    # Display assistant reply
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.rerun()

# Logout button
with st.sidebar:
    st.divider()
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.info("You have been logged out.")
        st.switch_page("Home.py")