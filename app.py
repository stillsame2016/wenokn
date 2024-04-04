import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl

st.write("Complex Research, Made Easy")

map_1 = KeplerGl(height=400)

col1, col2 = st.columns([3, 1])
with col1:
  keplergl_static(map_1)
with col2:
  st.write("Chat with WEN-OKN")
