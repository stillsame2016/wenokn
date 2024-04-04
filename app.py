import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
from html import escape

import google.generativeai as genai
import requests

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

safe = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

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

# st.markdown('<p class="big-font">WEN-OKN: Dive Deep, Made Easy</p>', unsafe_allow_html=True)
st.markdown("### WEN-OKN: Dive Deep, Made Easy")

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
    
  # Create a container for the chat messages
  chat_container = st.container()
  messages_container = st.container(height=350)
  
  # Function to add a new message to the chat
  def add_message(sender, message):
    with messages_container:
      # st.chat_message(sender).write(message)
      st.markdown(f'''
        <div style="font-size: 8px !important; padding: 2px 8px; background-color: { '#F2F2F2' if sender == 'User' else 'None' };">
          { message }
        </div>
      ''', unsafe_allow_html=True)
 
  # Get user input
  user_input = st.chat_input("What can I help you with?")
    
  # Add user message to the chat
  if user_input:
    add_message("User", user_input)

    
    add_message("assistant", f"echo {user_input}")
