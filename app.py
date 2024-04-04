import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl

st.markdown(" <style> div[class^='block-container'] { padding-top: 2rem; } </style> ", 
            unsafe_allow_html=True)

def wide_space_default():
  st.set_page_config(layout="wide")

wide_space_default()

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
  if prompt := st.chat_input("What can I do for you?"):
    st.write(prompt)
