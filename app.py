import json
import re
import time
import uuid
import requests

import pandas as pd
import streamlit as st
import numpy as np

from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
from html import escape

import google.generativeai as genai
import sparql_dataframe
import geopandas as gpd
from shapely import wkt

import traceback

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Add a Chat history object to Streamlit session state
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "wen_datasets" not in st.session_state:
    st.session_state.wen_datasets = []

if "sparqls" not in st.session_state:
    st.session_state.requests = []
    st.session_state.sparqls = []
    
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
  st.set_page_config(layout="wide", page_title="WEN-OKN")

def get_column_name_parts(column_name):
    return re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', column_name)
    
def df_to_gdf(df):
  column_names = df.columns.tolist()
  geometry_column_names = [ x for x in column_names if x.endswith('Geometry')]
  df['geometry'] = df[geometry_column_names[0]].apply(wkt.loads)
  gdf = gpd.GeoDataFrame(df, geometry='geometry')
  gdf.drop(columns=[geometry_column_names[0]], inplace=True)
  
  column_name_parts = get_column_name_parts(column_names[0])
  column_name_parts.pop()
  gdf.attrs['data_name'] = " ".join(column_name_parts).capitalize()
  
  for column_name in column_names:
    tmp_column_name_parts = get_column_name_parts(column_name)
    tmp_name = tmp_column_name_parts.pop()  
    tmp_data_name = " ".join(column_name_parts).capitalize()
    if gdf.attrs['data_name'] == tmp_data_name:
      gdf.rename(columns={column_name: tmp_name}, inplace=True)
  # if tmp_data_name == gdf.attrs['data_name']:
  #     gdf.rename(columns={column_name: name}, inplace=True)
  return gdf


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

# st.markdown('<p class="big-font">WEN-OKN: Dive into Data with Ease</p>', unsafe_allow_html=True)
st.markdown("### WEN-OKN: Dive into Data, Never Easier")

config = {
    "version": "v1",
    "config": {
        "mapState": {
            "bearing": 0,
            "latitude": 40.4173,
            "longitude": -82.9071,
            "pitch": 0,
            "zoom": 6,
        },
        "visState": {
          'layerBlending': "additive",
        }
    },
}

map_1 = KeplerGl(height=400)
map_1.config = config

if st.session_state.wen_datasets:
  for idx, df in enumerate(st.session_state.wen_datasets):
    # data_name = df.attrs['data_name']
    # map_1.add_data(data=df, name=f'{data_name}_{idx}')
    data_name = st.session_state.requests[idx] 
    map_1.add_data(data=df, name=f'{data_name}')
    if df.shape[0] > 0:
        minx, miny, maxx, maxy = df.total_bounds
        config['config']['mapState']['latitude'] = (miny + maxy) /2
        config['config']['mapState']['longitude'] = (minx + maxx) /2
        config['config']['mapState']['zoom'] = 5
    

col1, col2 = st.columns([6, 4])

info_container = st.container(height=350)
with info_container:
  for idx, sparql in enumerate(st.session_state.sparqls): 
    st.markdown(f"**Request:**  {st.session_state.requests[idx]}")
    st.code(sparql)

with col1:  
  keplergl_static(map_1) 

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
            max_tries = 5
            tried = 0
            gdf_empty = False
            while tried < max_tries:
              try:
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
                  elif data.startswith("\"```"):
                    start_index = data.find("```") + len("```")
                    end_index = data.find("```", start_index)
                    sparql_query = data[start_index:end_index].strip()
                  elif data.startswith('"') and data.endswith('"'):
                    # Remove leading and trailing double quotes
                    sparql_query = data[1:-1]
                  else:
                    sparql_query = data
                  sparql_query = sparql_query.replace("\n\n\n", "\n\n")
                  
                  st.markdown(
                      """
                      <style>
                      .st-code > pre {
                          font-size: 0.4em; 
                      }
                      </style>
                      """,
                      unsafe_allow_html=True
                    )
                  st.code(sparql_query)
                  
                  endpoint = "http://132.249.238.155/repositories/wenokn_ohio_all"
                  df = sparql_dataframe.get(endpoint, sparql_query)   
                  
                  gdf = df_to_gdf(df)
                  if gdf.shape[0] == 0:
                    # double check
                    if not gdf_empty:
                      gdf_empty = True
                      tried += 1
                      continue

                  tried = max_tries + 10
                  st.session_state.requests.append(message)
                  st.session_state.sparqls.append(sparql_query)
                  st.session_state.wen_datasets.append(gdf)  
                  st.rerun()
              except Exception as e:
                st.markdown(f"Encounter an error: {str(e)}. Try again...")
                traceback.print_exc()
                tried += 1               
            if tried == max_tries:
              st.markdown("We are not able to process your request at this moment. You can try it again now or later.")
        
      else: 
         st.chat_message(sender).write(message)

  for message in st.session_state.chat.history:
    with chat_container:
      with st.chat_message("assistant" if message.role == "model" else message.role):
        if message.role == 'user':
          prompt = message.parts[0].text
          start_index = prompt.find("[--- Start ---]") + len("[--- Start ---]")
          end_index = prompt.find("[--- End ---]")
          prompt = prompt[start_index:end_index].strip()
          st.markdown(prompt)
        else:
          answer = message.parts[0].text
          if answer.startswith('```json'):
            json_part = answer.split("\n", 1)[1].rsplit("\n", 1)[0]
            data = json.loads(json_part)
          else:
            data = json.loads(answer)

          if isinstance(data, dict):
            if not data["is_request_data"]:
              assistant_response = data["alternative_answer"]
            else:
              assistant_response = "Your request has been processed.."
            st.markdown(assistant_response)
    
  # Get user input
  user_input = st.chat_input("What can I help you with?")
    
  # Add user message to the chat
  if user_input:
    add_message("User", user_input)

    query = f"""
      You are an expert of the WEN-OKN knowledge database. You also have general knowledge.
      
      The following is a question the user is asking:
       
       [--- Start ---]
       {user_input}
       [--- End ---]

       Your main job is to determine if the user is requesting for data in the scope of the WEN-OKN 
       knowledge database.
       
       If they are requesting for data in the scope of the WEN-OKN knowledge database, then extract 
       the request from the user's input. Rephrase the user's request in a formal way. Remove all 
       adjectives like "beautiful" or "pretty". Remove the terms like "Please" etc. Use the format 
       like "Find ...". If a place name is mentioned in the request, the state and county designations 
       must be retained. If a place name may be both a county or a state, the state is taken.

       Please answer with a valid JSON string, including the following three fields:
       
       The boolean field "is_request_data" is true if the user is requesting to get data from
       the WEN-OKN knowledge database, otherwise "is_request_data" is false. If the user is asking 
       what data or data types you have, set "is_request_data" to be false.
       
       The string field "request" for the extracted request. The number of the entities the user is 
       asking for must be included in the "request".
       
       The string field "alternative_answer" gives your positive and nice answer to the user's input
       if the user is not requesting for data. If the user is asking what data or data types you have,
       please answer it by summarizing this description:

       The WEN-OKN knowledge database contains the following:
          1. Locations of buildings, power stations and underground storage tanks in Ohio.
          2. USA counties and their geometries.
          3. USA states and their geometries.
          4. Earthquakes.
          5. Rivers.
          6. Dams.
          7. Drought zones in 2020, 2021 and 2022.
          8. Hospitals
           
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
    # st.markdown(data)
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
        
