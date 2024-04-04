import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl

st.write("This is a kepler.gl map in streamlit")

map_1 = KeplerGl(height=400)

col1, col2 = st.columns([3, 1])
with col1:
  keplergl_static(map_1)
