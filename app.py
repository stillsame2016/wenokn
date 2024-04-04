import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl

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

st.markdown('<p class="big-font">Dive Deep with Easy Queries</p>', unsafe_allow_html=True)

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
  st.write("Chat with WEN-OKN")
