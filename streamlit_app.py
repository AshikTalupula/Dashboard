import streamlit as st
import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", message="missing ScriptRunContext!")

# --- PAGE SETUP ---
about_page = st.Page(
    "pages/about_me.py",
    title="About Me",
    icon=":material/account_circle:",
    default=True,
)
project_1_page = st.Page(
    "pages/sales_dashboard.py",
    title="Sales Dashboard",
    icon=":material/bar_chart:",
)
project_2_page = st.Page(
    "pages/supplychain.py",
    title="Supply Chain Analysis",
    icon=":material/smart_toy:",
)

# --- NAVIGATION SETUP ---
pg = st.navigation(
    {
        "Info": [about_page],
        "Projects": [project_1_page, project_2_page],
    }
)

# --- SHARED ON ALL PAGES ---
#st.sidebar.image("assets/logo.png", use_column_width=True)
st.sidebar.markdown("Made with ❤️ by [Ashik]")

# --- RUN NAVIGATION ---
pg.run()
