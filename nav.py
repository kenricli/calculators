import streamlit as st


def _hide_default_streamlit_navigation() -> None:
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


def render_sidebar_nav(current_page: str) -> None:
    """Render sidebar navigation buttons for the multipage app."""
    _hide_default_streamlit_navigation()

    with st.sidebar:
        st.title("🧮 Calculator Suite")
        st.caption("Select a calculator below")

        if st.button(
            "🏠 Home",
            use_container_width=True,
            type="primary" if current_page == "home" else "secondary",
            key=f"nav_home_{current_page}",
        ):
            st.switch_page("app.py")

        if st.button(
            "🩺 HAI Pump Calculator",
            use_container_width=True,
            type="primary" if current_page == "hai" else "secondary",
            key=f"nav_hai_{current_page}",
        ):
            st.switch_page("pages/1_HAI_Pump_Calculator.py")

        if st.button(
            "🧪 5-FU Infusion Pump Calculator",
            use_container_width=True,
            type="primary" if current_page == "5fu" else "secondary",
            key=f"nav_5fu_{current_page}",
        ):
            st.switch_page("pages/2_5FU_Infusion_Pump_Calculator.py")

        st.divider()
