import streamlit as st
from forms.contact import contact_form

# --- HERO SECTION ---
col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
with col1:
  st.image("./assets/profile_image.png", width=280)

with col2:
  st.title("Ashik Talupula", anchor=False)
  st.write(
      "Data Scientist / Supply Chain Analyst, assisting enterprises by supporting data-driven decision-making."
  )
  if st.button("Contact Me"):
      st.write("📧 [ashikhits3192@gmail.com]")
      st.write("📞 [Call me](tel:+46761728650)")

# --- ABOUT ME SECTION ---
st.write("\n")
st.subheader("About Me", anchor=False)
st.write(
  """
  With over **5 years of dedicated experience** in the field of supply chain management, I specialize in optimizing processes and enhancing demand forecasting to drive efficiency and growth. My journey has equipped me with a robust skill set that combines analytical prowess with practical implementation.

  ### My Expertise
  - **Supply Chain Optimization**: I have successfully streamlined supply chain processes, ensuring that operations run smoothly and efficiently. My focus is on identifying bottlenecks and implementing solutions that enhance overall productivity.
  
  - **Data-Driven Decision Making**: I am passionate about leveraging data to inform strategic decisions. By designing intuitive dashboards, I track and monitor key performance indicators (KPIs) for procurement and production, providing stakeholders with actionable insights.
  
  - **Innovative Forecasting Models**: I have played a pivotal role in the implementation and testing of new forecasting models. My hands-on approach allows me to identify and resolve issues during development, ensuring that the models are robust and reliable.
  
  - **Customer Insights**: By analyzing trends in existing customer data, I have successfully increased our customer base. Understanding customer behavior and preferences is key to driving engagement and loyalty.

  ### My Vision
  I believe that effective supply chain management is not just about logistics; it’s about creating a seamless experience for customers and stakeholders alike. I am committed to continuous improvement and innovation, always seeking new ways to enhance processes and deliver value.
  """
)

# --- EXPERIENCE & QUALIFICATIONS ---
st.write("\n")
st.subheader("Experience & Qualifications", anchor=False)
st.write(
  """
  - 5 years of experience in optimizing supply chain processes and demand forecasting.
  - Designed dashboards to track and monitor KPIs for procurement and production.
  - Assisted in implementing and testing new forecasting models, resolving issues during development.
  - Increased customer base by analyzing trends in existing customer data.
  """
)

# --- TECHNICAL SKILLS ---
st.write("\n")
st.subheader("Hard Skills", anchor=False)
st.write(
  """
  - **Programming & Tools:** Python, SQL, PySpark, Databricks, Azure, AWS, Dash, Plotly, Power BI, GitHub
  - **Forecasting & Analysis:** XGBoost, Facebook Prophet, RandomForest Regressor, Predictive Modeling, Optimization, Neural Networks
  - **Supply Chain & Logistics:** Demand Forecasting, Workforce Optimization, Inventory Management, S&OP Processes, Sustainability in Supply Chains
  - **Visualization:** Power BI, Tableau, Plotly, Dash
  """
)
