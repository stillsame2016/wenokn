import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
from html import escape
import json

import google.generativeai as genai
import requests
import time

import pandas as pd
from io import StringIO


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

  df = pd.DataFrame(
    {
        "City": ["San Francisco", "San Jose", "Palo Alto"],
        "Latitude": [37.77, 37.33, 37.44],
        "Longitude": [-122.43, -121.89, -122.14],
    }
  )

  map_1.add_data(
    data=df, name="cities"
  ) 
       
  # keplergl_static(map_1)
  map_instance = KeplerGl()
  html_buffer = StringIO()
  map_instance.save_to_html(file_name=html_buffer, force_save=True)
  map_html = html_buffer.getvalue()
  st_keplergl = st.empty()
  st_keplergl.write(map_html, unsafe_allow_html=True)

with col2:
  # if prompt := st.chat_input("What can I help you with?"):
  #  st.write(prompt)
    
  # Create a container for the chat messages
  chat_container = st.container(height=350)
  
  # Function to add a new message to the chat
  def add_message(sender, message, processing=False):
    with chat_container:
      if processing:
        with st.chat_message("assistant"):
          with st.spinner(f"""We're currently processing your request:
                                    **{message}{'' if message.endswith('.') else '.'}**
                              Depending on the complexity of the query and the volume of data, 
                              this may take a moment. We appreciate your patience."""):
                                     
            response = requests.get(f"https://sparcal.sdsc.edu/staging-api/v1/Utility/wenokn?query_text={message}")
            data = response.text.replace('\\n', '\n').replace('\\"', '"').replace('\\t', ' ')
            if data.startswith("\"```sparql"):
              start_index = data.find("```sparql") + len("```sparql")
              end_index = data.find("```", start_index)
              sparql_query = data[start_index:end_index].strip()
            elif data.startswith("\"```code"):
              start_index = data.find("```code") + len("```code")
              end_index = data.find("```", start_index)
              sparql_query = data[start_index:end_index].strip()
            else:
              sparql_query = data
            
            st.code(sparql_query)

            df = pd.DataFrame(
                    {'City': ['Columbus'],
                     'Latitude': [ 39.9612 ],
                     'Longitude': [ -82.9988 ]})

            map_1.add_data(data=df, name='cities')

        
      else: 
         st.chat_message(sender).write(message)
          
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

       Your main job is to determine if the user is requesting for data in the scope of the WEN-OKN 
       knowledge database.
       
       If they are requesting for data in the scope of the WEN-OKN knowledge database, then extract 
       the concise request from the user's input. Rephrase the user's request in a simple and format
       way. Remove all the terms like "Please" etc. Use the format like "Find ...".

       Please answer with a valid JSON string, including the following three fields:
       
       The boolean field "is_request_data" is true if the user is requesting to get data from
       the WEN-OKN knowledge database, otherwise "is_request_data" is false. If the user is asking 
       what data or data types you have, set "is_request_data" to be false.
       
       The string field "request" for the extracted request in the simplest format.
       
       The string field "alternative_answer" gives your positive answer to the user's input
       if the user is not requesting for data. If the user is asking what data or data types you have,
       please answer it based on this description:

       The WEN-OKN knowledge database contains the locations of buildings, power stations 
       and underground storage tanks in Ohio.
        
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
    st.markdown(data)
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
        add_message("assistant", f"{data['request']}", processing=True)
        

