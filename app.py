import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl

def wide_space_default():
  st.set_page_config(layout="wide")

wide_space_default()

st.write("Dive Deep with Easy Queries")

map_1 = KeplerGl(height=400)

col1, col2 = st.columns([7, 3])
with col1:
  keplergl_static(map_1)
with col2:
  st.write("Chat with WEN-OKN")
