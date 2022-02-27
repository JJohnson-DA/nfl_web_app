# ---- Main Imports ----
import streamlit as st
import numpy as np
from PIL import Image
import pandas as pd


# ---- Custom imports ----
from multipage import MultiPage
from pages import home, team_stats, quarterbacks


# ---- Page Configuration ----
st.set_page_config(layout="wide", page_title="Explore the NFL", page_icon="🏈")

# ---- Load Apps/Pages ----

# Create an instance of the app
app = MultiPage()

# Add all your application here
app.add_page("Home Page", home.app)
app.add_page("Team Stats", team_stats.app)
app.add_page("Quarterback Stats", quarterbacks.app)

# The main app
app.run()
