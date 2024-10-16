import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load and clean the dataset
df = pd.read_csv("filtered_data.csv")
df['INPUT DATE'] = pd.to_datetime(df['INPUT DATE'],errors='coerce')
df =df[df['INPUT DATE'].dt.year >= 2017]

# Function to format large numbers with dollar sign
def format_large_number(num):
    if abs(num) >= 1_000_000_000:
        return f"${num / 1_000_000_000:.1f}B"  # Format in billions with $
    elif abs(num) >= 1_000_000:
        return f"${num / 1_000_000:.1f}M"  # Format in millions with $
    else:
        return f"${num:,.2f}"  # Default format for smaller numbers with $


# Convert dates and handle missing or erroneous values
df['INPUT DATE'] = pd.to_datetime(df['INPUT DATE'], errors='coerce')
df['ITEM TOTAL COST'] = pd.to_numeric(df['ITEM TOTAL COST'], errors='coerce')

# Fill missing values with appropriate data or 'Unknown'
df['VENDOR NAME 1'] = df['VENDOR NAME 1'].fillna('Unknown Vendor')
df['COMMODITY DESCRIPTION'] = df['COMMODITY DESCRIPTION'].fillna('Unknown Commodity')
df['STATUS'] = df['STATUS'].fillna('Unknown Status')
df['VENDOR STATE'] = df['VENDOR STATE'].fillna('Unknown Region')

# Streamlit Dashboard Title
st.title("Procurement Management Dashboard")

# KPI Section
col1, col2, col3 = st.columns(3)
total_suppliers = df['VENDOR NAME 1'].nunique()
#total_contractors = df['DOCUMENT DESCRIPTION'].nunique()  # Assuming there is a contractor field
total_amount = df['ITEM TOTAL COST'].sum()
total_invoices = len(df)

# Display KPIs
with col1:
    st.metric("Total Suppliers", total_suppliers)
with col2:
    #st.metric("Contractors", total_contractors)
    st.metric("Overall Procurement Expenditure", format_large_number(total_amount))
with col3:
    #st.metric("Overall Procurement Expenditure", f"${total_amount:,.2f}")
    st.metric("Complete Invoice Tally", total_invoices)

# Column Layout for Graphs
col1, col2 = st.columns(2)

# Procurement Charges by Supplier (Pie chart)
supplier_costs = df.groupby('VENDOR NAME 1')['ITEM TOTAL COST'].sum().reset_index().nlargest(10, 'ITEM TOTAL COST')
fig_supplier = px.pie(supplier_costs, names='VENDOR NAME 1', values='ITEM TOTAL COST', 
                      title='Procurement Charges by Supplier',
                      color_discrete_sequence=px.colors.sequential.Plasma)

# Spend Under Management by Commodity (Bar chart)
spend_by_commodity = df.groupby('COMMODITY DESCRIPTION')['ITEM TOTAL COST'].sum().reset_index().nlargest(10, 'ITEM TOTAL COST')
fig_spend = px.bar(spend_by_commodity, x='COMMODITY DESCRIPTION', y='ITEM TOTAL COST', 
                   title='Spend Under Management by Commodity', 
                   color='ITEM TOTAL COST', 
                   color_continuous_scale=px.colors.sequential.Viridis)

# Display Graphs Side by Side
#with col1:
st.plotly_chart(fig_supplier, use_container_width=True)
#with col2:
st.plotly_chart(fig_spend, use_container_width=True)

# Another Row for More Analysis Graphs
col3, col4 = st.columns(2)

# Status-wise Order Overview (Pie chart)
status_count = df['STATUS'].value_counts().reset_index()
status_count.columns = ['STATUS', 'COUNT']
fig_status = px.pie(status_count, names='STATUS', values='COUNT', 
                    title='Status-wise Order Overview',
                    color_discrete_sequence=px.colors.sequential.Sunset)

# Revenue and Expenditure Comparative Analysis (Bar Chart)
monthly_data = df.groupby(df['INPUT DATE'].dt.to_period('M')).agg({'ITEM TOTAL COST': 'sum'}).reset_index()
monthly_data['INPUT DATE'] = monthly_data['INPUT DATE'].dt.to_timestamp()
fig_revenue = px.bar(monthly_data, x='INPUT DATE', y='ITEM TOTAL COST', 
                     title='Revenue and Expenditure Comparative Analysis',
                     color='ITEM TOTAL COST', 
                     color_continuous_scale=px.colors.sequential.Tealgrn)

# Display Next Set of Graphs
with col3:
    st.plotly_chart(fig_status, use_container_width=True)
with col4:
    st.plotly_chart(fig_revenue, use_container_width=True)

# Final Row for Custom Graphs
col5, col6 = st.columns(2)

# Cost Savings Percentage by Region (Example)
region_costs = df.groupby('VENDOR STATE')['ITEM TOTAL COST'].sum().reset_index()  # Assuming 'VENDOR STATE' field exists
fig_savings = px.bar(region_costs, x='VENDOR STATE', y='ITEM TOTAL COST', 
                     title='Cost Savings by Region',
                     color='ITEM TOTAL COST',
                     color_continuous_scale=px.colors.sequential.Magma)

# Inventory Turnover Rate (Assuming 'DEPARTMENT NAME' is present in the data)
inventory_turnover = df.groupby('DEPARTMENT NAME')['ITEM TOTAL COST'].sum().reset_index()
fig_inventory = px.bar(inventory_turnover, x='DEPARTMENT NAME', y='ITEM TOTAL COST',
                       title='Inventory Turnover Rate',
                       color='ITEM TOTAL COST',
                       color_continuous_scale=px.colors.sequential.Burg)

# Display Custom Graphs
with col5:
    st.plotly_chart(fig_savings, use_container_width=True)
with col6:
    st.plotly_chart(fig_inventory, use_container_width=True)

# Additional Insights Section
st.write("### Additional Insights")

# Supplier Dependency Analysis
supplier_dependency = df.groupby('VENDOR NAME 1')['ITEM TOTAL COST'].sum().reset_index().sort_values(by='ITEM TOTAL COST', ascending=False).head(10)

supplier_dependency['Percentage of Total Spend'] = (supplier_dependency['ITEM TOTAL COST'] / total_amount) * 100
fig_dependency = px.bar(supplier_dependency, x='VENDOR NAME 1', y='Percentage of Total Spend',
                        title='Supplier Dependency Analysis', 
                        color='Percentage of Total Spend',
                        color_continuous_scale=px.colors.sequential.Cividis)
st.plotly_chart(fig_dependency, use_container_width=True)

# Spend Over Time by Department
department_spend = df.groupby([df['INPUT DATE'].dt.to_period('M'), 'DEPARTMENT NAME'])['ITEM TOTAL COST'].sum().reset_index()
department_spend['INPUT DATE'] = department_spend['INPUT DATE'].dt.to_timestamp()
fig_department = px.line(department_spend, x='INPUT DATE', y='ITEM TOTAL COST', 
                         color='DEPARTMENT NAME', title='Spend Over Time by Department')
st.plotly_chart(fig_department, use_container_width=True)




# Order Approval vs Rejection Rate
order_status = df['STATUS'].value_counts(normalize=True).reset_index()
order_status.columns = ['STATUS', 'proportion']  # Rename the columns for clarity

# Create the pie chart
fig_approval_rate = px.pie(order_status, names='STATUS', values='proportion', 
                           title='Order Approval vs Rejection Rate', 
                           hole=.4, color_discrete_sequence=px.colors.sequential.Pinkyl)

# Display the pie chart
st.plotly_chart(fig_approval_rate, use_container_width=True)


# Seasonal Procurement Trends
df['Year'] = df['INPUT DATE'].dt.year
df['Month'] = df['INPUT DATE'].dt.month_name()
# Define a categorical order for the months
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']
df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)

seasonal_trends = df.groupby(['Year', 'Month'])['ITEM TOTAL COST'].sum().reset_index()
seasonal_trends = seasonal_trends[seasonal_trends['Year']>=2017].sort_values(['Year', 'Month'])
fig_seasonal = px.density_heatmap(seasonal_trends, x='Month', y='Year', z='ITEM TOTAL COST', 
                                  title='Seasonal Procurement Trends',
                                  color_continuous_scale=px.colors.sequential.Blues)
st.plotly_chart(fig_seasonal, use_container_width=True)



# Footer: Add a note or observation
st.write("### Insights:")
st.write("""

1. Supplier 5 has one of the highest procurement charges, indicating a key supplier relationship.
2. Status-wise order overview shows a significant number of completed orders, reflecting operational efficiency.
3. Revenue and expenditure comparison highlights increasing costs in recent months.
4. Regional procurement cost analysis points to higher expenditures in key regions.
""")
