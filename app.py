import streamlit as st
from nav import render_sidebar_nav

st.set_page_config(
    page_title="Infusion Pump Calculators",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
    <style>
        section[data-testid="stSidebarNav"] {
            display: none;
        }
        div[data-testid="collapsedControl"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

render_sidebar_nav("home")

st.title("🩺 Infusion Pump Calculator Suite")
st.write("Use the sidebar buttons to open the calculator you need.")

st.markdown("### Available tools")
st.markdown(
    """
    **🩺 HAI Pump Calculator**  
    Calculates FUDR dose and compounding components for a 28-day cycle.

    **🧪 5-FU Infusion Pump Calculator**  
    Calculates overfill-related dose, concentration, and compounding volumes.
    """
)

st.info("Choose a calculator from the left sidebar to begin.")
