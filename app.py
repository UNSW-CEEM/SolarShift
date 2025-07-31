import streamlit as st
from PIL import Image
from streamlit_scroll_to_top import scroll_to_here

from graphics.style import change_label_style

from data_processing.data_processing import (
    load_and_preprocess_data,
)
from tabs import tab_control, home_tab, begin_tab, explore_tab, compare_tab, assumptions_and_details_tab

# Get image used as icon in web browser tab.
im = Image.open("images/favicon.png")

# Configure Streamlit page settings
st.set_page_config(page_title="SolarShift", layout="wide", page_icon=im)

st.caption("🔄 SolarShift App – Version 2.0 (Deployed July 2025)")
# Set content width to 90% of browser width
st.html(
    """
    <style>
        .stMainBlockContainer {
            max-width: 90vw;
        }
    </style>
    """)

# Reduce padding around main content
st.markdown(
    """
    <style>
    
    .block-container
    {
        max-width: 1300px;
        padding-top: 0.9rem;
        padding-bottom: 0rem;
        margin-top: 1rem;
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize scroll-to-top functionality
if "scroll_to_top" not in st.session_state:
    st.session_state.scroll_to_top = False

# Execute scroll if flag is set
if st.session_state.scroll_to_top:
    scroll_to_here(0, key="top")
    st.session_state.scroll_to_top = False  # Reset the state after scrolling

# Add space that help tabs bar not get hidden.
st.markdown("<br><br>", unsafe_allow_html=True)

# Define tabs.
tab_names = ["Home", "Begin", "Compare", "Advanced explorer", "Assumptions & details"]

# Create tab navigation bar
tab_control.create(tab_names)

# Load and cache data for performance
data, postcode_df = load_and_preprocess_data() #Modified by Arastoo

# Render tab content based on selection

# Home tab: Introduction and overview
if st.session_state["tab"] == "Home":
    home_tab.render()

# Begin tab: Initial data exploration
if st.session_state["tab"] == "Begin":
    begin_tab.render(data, postcode_df)  # Modified by Arastoo

# Compare tab: Side-by-side system comparison
if st.session_state["tab"] == "Compare":
    compare_tab.render(data)   # Modified by Arastoo

# Advanced explorer tab: Detailed filtering options
if st.session_state["tab"] == "Advanced explorer":
    explore_tab.render(data)    # Modified by Arastoo

# Assumptions & details tab: Technical information
if st.session_state["tab"] == "Assumptions & details":
    assumptions_and_details_tab.render(data)   # Modified by Arastoo

# Apply consistent styling to tab labels
for name in tab_names:
    change_label_style(name, font_size="20px")
