import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import plotly.figure_factory as ff

# Suppress warnings
warnings.filterwarnings('ignore')

# Set page configuration
#st.set_page_config(page_title="Superstore Sales Analysis", page_icon=":bar_chart:", layout="wide")

# --- Title ---
st.title("Interactive Superstore Sales Dashboard")
st.markdown("Explore sales trends, regional performance, and product categories.")

# --- File Uploader ---
uploaded_file = st.file_uploader(":file_folder: Upload Your Sales Data (CSV, TXT, XLSX, XLS)", type=["csv", "txt", "xlsx", "xls"])

# --- Data Loading and Preprocessing ---
if uploaded_file is not None:
  filename = uploaded_file.name
  st.write(f"Uploaded file: {filename}")
  try:
      df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
  except UnicodeDecodeError:
      st.error("Error decoding file. Please ensure it's in a compatible format.")
      st.stop()
else:
  df = pd.read_excel("Superstore.xls")

df["Order Date"] = pd.to_datetime(df["Order Date"])
start_date = df["Order Date"].min()
end_date = df["Order Date"].max()

# --- Date Range Selection ---
col1, col2 = st.columns(2)
with col1:
  date1 = pd.to_datetime(st.date_input("Start Date", start_date))
with col2:
  date2 = pd.to_datetime(st.date_input("End Date", end_date))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# --- Sidebar Filters ---
st.sidebar.header("Filter Your Data")
region = st.sidebar.multiselect("Select Region(s)", df["Region"].unique())
if region:
  df = df[df["Region"].isin(region)]

state = st.sidebar.multiselect("Select State(s)", df["State"].unique())
if state:
  df = df[df["State"].isin(state)]

city = st.sidebar.multiselect("Select City(ies)", df["City"].unique())
if city:
  df = df[df["City"].isin(city)]


# --- Category Wise Sales ---
category_df = df.groupby(by=["Category"], as_index=False)["Sales"].sum()
col1, col2 = st.columns(2)
with col1:
  st.subheader("Category wise Sales")
  fig = px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
               template="seaborn")
  st.plotly_chart(fig, use_container_width=True, height=400)  # Increased height for better visibility

with col2:
  st.subheader("Region wise Sales")
  fig = px.pie(df, values="Sales", names="Region", hole=0.5)
  fig.update_traces(text=df["Region"], textposition="outside")
  st.plotly_chart(fig, use_container_width=True)

# --- Expandable Data Views ---
cl1, cl2 = st.columns((2))
with cl1:
  with st.expander("Category View Data"):
      st.write(category_df.style.background_gradient(cmap="Blues"))
      csv = category_df.to_csv(index=False).encode('utf-8')
      st.download_button("Download Category Data", data=csv, file_name="Category.csv", mime="text/csv")

with cl2:
  with st.expander("Region View Data"):
      region_df = df.groupby(by="Region", as_index=False)["Sales"].sum()
      st.write(region_df.style.background_gradient(cmap="Oranges"))
      csv = region_df.to_csv(index=False).encode('utf-8')
      st.download_button("Download Region Data", data=csv, file_name="Region.csv", mime="text/csv")

# --- Time Series Analysis ---
df["month_year"] = df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis of Sales')

linechart = pd.DataFrame(df.groupby(df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Time Series Data"):
  st.write(linechart.T.style.background_gradient(cmap="Blues"))
  csv = linechart.to_csv(index=False).encode("utf-8")
  st.download_button('Download Time Series Data', data=csv, file_name="TimeSeries.csv", mime='text/csv')


# --- Treemap ---
st.subheader("Hierarchical View of Sales using TreeMap")
fig3 = px.treemap(df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"],
                color="Sub-Category")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)


# --- Pie Charts ---
chart1, chart2 = st.columns((2))
with chart1:
  st.subheader('Segment wise Sales')
  fig = px.pie(df, values="Sales", names="Segment", template="plotly_dark")
  fig.update_traces(text=df["Segment"], textposition="inside")
  st.plotly_chart(fig, use_container_width=True)

with chart2:
  st.subheader('Category wise Sales Distribution') # More descriptive title
  fig = px.pie(df, values="Sales", names="Category", template="gridon")
  fig.update_traces(text = df["Category"], textposition = "inside")
  st.plotly_chart(fig,use_container_width=True)


# --- Summary Table and Monthly Sub-Category Sales ---
st.subheader("Month wise Sub-Category Sales Summary")
with st.expander("View Summary Table"):
  df_sample = df.head()[["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
  fig = ff.create_table(df_sample, colorscale="Cividis")
  st.plotly_chart(fig, use_container_width=True)

  st.markdown("Month wise Sub-Category Sales")
  df["month"] = df["Order Date"].dt.month_name()
  sub_category_Year = pd.pivot_table(data=df, values="Sales", index=["Sub-Category"], columns="month")
  st.write(sub_category_Year.style.background_gradient(cmap="Blues"))


# --- Scatter Plot ---
st.subheader("Relationship between Sales and Profit") # Clearer title
data1 = px.scatter(df, x="Sales", y="Profit", size="Quantity", title="Sales vs. Profit",
                labels={"Sales": "Sales Amount", "Profit": "Profit Amount", "Quantity": "Quantity Sold"}) # Improved labels
st.plotly_chart(data1, use_container_width=True)


# --- View Filtered Data ---
with st.expander("View Filtered Data"):
  st.write(df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# --- Download Original Dataset ---
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Filtered Dataset', data=csv, file_name="Filtered_Superstore_Data.csv", mime="text/csv")


# --- Indicate created/modified files during execution ---
created_files = ["Category.csv", "Region.csv", "TimeSeries.csv", "Filtered_Superstore_Data.csv"]
if created_files:
  st.write("**Created/Modified files during execution:**")
  for file_name in created_files:
      st.write(file_name)