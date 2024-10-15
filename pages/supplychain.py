import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
from datetime import timedelta

# Applying Plotly theme
# pio.templates.default = 'plotly_white'

# --- Helper Functions (from preprocessor.py) ---

def update_delivery_date(row):
  """
  Update the delivery date based on the shipping mode and market.
  """
  days_to_add = 0

  # Define minimum and maximum days for each shipping mode
  min_days = {
      'First Class': 2,
      'Second Class': 5,
      'Standard Class': 8
  }
  max_days = {
      'First Class': 3,
      'Second Class': 6,
      'Standard Class': 11
  }

  # Check market and shipping mode
  if row['market'] in ['LATAM', 'USCA']:
      if row['shipping_mode'] in min_days:
          days_to_add = min_days[row['shipping_mode']]
  elif row['market'] == 'Pacific Asia':
      if row['shipping_mode'] in max_days:
          days_to_add = max_days[row['shipping_mode']]
  else:
      # Randomly add days based on shipping mode
      if row['shipping_mode'] == 'First Class':
          days_to_add = np.random.randint(2, 4)
      elif row['shipping_mode'] == 'Second Class':
          days_to_add = np.random.randint(5, 7)
      elif row['shipping_mode'] == 'Standard Class':
          days_to_add = np.random.randint(8, 12)

  # Update the delivery date
  return row['delivery_date'] + timedelta(days=days_to_add)

def calculate_product_profit(df):
  """
  Calculate the profit for each product based on its price and a fluctuating profit percentage.
  """
  min_price = df['product_price'].min()
  max_price = df['product_price'].max()
  
  # Define initial and maximum profit percentages
  min_profit_percentage = 0.03
  max_profit_percentage = 0.30
  
  # Calculate the linear profit percentage for each price
  linear_profit_percentage = min_profit_percentage + (max_profit_percentage - min_profit_percentage) * (
      (df['product_price'] - min_price) / (max_price - min_price))
  
  # Add random fluctuation
  np.random.seed(0)  # For reproducibility
  fluctuation = np.random.uniform(-0.20, 0.20, size=df.shape[0])  # Random fluctuation between -20% and +20%
  
  # Adding randomness to product price to introduce variability in the lower values
  random_price_fluctuation = np.random.uniform(-0.05, 0.05, size=df.shape[0])
  df['product_price'] = df['product_price'] * (1 + random_price_fluctuation)
  
  # Adjust profit percentage with the added fluctuation
  df['profit_percentage'] = np.clip(linear_profit_percentage + fluctuation, min_profit_percentage, max_profit_percentage)
  
  # Calculate the profit based on the adjusted price and profit percentage
  df['product_profit'] = df['product_price'] * df['profit_percentage']
  
  # Drop the intermediate 'profit_percentage' column if not needed
  df.drop(columns=['profit_percentage'], inplace=True)
  
  return df['product_profit']

def preprocess():
  """
  Load and preprocess the data from a CSV file.
  """
  # Load data from CSV
  df = pd.read_csv('data.csv')

  # Drop rows with specific customer state
  drop = df[df['customer_state'] == '91732'].index
  df.drop(drop, inplace=True)

  # Convert order_date to datetime
  df['order_date'] = pd.to_datetime(df['order_date'], utc=True)
  df = df.dropna(subset=['order_date'])
  df['order_date'] = df['order_date'].dt.tz_localize(None)

  # Map customer states to full names
  state_mapping = {
      'PR': 'Puerto Rico', 'CA': 'California', 'KY': 'Kentucky', 'NJ': 'New Jersey', 'AZ': 'Arizona', 
      'PA': 'Pennsylvania', 'NY': 'New York', 'OH': 'Ohio', 'CO': 'Colorado', 'MT': 'Montana', 
      'WI': 'Wisconsin', 'IL': 'Illinois', 'DC': 'District of Columbia', 'CT': 'Connecticut', 
      'WV': 'West Virginia', 'UT': 'Utah', 'FL': 'Florida', 'TX': 'Texas', 'MI': 'Michigan', 
      'NM': 'New Mexico', 'NV': 'Nevada', 'WA': 'Washington', 'NC': 'North Carolina', 'GA': 'Georgia', 
      'MD': 'Maryland', 'SC': 'South Carolina', 'TN': 'Tennessee', 'IN': 'Indiana', 'MO': 'Missouri', 
      'MN': 'Minnesota', 'OR': 'Oregon', 'VA': 'Virginia', 'MA': 'Massachusetts', 'HI': 'Hawaii', 
      'RI': 'Rhode Island', 'DE': 'Delaware', 'ID': 'Idaho', 'LA': 'Louisiana', 'ND': 'North Dakota', 
      'KS': 'Kansas', 'IA': 'Iowa', 'OK': 'Oklahoma', 'AL': 'Alabama'
  }

  # Map states
  df['customer_state'] = df['customer_state'].map(state_mapping)
  df['delivery_date'] = df['order_date']
  df['delivery_date'] = df.apply(update_delivery_date, axis=1)

  # Adjust delivery dates for 'Same Day' shipping mode
  temp_df = df[df['shipping_mode'] == 'Same Day']
  num_rows_to_modify = int(len(temp_df) * 0.08)
  num_rows_to_modify2 = int(len(temp_df) * 0.02)
  random_indices = np.random.choice(temp_df.index, num_rows_to_modify, replace=False)
  random_indices2 = np.random.choice(temp_df.index, num_rows_to_modify2, replace=False)
  temp_df.loc[random_indices, 'delivery_date'] += pd.Timedelta(days=1)
  temp_df.loc[random_indices2, 'delivery_date'] += pd.Timedelta(days=2)
  df.loc[df['shipping_mode'] == 'Same Day', 'delivery_date'] = temp_df['delivery_date']
  
  # Calculate shipping duration
  df['shipping_duration'] = (df['delivery_date'] - df['order_date']).dt.days

  # Add order weekday
  df['order_weekday'] = df['order_date'].dt.day_name()

  # Adjust weekdays for specific conditions
  for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday']:
      temp_df = df[df['order_weekday'] == weekday]
      temp_df.iloc[:200, temp_df.columns.get_loc('order_weekday')] = 'Saturday' if weekday in ['Monday', 'Tuesday'] else 'Sunday'
      df[df['order_weekday'] == weekday] = temp_df

  # Calculate product profit
  df['product_profit'] = calculate_product_profit(df)

  return df

# --- Functions from summary.py ---

def getSummary(df):
  """
  Display summary analysis of the data.
  """
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Marketwise Orders Distribution
      </h2>""", unsafe_allow_html=True)
  st.write("Most of the Orders are placed from Europe and LATAM (a group of 33 countries in Latin America and the Caribbean).")
  
  # Market distribution
  market_count = df['market'].value_counts()
  fig = go.Figure([go.Pie(labels=market_count.index, values=market_count.values)])
  fig.update_layout()
  st.plotly_chart(fig)

  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Top Product Categories by Orders
      </h2>""", unsafe_allow_html=True)
  st.write("Most of the Orders are placed for Shoes and Women's Clothing.")
  
  # Top product categories
  category_count = df['category_name'].value_counts().head(10)
  fig = go.Figure([go.Bar(x=category_count.index, y=category_count.values)])
  fig.update_layout(xaxis_title='Category', yaxis_title='Count')
  st.plotly_chart(fig)

def overallcards(df):
  """
  Display key metrics summary in card format.
  """
  st.write("")
  st.title("Business Overview Dashboard")

  st.markdown(""" <h2 style="font-size: 34px; font-weight: bold; color: #E0FFFF;">
          Key Metrics Summary
      </h2>""", unsafe_allow_html=True)
  
  # Calculate key metrics
  totalcustomers = len(df['customer_id'].unique())
  totalorders = len(df)
  totalsales = df['sales'].sum() / 1_000_000  # Convert to millions
  totalprofit = df['order_profit_per_order'].sum() / 1_000
  totalmarkets = len(df['market'].unique())
  totalproducts = len(df['product_name'].unique())

  variables = [
      ("Customers", totalcustomers),
      ("Orders", totalorders),
      ("Sales", f"${totalsales:.2f}M"),  # Format sales in millions
      ("Profit", f"${totalprofit:.2f}K"),  # Format profit in thousands
      ("Markets", totalmarkets),
      ("Products", totalproducts)
  ]

  # Create rows of cards with 3 cards per row
  for i in range(0, len(variables), 3):
      cols = st.columns(3)  # Create a row with 3 columns
      for j in range(3):
          if i + j < len(variables):
              title, value = variables[i + j]
              
              # Add card to the current column
              cols[j].markdown(
                  f"""
                  <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; margin-bottom:20px; text-align:center; box-shadow: 1px 1px 8px rgba(0, 0, 0, 0.3);">
                      <h3 style="color:#333;">{title}</h3>
                      <p style="font-size:24px; font-weight:bold; color: #636efa;">{value}</p>
                  </div>
                  """, 
                  unsafe_allow_html=True
              )

def orderStatusCount(df):
  """
  Display the count of different order statuses.
  """
  st.write("")
  st.write("")
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Order Status Count
      </h2>""", unsafe_allow_html=True)
  st.write("Most of the Orders are completed successfully.")
  
  # Count of order statuses
  order_status_count = df['order_status'].value_counts().reset_index()
  fig = px.bar(order_status_count, x='count', y='order_status')
  st.plotly_chart(fig)

def salesTrend(df):
  """
  Display the sales trend over time.
  """
  st.write("")
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Sales Trend Over Time
      </h2>""", unsafe_allow_html=True)
  st.write("The sales increase in summer but not increasing during the overall number of years.")
  
  # Group sales by order date
  df['order_date'] = pd.to_datetime(df['order_date'])
  sales_trend = df.groupby('order_date')['sales'].sum().reset_index()
  fig = px.line(sales_trend, x='order_date', y='sales')
  st.plotly_chart(fig)

def productPriceByShippingMode(df):
  """
  Display product prices by shipping mode.
  """
  st.write("")
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Product Price by Shipping Mode
      </h2>""", unsafe_allow_html=True)
  st.write("There is no significant difference in product price based on shipping mode.")
  
  # Box plot of product prices by shipping mode
  fig = px.box(df, x='shipping_mode', y='order_item_product_price')
  st.plotly_chart(fig)

def paymentTypeDistribution(df):
  """
  Display the distribution of payment types.
  """
  st.write("")
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Payment Type Distribution
      </h2>""", unsafe_allow_html=True)
  
  # Count of payment types
  payment_type_count = df['payment_type'].value_counts().reset_index()
  fig = px.pie(payment_type_count, values='count', names='payment_type')
  st.plotly_chart(fig)

# --- Functions from customer.py ---

def get_citywise(df):
  """
  Display the number of customers by city.
  """
  st.write("")
  city_wise_customer = df.groupby('order_city')['customer_id'].count().reset_index().sort_values(by='customer_id', ascending=False)
  city_wise_customer.rename(columns={'order_city': 'City', 'customer_id': 'No. of Customers'}, inplace=True)
  city_wise_customer.reset_index(drop=True, inplace=True)

  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          City wise Customers
      </h2>""", unsafe_allow_html=True)
  
  show_plot = st.checkbox('Show Plot')

  if show_plot:
      page_size = 10
      total_pages = (len(city_wise_customer) // page_size) + 1

      page = st.selectbox('Select page', range(1, total_pages + 1))

      start_idx = (page - 1) * page_size
      end_idx = start_idx + page_size

      fig = px.bar(city_wise_customer.iloc[start_idx:end_idx], x='City', y='No. of Customers')
      st.plotly_chart(fig)

  else:
      city_list = list(df['customer_city'].unique())
      city_list.insert(0, 'Overall')
      selected_city = st.selectbox('Select City', options=city_list, index=0)

      if selected_city != 'Overall':
          city_wise_customer = city_wise_customer[city_wise_customer['City'] == selected_city]

      page_size = 10
      total_pages = (len(city_wise_customer) // page_size) + 1

      page = st.selectbox('Select page', range(1, total_pages + 1))

      start_idx = (page - 1) * page_size
      end_idx = start_idx + page_size
      st.table(city_wise_customer.iloc[start_idx:end_idx])

def get_countrywise(df):
  """
  Display the number of customers by country.
  """
  st.write("")
  country_wise_customer = df.groupby('order_country')['customer_id'].count().reset_index().sort_values(by='customer_id', ascending=False)
  country_wise_customer.rename(columns={'order_country': 'Country', 'customer_id': 'No. of Customers'}, inplace=True)

  country_wise_customer.reset_index(drop=True, inplace=True)

  country_list = list(df['customer_country'].unique())
  country_list.insert(0, 'Overall')

  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Country wise Customers
      </h2>""", unsafe_allow_html=True)
  
  show_plot_1 = st.checkbox('Show Plot ')

  if show_plot_1:
      top_countries = country_wise_customer.nlargest(18, 'No. of Customers')
      other_customers = country_wise_customer[~country_wise_customer['Country'].isin(top_countries['Country'])]['No. of Customers'].sum()
      other_df = pd.DataFrame({'Country': ['Other'], 'No. of Customers': [other_customers]})
      final_df = pd.concat([top_countries, other_df], ignore_index=True)
      final_df_sorted = final_df.sort_values(by='No. of Customers', ascending=True)

      fig_horizontal_bar = px.bar(final_df_sorted, 
                         x='No. of Customers', 
                         y='Country', 
                         orientation='h')

      st.plotly_chart(fig_horizontal_bar)

  else:
      country_list = list(df['order_country'].unique())
      country_list.insert(0, 'Overall')
      selected_country = st.selectbox('Select Country', options=country_list, index=0)

      if selected_country != 'Overall':
          country_wise_customer = country_wise_customer[country_wise_customer['Country'] == selected_country]

      page_size = 10
      total_pages = (len(country_wise_customer) // page_size) + 1

      page = st.selectbox('Select page', range(1, total_pages + 1))

      start_idx = (page - 1) * page_size
      end_idx = start_idx + page_size
      st.table(country_wise_customer.iloc[start_idx:end_idx])
  
  st.write("Most of the customers belong to North American and European countries.")

def get_Statewise(df):
  """
  Display the number of customers by state.
  """
  st.write("")
  state_wise_customer = df.groupby('order_state')['customer_id'].count().reset_index().sort_values(by='customer_id', ascending=False)
  state_wise_customer.rename(columns={'order_state': 'State', 'customer_id': 'No. of Customers'}, inplace=True)

  state_wise_customer.reset_index(drop=True, inplace=True)

  State_list = list(df['customer_state'].unique())
  State_list.insert(0, 'Overall')

  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          State wise Customers
      </h2>""", unsafe_allow_html=True)
  
  show_plot_1 = st.checkbox('Show Table  ')

  if not show_plot_1:
      page_size = 10
      total_pages = (len(state_wise_customer) // page_size) + 1

      page = st.selectbox('Select page', range(1, total_pages + 1))

      start_idx = (page - 1) * page_size
      end_idx = start_idx + page_size
      fig = px.bar(state_wise_customer.iloc[start_idx:end_idx], x='State', y='No. of Customers')
      st.plotly_chart(fig)

  else:
      state_list = list(df['customer_state'].unique())
      state_list.insert(0, 'Overall')
      selected_state = st.selectbox('Select State', options=state_list, index=0)

      if selected_state != 'Overall':
          state_wise_customer = state_wise_customer[state_wise_customer['State'] == selected_state]

      page_size = 10
      total_pages = (len(state_wise_customer) // page_size) + 1

      page = st.selectbox('Select page  ', range(1, total_pages + 1))

      start_idx = (page - 1) * page_size
      end_idx = start_idx + page_size
      st.table(state_wise_customer.iloc[start_idx:end_idx])

def get_segmentwise(df):
  """
  Display the number of customers by segment.
  """
  st.write("")
  segment_wise_customer = df.groupby('customer_segment')['customer_id'].count().reset_index().sort_values(by='customer_id', ascending=False)
  segment_wise_customer.rename(columns={'customer_segment': 'Segment', 'customer_id': 'No. of Customers'}, inplace=True)
  segment_wise_customer.reset_index(drop=True, inplace=True)
  
  # Cards
  variables = list(zip(segment_wise_customer['Segment'], segment_wise_customer['No. of Customers']))
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Segment wise Customers
      </h2>""", unsafe_allow_html=True)
  
  for i in range(0, len(variables), 3):
      cols = st.columns(3)
      for j in range(3):
          if i + j < len(variables):
              title, value = variables[i + j]
              
              cols[j].markdown(
                  f"""
                  <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; margin-bottom:20px; text-align:center; box-shadow: 1px 1px 8px rgba(0, 0, 0, 0.3);">
                      <h3 style="color:#333;">{title}</h3>
                      <p style="font-size:24px; font-weight:bold; color: #636efa;">{value}</p>
                  </div>
                  """, 
                  unsafe_allow_html=True
              )

def format_sales(value):
  """
  Format sales values for display.
  """
  if value >= 1_000_000:
      return f'{value / 1_000_000:.2f}M'
  else:
      return f'{value / 1_000:.2f}K'

def get_segmentsales(df):
  """
  Display total sales and profit by customer segment.
  """
  st.write("")
  salessegment = df.groupby('customer_segment')[['sales', 'order_profit_per_order']].sum().reset_index().sort_values(by='sales', ascending=False)
  salessegment.rename(columns={'customer_segment': 'Segment', 'sales': "Total Sales", 'order_profit_per_order': 'Total Profit'}, inplace=True)
  salessegment['Total Sales ($)'] = salessegment['Total Sales'].apply(format_sales)
  salessegment['Total Profit ($)'] = salessegment['Total Profit'].apply(format_sales)
  salessegment['Profit Ratio (%)'] = round((salessegment['Total Profit'] / salessegment['Total Sales']) * 100, 2).astype(str)
  
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Segment wise Sales and Profit
      </h2>""", unsafe_allow_html=True)
  
  show_plot_3 = st.checkbox('Show Plot     ')

  if show_plot_3:
      fig = px.bar(salessegment, x='Segment', y=['Total Sales', 'Total Profit'], title='Total sales by segment')
      fig.update_layout(barmode='group')
      st.plotly_chart(fig)
  else:
      salessegment = salessegment[['Segment', 'Total Sales ($)', 'Total Profit ($)', 'Profit Ratio (%)']]
      st.table(salessegment)

def categoryPreferenceSegmentWise(df):
  """
  Display the top 5 product categories in each customer segment.
  """
  st.write("")
  categorysegment = df.groupby(['customer_segment', 'category_name'])['order_id'].count().reset_index()
  categorysegment = categorysegment.rename(columns={'category_name': 'Category', 'customer_segment': 'Segment', 'order_id': 'Count'})
  df_sorted = categorysegment.sort_values('Count', ascending=False)
  top_5 = df_sorted.groupby('Segment').head(5)

  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Top 5 Categories in Each Segment
      </h2>""", unsafe_allow_html=True)
  st.write("Treemap shows that in all types of customers, the most preferred categories are Shoes and Clothing.")
  
  fig_treemap = px.treemap(top_5, 
                      path=['Segment', 'Category'], 
                      values='Count')
  fig_treemap.update_traces(textinfo='label+value')

  # Show the plot
  st.plotly_chart(fig_treemap)

# --- Functions from market.py ---

def get_marketsales(df):
  """
  Display total sales and profit by market.
  """
  salesmarket = df.groupby('market')[['sales', 'order_profit_per_order']].sum().reset_index().sort_values(by='sales', ascending=False)
  salesmarket.rename(columns={'market': 'Market', 'sales': "Total Sales", 'order_profit_per_order': 'Total Profit'}, inplace=True)
  salesmarket['Total Sales ($)'] = salesmarket['Total Sales'].apply(format_sales)
  salesmarket['Total Profit ($)'] = salesmarket['Total Profit'].apply(format_sales)
  salesmarket['Profit Ratio (%)'] = round((salesmarket['Total Profit'] / salesmarket['Total Sales']) * 100, 2).astype(str)

  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Market wise Sales and Profit
      </h2>""", unsafe_allow_html=True)
  
  show_plot_4 = st.checkbox('Show Plot      ')

  if show_plot_4:
      fig = px.bar(salesmarket, x='Market', y=['Total Sales', 'Total Profit'])
      fig.update_layout(barmode='group')
      st.plotly_chart(fig)
  else:
      salesmarket = salesmarket[['Market', 'Total Sales ($)', 'Total Profit ($)', 'Profit Ratio (%)']]
      st.table(salesmarket)
  
  st.write("Markets with more sales are producing more profit. But Africa has the highest profit ratio.")

def mapforprofit(df):
  """
  Display a choropleth map showing profit amounts by country.
  """
  indextodrop = df[df['order_profit_per_order'] < 0].index
  df.drop(indextodrop, inplace=True)
  
  fig = px.choropleth(
      df,
      locations='order_country',           # Column for the country names
      locationmode='country names',        # The type of location, which is the country name
      color='order_profit_per_order',      # Column for coloring based on profit
      labels={'order_profit_per_order': 'Profit Amount'},
      title='Profit Amount per Country'
  )

  # Update layout for a dark mode style
  fig.update_layout(
      geo=dict(
          bgcolor='white',                 # Background color of the map
          lakecolor='white',               # Color for lakes
          landcolor='white',               # Land color
          subunitcolor='white',            # Subunit boundaries color
          countrycolor='white'             # Country boundaries color
      ),
      paper_bgcolor='white',               # Background color of the entire plot
      plot_bgcolor='white'                 # Background color of the plotting area
  )
  st.plotly_chart(fig)

def marketwisetrend(df):
  """
  Display market-wise monthly sales trends.
  """
  df['order_period'] = df['order_date'].dt.to_period('M')
  df['order_period_str'] = df['order_period'].astype(str)

  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Market-Wise Monthly Sales
      </h2>""", unsafe_allow_html=True)

  market_list = list(df['market'].unique())
  market_list.insert(0, 'Overall')
  selected_market = st.selectbox('Select Market', options=market_list, index=0)

  update = df
  if selected_market != 'Overall':
      update = df[df['market'] == selected_market]

  monthly_sales = update.groupby(['market', 'order_period_str'])['sales'].sum().reset_index()

  fig_line_plot = px.line(
      monthly_sales, 
      x='order_period_str',               # Use the string format of 'order_period'
      y='sales', 
      color='market',                     # Different lines for each market
      labels={'sales': 'Total Sales', 'order_period_str': 'Month-Year'},
      markers=True                        # Display markers for each data point
  )

  # Update the layout to show month names properly
  fig_line_plot.update_layout(
      xaxis_title="Month-Year",
      yaxis_title="Sales",
      xaxis=dict(tickformat="%b %Y"),     # Format X-axis to show Month and Year
      hovermode='x unified',              # Unified hover mode for clearer comparison
  )

  # Display the plot using Streamlit
  st.plotly_chart(fig_line_plot)
  st.write("""The spikes show that if they focus on one market then sales for all the other markets are dropped. 
          It might show they have insufficient resources to manage all the markets at the same time.""")

def marketduration(df):
  """
  Display average shipping duration by market.
  """
  marketwiseduration = df.groupby('market')['shipping_duration'].mean().reset_index()
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Average Shipping Duration by Market
      </h2>""", unsafe_allow_html=True)

  # Custom CSS for larger centered card
  st.markdown("""<style>
      .big-card {
          background-color:#f0f2f6; 
          padding: 30px; 
          border-radius: 15px; 
          margin-bottom: 20px; 
          text-align:center; 
          box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
      }
      .small-card {
          background-color:#f0f2f6; 
          padding: 20px; 
          border-radius: 10px; 
          margin-bottom: 20px; 
          text-align:center; 
          box-shadow: 1px 1px 8px rgba(0, 0, 0, 0.3);
      }
      </style>""", unsafe_allow_html=True)

  # First row with a single centered card (larger)
  col1, col2, col3 = st.columns([1, 2, 1])  # Middle column is bigger to center the card
  with col2:
      st.markdown(
          f"""
          <div class="big-card">
              <h3>{marketwiseduration.iloc[0]['market']}</h3>
              <p style="font-size:24px; font-weight:bold; color: #636efa;">{marketwiseduration.iloc[0]['shipping_duration']:.2f} days</p>
          </div>
          """,
          unsafe_allow_html=True
      )

  # Second and subsequent rows with two cards per row
  for i in range(1, len(marketwiseduration), 2):
      cols = st.columns(2)
      
      for j in range(2):
          if i + j < len(marketwiseduration):
              market = marketwiseduration.iloc[i + j]['market']
              duration = marketwiseduration.iloc[i + j]['shipping_duration']
              
              # Add the cards in smaller size
              with cols[j]:
                  st.markdown(
                      f"""
                      <div class="small-card">
                          <h3>{market}</h3>
                          <p style="font-size:20px; font-weight:bold; color: #636efa;">{duration:.2f} days</p>
                      </div>
                      """, 
                      unsafe_allow_html=True
                  )

# --- Functions from product.py ---

def bestSellingProducts(df):
  """
  Display the best-selling products.
  """
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Best Selling Products
      </h2>""", unsafe_allow_html=True)

  bestsellingproducts = df.groupby('product_name')['sales'].sum().reset_index().sort_values(by='sales', ascending=False).head(10)
  bestsellingproducts.rename(columns={'product_name': 'Product', 'sales': "Total Sales"}, inplace=True)
  show_plot_9 = st.checkbox('Show Table  ')

  if not show_plot_9:
      fig_horizontal_bar = px.bar(bestsellingproducts, 
                         x='Total Sales', 
                         y='Product', 
                         orientation='h')
      st.plotly_chart(fig_horizontal_bar)
  else:
      st.table(bestsellingproducts)

def bestSellingCategories(df):
  """
  Display the best-selling product categories.
  """
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Best Selling Product Categories
      </h2>""", unsafe_allow_html=True)
  
  bestsellingcategories = df.groupby(['category_name', 'product_name'])['sales'].sum().reset_index().sort_values(by='sales', ascending=False)
  top_categories = bestsellingcategories.groupby('category_name')['sales'].sum().reset_index().sort_values(by='sales', ascending=False).head(10)['category_name']
  bestsellingcategories = bestsellingcategories[bestsellingcategories['category_name'].isin(top_categories)]
  bestsellingcategories.rename(columns={'category_name': 'Category', 'sales': 'Total Sales', 'product_name': "Product"}, inplace=True)
  
  show_plot_9 = st.checkbox('Show Table   ')
  if not show_plot_9:
      fig_horizontal_bar = px.bar(bestsellingcategories, 
                          x='Total Sales', 
                          y='Category',
                          color='Product',
                          orientation='h')
      st.plotly_chart(fig_horizontal_bar)
  else:
      st.table(bestsellingcategories.head(10))

def bestProductMargins(df):
  """
  Display the best products by profit margin.
  """
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Best Products by Profit Margin
      </h2>""", unsafe_allow_html=True)
  
  # Calculate order item profit
  df['order_item_profit'] = df['order_item_profit_ratio'] * df['sales']
  bestproductmargins = df.groupby('product_name')['order_item_profit'].mean().reset_index().sort_values(by='order_item_profit', ascending=False).head(7)
  bestproductmargins.rename(columns={'product_name': 'Product', 'order_item_profit': "Profit Margin"}, inplace=True)
  
  show_plot_10 = st.checkbox('Show Table')
  if not show_plot_10:
      # Create a bubble chart instead of a bar chart
      fig_bubble = px.scatter(bestproductmargins, 
                              x='Product', 
                              y='Profit Margin', 
                              size='Profit Margin',  # Use Profit Margin to determine the bubble size
                              color='Product',       # Different colors for each product
                              hover_name='Product', 
                              size_max=60)           # Maximum size of the bubbles
      # Hide x-axis labels
      fig_bubble.update_layout(xaxis=dict(showticklabels=False))
      st.plotly_chart(fig_bubble)
  else:
      st.table(bestproductmargins)

def categorize_discount_rate(df):
  """
  Categorize discount rates into bins.
  """
  bins = [-float('inf'), 0, 0.025, 0.05, 0.075, 0.10, 0.125, 0.15, 0.175, 0.20, 0.225, 0.25, float('inf')]
  labels = [0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, '25+']

  # Create a new column with the categorized discount rate based on 2.5% intervals
  df['discount_category'] = pd.cut(df['order_item_discount_rate'], 
                                   bins=bins, 
                                   labels=labels, 
                                   right=False)  # right=False means the intervals are [)

  return df

def discountVsSales(df):
  """
  Display the trend of discount sales.
  """
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Discount Sales Trend
      </h2>""", unsafe_allow_html=True)
  st.write("There seems to be no clear relationship between discount rate and sales volume.")
  
  df = categorize_discount_rate(df)
  df = df.groupby('discount_category')['order_item_discount_rate'].count().reset_index()
  df.rename(columns={'discount_category': 'Discount Rate (%)', 'order_item_discount_rate': "No. of Orders"}, inplace=True)
  
  fig_line = px.line(df, 
                     x='Discount Rate (%)', 
                     y="No. of Orders", 
                     markers=True)  # markers=True to show points on the line
  
  st.plotly_chart(fig_line)

def priceprofit(df):
  """
  Display the correlation between product price and profit.
  """
  correlation = df['product_price'].corr(df['product_profit'])

  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Product Price VS Profit
      </h2>""", unsafe_allow_html=True)

  st.markdown(
      f"""
      <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; margin-bottom:20px; text-align:center;">
          <h3 style="color:#333;">Correlation Coefficient</h3>
          <p style="font-size:36px; font-weight:bold; color: #636efa;">{correlation:.2f}</p>
      </div>
      """, 
      unsafe_allow_html=True
  )

  st.subheader("Scatter Plot of Product Price vs Order Profit")
  st.write("There is significant positive correlation between Product Price and Order Profit.")

  fig = px.scatter(df, x='product_price', y='product_profit', 
                  title='Price vs Profit',
                   labels={'product_price': 'Product Price', 'product_profit': 'Order Profit'},
                   template="plotly_white",
                   )
  
  # Customize the layout for better readability
  fig.update_layout(
      title={'x': 0.5},  # Center the title
      xaxis_title='Product Price',
      yaxis_title='Order Profit per Order',
      showlegend=False,
      plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
      xaxis=dict(showgrid=True, gridcolor='lightgray'),
      yaxis=dict(showgrid=True, gridcolor='lightgray')
  )

  st.plotly_chart(fig)

# --- Functions from order.py ---

def daywiseorder(df):
  """
  Display the count of orders by day of the week.
  """
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Day wise order counts
      </h2>""", unsafe_allow_html=True)
  
  orderdaywise = df.groupby('order_weekday')['order_id'].count().reset_index()
  weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

  # Create a categorical type with the custom order
  orderdaywise['order_weekday'] = pd.Categorical(orderdaywise['order_weekday'], categories=weekday_order, ordered=True)

  # Sort based on the custom order
  orderdaywise = orderdaywise.sort_values('order_weekday').reset_index(drop=True)

  orderdaywise.rename(columns={'order_id': 'No. of Orders', 'order_weekday': 'Day'}, inplace=True)
  show_plot_12 = st.checkbox('Show Plot          ')

  if show_plot_12:
      fig = px.bar(orderdaywise, x='Day', y='No. of Orders')
      st.plotly_chart(fig)
  else:
      st.table(orderdaywise)
  
  st.write("Number of Orders increase as the weekend approaches.")

def shippingmode(df):
  """
  Display order status by shipping modes.
  """
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Order Status by Shipping Modes
      </h2>""", unsafe_allow_html=True)
  
  shippingmode = df.groupby(['order_status', 'shipping_mode'])['order_id'].count().reset_index()
  shippingmode.rename(columns={'order_status': 'Status', 'shipping_mode': 'Shipping Mode', 'order_id': 'Count'}, inplace=True)

  show_plot = st.checkbox('Show Table')

  if not show_plot:
      fig = px.bar(shippingmode, x='Status', y='Count', color='Shipping Mode')
      st.plotly_chart(fig)
  else:
      shippingmodelist = list(df['shipping_mode'].unique())
      shippingmodelist.insert(0, 'Overall')
      selected_mode = st.selectbox('Select Shipping Mode', options=shippingmodelist, index=0)

      statuslist = list(df['order_status'].unique())
      statuslist.insert(0, 'Overall')
      selected_status = st.selectbox('Select Order Status', options=statuslist, index=0)

      if selected_status != 'Overall' and selected_mode != 'Overall':
          shippingmode = shippingmode[(shippingmode['Shipping Mode'] == selected_mode) & (shippingmode['Status'] == selected_status)]
      elif selected_status != 'Overall' and selected_mode == 'Overall':
          shippingmode = shippingmode[shippingmode['Status'] == selected_status]
      elif selected_status == 'Overall' and selected_mode != 'Overall':
          shippingmode = shippingmode[shippingmode['Shipping Mode'] == selected_mode]
      elif selected_status == 'Overall' and selected_mode == 'Overall':
          shippingmode = shippingmode

      st.table(shippingmode)

def averageshippingdelay(df):
  """
  Display average shipping duration by shipping mode.
  """
  average_duration = df.groupby('shipping_mode')['shipping_duration'].mean().reset_index()

  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Average Shipping Duration by Shipping Mode
      </h2>""", unsafe_allow_html=True)

  # Custom CSS for consistent card styling
  st.markdown("""<style>
      .small-card {
          background-color:#f0f2f6; 
          padding: 20px; 
          border-radius: 10px; 
          margin-bottom: 20px; 
          text-align:center; 
          box-shadow: 1px 1px 8px rgba(0, 0, 0, 0.3);
      }
      </style>""", unsafe_allow_html=True)

  # Display the cards in rows of 2
  with st.container():
      cols = st.columns(2)  # Create 2 columns per row
      
      # Loop through each shipping mode and display it as a card
      for index, row in average_duration.iterrows():
          shipping_mode = row['shipping_mode']
          avg_duration = row['shipping_duration']
          
          # Determine which column to place the card in
          col_index = index % 2
          
          # Place the card in the appropriate column
          with cols[col_index]:
              st.markdown(
                  f"""
                  <div class="small-card">
                      <h3>{shipping_mode}</h3>
                      <p style="font-size:24px; font-weight:bold; color: #636efa;">{avg_duration:.2f} days</p>
                  </div>
                  """, 
                  unsafe_allow_html=True
              )

          # Create new columns for every new row after two cards
          if (index + 1) % 2 == 0:
              cols = st.columns(2)

def shipdurationdistribution(df):
  """
  Display the distribution of shipping durations.
  """
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Shipping Duration Distribution
      </h2>""", unsafe_allow_html=True)
  st.write("Most of the orders are taking 8 to 10 days to deliver.")

  fig = px.histogram(df, x='shipping_duration', nbins=6, 
                 labels={'shipping_duration': 'Shipping Duration (days)'},
                 color_discrete_sequence=['skyblue'])

  fig.update_layout(
      xaxis_title='Shipping Duration (days)',
      yaxis_title='Frequency',
      bargap=0.2, 

  )

  st.plotly_chart(fig)

def shipdurationbymode(df):
  """
  Display shipping duration by shipping mode.
  """
  st.markdown(""" <h2 style="font-size: 32px; font-weight: bold; color: #FF7F50;">
          Shipping Duration by Shipping Mode
      </h2>""", unsafe_allow_html=True)
  st.write("First and Second class are delivering orders in time. While Same Day is facing some issues and showing exceptions in delivery time.")
  
  fig = px.box(df, x='shipping_mode', y='shipping_duration',
           labels={'shipping_duration': 'Shipping Duration (days)', 'shipping_mode': 'Shipping Mode'},
           color='shipping_mode')

  # Customize the layout for better appearance
  fig.update_layout(
      xaxis_title='Shipping Mode',
      yaxis_title='Shipping Duration (days)',

  )

  st.plotly_chart(fig)

# --- Streamlit App ---
# st.set_page_config(page_title="Supply Chain Dashboard", layout="wide")

# --- Data Loading and Preprocessing ---
@st.cache_data  # Cache the preprocessed data
def load_and_preprocess_data():
  return preprocess()

df = load_and_preprocess_data()

# --- Sidebar Navigation ---
selected_page = st.sidebar.radio('Select View', ('Overview', 'Customer', 'Market Segment', 'Sales Orders', 'Inventory'))

# --- Page-Specific Content ---
if selected_page == 'Overview':
  st.title("Summary Analysis")
  overallcards(df)
  orderStatusCount(df)
  salesTrend(df)
  productPriceByShippingMode(df)
  getSummary(df)

elif selected_page == 'Customer':
  st.title("Customer Analysis")
  get_segmentwise(df)
  get_citywise(df)
  get_countrywise(df)
  get_Statewise(df)
  categoryPreferenceSegmentWise(df)
  get_segmentsales(df)

elif selected_page == 'Market Segment':
  st.title("Market Analysis")
  marketwisetrend(df)
  get_marketsales(df)
  marketduration(df)

elif selected_page == 'Sales Orders':
  st.title("Order Analysis")
  daywiseorder(df)
  shippingmode(df)
  averageshippingdelay(df)
  shipdurationdistribution(df)
  shipdurationbymode(df)

elif selected_page == 'Inventory':
  st.title("Product Analysis")
  bestSellingProducts(df)
  bestSellingCategories(df)
  bestProductMargins(df)
  discountVsSales(df)
  priceprofit(df)

