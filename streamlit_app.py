import streamlit as st
import warnings
from PIL import Image
import base64

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
project_3_page = st.Page(
    "pages/procurement.py",
    title="Procurement Analysis",
    icon=":material/shopping_cart:",
)


#st.sidebar.image("assets/logo.png", width=150)
#st.sidebar.markdown("---")

# --- NAVIGATION SETUP ---
def add_logo():
  # Load and encode the logo image
  LOGO_IMAGE = "assets/logo.png"
  with open(LOGO_IMAGE, "rb") as image_file:
      encoded_logo = base64.b64encode(image_file.read()).decode()

  # Inject CSS to style the sidebar
  st.markdown(
      f"""
      <style>
          [data-testid="stSidebarNav"] {{
              background-image: url(data:image/png;base64,{encoded_logo});
              background-repeat: no-repeat;
              background-size: 250px 100px;  /* Adjust the size of the logo */
              padding-top: 150px;  /* Adjust this value based on your logo size */
              background-position: 10px 10px;  /* Adjust position as needed */
          }}
          [data-testid="stSidebarNav"]::before {{
              margin-left: 20px;
              margin-top: 20px;
              font-size: 14px;  /* Adjust font size */
              color: #f9a01b;  /* Adjust text color */
              position: relative;
              top: 100px;  /* Adjust this value based on your layout */
          }}
      </style>
      """,
      unsafe_allow_html=True,
  )

# Call the function to add the logo
add_logo()

#st.logo("assets/logo.png", size="large",icon_image="assets/logo1.png")  # Adjust width as needed



pg = st.navigation(
    {
        "Info": [about_page],
        "Projects": [project_3_page,project_1_page, project_2_page],
    }
)

# --- SHARED ON ALL PAGES ---
#st.sidebar.markdown("Made with ❤️ by [Ashik]")

# --- RUN NAVIGATION ---
pg.run()
