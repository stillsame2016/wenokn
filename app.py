import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl

st.write("This is a kepler.gl map in streamlit")

map_1 = KeplerGl(height=400)
keplergl_static(map_1)

map_1 = KeplerGl(height=400)
map_1.add_data(
    data=df, name="cities"
)  # Alternative: KeplerGl(height=400, data={"name": df})

keplergl_static(map_1, center_map=True)
