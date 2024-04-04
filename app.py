import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl

def wide_space_default():
  st.set_page_config(layout="wide")

wide_space_default()

st.markdown(" <style> div[class^='block-container'] { padding-top: 2rem; } </style> ", 
            unsafe_allow_html=True)

st.markdown("""
<style>
.big-font {
    font-size:20px !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">WEN-OKN: Dive Deep, Made Easy</p>', unsafe_allow_html=True)

config = {
    "version": "v1",
    "config": {
        "mapState": {
            "bearing": 0,
            "latitude": 40.4173,
            "longitude": -82.9071,
            "pitch": 0,
            "zoom": 6,
        }
    },
}

map_1 = KeplerGl(height=400)
map_1.config = config

col1, col2 = st.columns([7, 3])
with col1:
  keplergl_static(map_1)
with col2:
  # if prompt := st.chat_input("What can I help you with?"):
  #  st.write(prompt)
  st.markdown("### Chat Interface")
    
    # Create a container for the chat messages
    chat_container = st.container()
    
    # Function to add a new message to the chat
    def add_message(sender, message):
        with chat_container:
            st.markdown(f"**{sender}:** {message}")

    # Get user input
    user_input = st.text_input("Enter your message", key="user_input")
    
    # Add user message to the chat
    if user_input:
        add_message("User", user_input)
        # Simulate a response from the chat interface
        add_message("Bot", "This is a simulated response from the chat interface.")
        st.text_input("Enter your message", key="user_input", value="")
