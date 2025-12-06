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

with st.sidebar:
    selected_categories = st.selectbox(
        "Select a domain:",
        categories,
        index=categories.index(st.session_state.get("selected_categories", "NONE")),
        key="selected_categories"
    )

if st.session_state.selected_categories == "NONE":
    st.write("No domain selected.")
    st.stop()
else:
    st.write(st.session_state.selected_categories, "assistant")

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


# import streamlit as st
# from google import genai
# from google.genai import types
# from app.data.db import connect_database
# from app.data.incidents import get_all_incidents
# from app.data.tickets import get_all_tickets
# from app.data.datasets import get_all_datasets
#
# st.set_page_config(page_title="Gemini API", page_icon="🤖 ",
# layout="wide")
#
# # st.write("DEBUG:", st.session_state)
#
# # Ensure state keys exist
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
# if "username" not in st.session_state:
#     st.session_state.username = ""
#
# # Guard: if not logged in, send user back
# if not st.session_state.logged_in:
#     st.error("You must be logged in to view the dashboard.")
#     if st.button("Go to login page"):
#         st.switch_page("Home.py") # back to the first page
#     st.stop()
#
# st.subheader("Gemini API")
#
# client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
#
# categories = ["NONE", "Cybersecurity", "Data Science", "IT Operations"]
#
# with st.sidebar:
#     selected_categories = st.selectbox(
#         "Select a domain:",
#         categories,
#         index=categories.index(st.session_state.get("selected_categories", "NONE")),
#         key="selected_categories"
#     )
#
# # Insure a domain has been selected
# if st.session_state.selected_categories == "NONE":
#     st.write("No domain selected.")
#     st.stop()
# else:
#     st.write(st.session_state.selected_categories, "assistant")
#
# # Initialise session state
# if 'messages' not in st.session_state:
#     st.session_state.messages = []
#
#
# # Display existing messages
# for message in st.session_state.messages:
#     if message["role"] == "model":
#         role = "assistant"
#     else:
#         role = message["role"]
#     with st.chat_message(role):
#         st.markdown(message["parts"][0]["text"])
#
# # Show message count
# with st.sidebar:
#     st.title("💬 Chat Controls")
#
#     # Show message count
#     message_count = len(st.session_state.get("messages", []))
#     st.metric("Messages", message_count)
#
#     # Clear chat button
#     if st.button("🗑️ Clear Chat", use_container_width=True):
#         # Reset messages to initial state
#         st.session_state.messages = []
#         # Rerun to refresh the interface
#         st.rerun()
#
# # User input
# prompt = st.chat_input("Say Something")
#
# if prompt:
#
#     # Display user message
#     with st.chat_message("user"):
#         st.markdown(prompt)
#
#     # Save user message
#     st.session_state.messages.append({
#         "role": "user",
#         "parts": [{"text": prompt}]
#     })
#
#     # Setup database
#     conn = connect_database()
#
#     if 'data_text' not in st.session_state:
#         st.session_state.data_text = ""
#
#     # Get data table for Gemini
#     if st.session_state.selected_categories == "NONE":
#         st.session_state.data_text = "As user to select a category (Cybersecurity, Data Science or IT Operations)."
#     elif st.session_state.selected_categories == "Cybersecurity":
#         df = get_all_incidents(conn)
#         st.session_state.data_text = df.to_csv(index=False) # To convert the Pandas tabel to text so that Gemini can read it
#     elif st.session_state.selected_categories == "Data Science":
#         df = get_all_datasets(conn)
#         st.session_state.data_text = df.to_csv(index=False)
#     elif st.session_state.selected_categories == "IT Operations":
#         df = get_all_tickets(conn)
#         st.session_state.data_text = df.to_csv(index=False)
#
#     # Send to Gemini
#     category = st.session_state.get("selected_categories", "NONE")
#     response = client.models.generate_content_stream(
#         model = "gemini-3-pro-preview",
#         config = types.GenerateContentConfig(
#             system_instruction = f"You are an {category} data analysis. Your name is Gem."),
#         contents = [
#             *st.session_state.messages,
#             {"role": "user", "parts": [{"text": f"Here is the {category} table:\n{st.session_state.data_text}"}]}
#         ]
#     )
#
#     # Display streaming assistant output
#     with st.chat_message("assistant"):
#         container = st.empty()
#         full_reply = ""
#         for chunk in response:
#             full_reply += chunk.text
#             container.markdown(full_reply)
#
#     # Save assistant message
#     st.session_state.messages.append({"role": "model", "parts": [{"text": full_reply}]})
#     st.rerun()