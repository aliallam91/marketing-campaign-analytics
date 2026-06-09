import streamlit as st
import os
from data_loader import load_data

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Marketing Campaign Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("d:/Depi Project/style.css")

# Load data
try:
    data_dict = load_data()
    # Store raw data in session state for pages to access
    st.session_state['all_data'] = data_dict
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar Branding (Rounded Rectangle 2/5 Slicer Panel is now on main page, sidebar is navigation only)
st.sidebar.image("d:/Depi Project/assets/Intro_img_1.png", width=120)
st.sidebar.markdown("<h2 style='font-size: 1.2rem; font-weight: 800; color: #50164A; margin-top: 10px; margin-bottom: 2px;'>Analytics Portal</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='height: 2px; background-color: #50164A; margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# Page Definitions using st.Page
intro_page = st.Page("pages/intro.py", title="Overview & Credits", icon="🏠", default=True)
dash1_page = st.Page("pages/dashboard1.py", title="Platform Analytics (Dashboard 1)", icon="📈")
dash2_page = st.Page("pages/dashboard2.py", title="Regional & Asset Analytics (Dashboard 2)", icon="🌍")
pivots_page = st.Page("pages/pivots.py", title="Interactive Pivot Tables", icon="🎛️")
explorer_page = st.Page("pages/data_explorer.py", title="Raw Data Explorer", icon="🔍")

# Initialize and run navigation
pg = st.navigation({
    "Project Info": [intro_page],
    "Visual Dashboards": [dash1_page, dash2_page],
    "Data & Tables": [pivots_page, explorer_page]
})
pg.run()
