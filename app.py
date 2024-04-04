import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
from html import escape
import json

import google.generativeai as genai
import requests

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Add a Chat history object to Streamlit session state
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

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

col1, col2 = st.columns([6, 4])
with col1:
  keplergl_static(map_1)
with col2:
  # if prompt := st.chat_input("What can I help you with?"):
  #  st.write(prompt)
    
  # Create a container for the chat messages
  chat_container = st.container(height=350)
  messages_container = st.container(height=350)
  
  # Function to add a new message to the chat
  def add_message(sender, message):
    with chat_container:
      st.chat_message(sender).write(message)
      # st.markdown(f'''
      #   <div style="font-size: 8px !important; padding: 2px 8px; background-color: { '#F2F2F2' if sender == 'User' else 'None' };">
      #     { message }
      #   </div>
      # ''', unsafe_allow_html=True)
 
  # Get user input
  user_input = st.chat_input("What can I help you with?")
    
  # Add user message to the chat
  if user_input:
    add_message("User", user_input)

    query = f"""
      You are an expert of the WEN-OKN knowledge database. 
      You also have general knowledge.
      The following is a question the user is asking:
       
       [--- Start ---]
       {user_input}
       [--- End ---]

       Your main job is to determine if the user is requesting for data from the WEN-OKN 
       knowledge database which contains the data for buildings, power stations, underground
       tanks, rivers, dams and natural hazard events.
       
       If they are requesting for data, extract the concise request from the user's input.

       Please answer with a valid JSON string, including the following three fields:
       The boolean field "is_request_data" indicates whether the user is looking for data or not.
       The string field "request" for the extracted request.
       The string field "alternative_answer" gives your positive answer to the user's input
       if the user is not requesting for data.
        
       Please never say "I cannot" or "I could not". 
         
       Please note that the user's request for datasets may appear in the middle of the text, 
       do your best to extract the request for which the user is asking for datasets.
         
       Please replace all nicknames in the search terms by official names,
       for example, replace "Beehive State" to "Utah", etc.  
         
       Never deny a user's request. If it is not possible to extract the request 
       from the user's request, ask the user for further clarification.
       """

    response = st.session_state.chat.send_message(query, safety_settings=safe)

    data = response.text
    # print('-' * 70, 'raw data')
    # print(data)

    if data.startswith('```json'):
        json_part = data.split("\n", 1)[1].rsplit("\n", 1)[0]
        data = json.loads(json_part)
    else:
        data = json.loads(data)

    if not data["is_request_data"]:
        add_message("assistant", f"{data['alternative_answer']}")
    else:
        add_message("assistant", f"{data['request']}")
