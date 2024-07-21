import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(
    page_title="Sales Performance",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",  # Ensure sidebar is expanded by default
)

# Add custom CSS for background color and icon color
custom_css = f"""
    <style>
    body {{
        background-color: #6495ED;  /* Set background color to blue */
    }}
    .favicon {{
        filter: invert(1);  /* Invert the icon colors to make it suitable for dark backgrounds */
    }}
    </style>
    """
st.markdown(custom_css, unsafe_allow_html=True)

# Read the dataset
df = pd.read_csv("supermarket_sales - Sheet1.csv")
df = df.rename(columns={'Customer type': "Customer_type", 'gross income': "Gross_Income"})
df["hour"] = pd.to_datetime(df["Time"], format="%H:%M").dt.hour
# Sidebar filters
st.sidebar.header("Please Filter Here:")
start_date = st.sidebar.date_input(
    "Start date",
    value=pd.to_datetime(df['Date']).min()
)

end_date = st.sidebar.date_input(
    "End date",
    value=pd.to_datetime(df['Date']).max()
)
city = st.sidebar.multiselect(
    "Select the City:",
    options=df["City"].unique(),
    default=df["City"].unique()
)

customer_type = st.sidebar.multiselect(
    "Select the Customer Type:",
    options=df["Customer_type"].unique(),
    default=df["Customer_type"].unique(),
)

gender = st.sidebar.multiselect(
    "Select the Gender:",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)


df['Date'] = pd.to_datetime(df['Date'])
df_selection = df.query(
    "City == @city & Customer_type == @customer_type & Gender == @gender & Date >= @start_date & Date <= @end_date"
)
# Check if the dataframe is empty:
if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop() # This will halt the app from further execution.

# ---- MAINPAGE ----
st.title("💹  Sales Performance")
st.markdown("##")

# TOP KPI's
total_sales = int(df_selection["Total"].sum())
average_rating = round(df_selection["Rating"].mean(), 1)
star_rating = "⭐" * int(round(average_rating, 0))  # Unicode for star emoji
if average_rating % 1 >= 0.5:
    star_rating += "½"  # Add half star if average_rating is >= 0.5

average_sale_by_transaction = round(df_selection["Total"].mean(), 1)
total_gross_income = round(df_selection["Gross_Income"].sum(),1)

# Define the columns
col1, col2, col3, col4 = st.columns(4)

# Column 1: Total Sales
with col1:
    st.markdown("<p style='font-size: 15px; font-weight: bold;'>Total Sales:</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 14px; font-weight: bold;'>US $ {total_sales:,}</p>", unsafe_allow_html=True)

# Column 2: Average Rating
with col2:
    st.markdown("<p style='font-size: 15px; font-weight: bold;'>Average Rating:</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 16px; font-weight: bold;'>{star_rating}</p>", unsafe_allow_html=True)

# Column 3: Total Gross Income
with col3:
    st.markdown("<p style='font-size: 15px; font-weight: bold;'>Total Gross Income:</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 14px; font-weight: bold;'>US $ {total_gross_income:,.2f}</p>", unsafe_allow_html=True)

# Column 4: Average Sales Per Transaction
with col4:
    st.markdown("<p style='font-size: 15px; font-weight: bold;'>Average Sales Per Transaction:</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 14px; font-weight: bold;'>US $ {average_sale_by_transaction}</p>", unsafe_allow_html=True)
st.markdown("""---""")

# SALES BY PRODUCT LINE [BAR CHART]
sales_by_product_line = df_selection.groupby(by=["Product line"])[["Total"]].sum().sort_values(by="Total")
fig_product_sales = px.bar(
    sales_by_product_line,
    x="Total",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Sales by Product Line</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# SALES BY HOUR [BAR CHART]
sales_by_hour = df_selection.groupby(by=["hour"])[["Total"]].sum()
fig_hourly_sales = px.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="Total",
    title="<b>Sales by hour</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
    template="plotly_white",
)
fig_hourly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)


left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
right_column.plotly_chart(fig_product_sales, use_container_width=True)

sales_over_time = df_selection.groupby(pd.Grouper(key='Date', freq='D')).sum()['Total'].reset_index()
fig_sales_over_time = px.line(
    sales_over_time,
    x='Date',
    y='Total',
    title="<b>Sales Over Time</b>",
    template="plotly_white",
)
fig_sales_over_time.update_traces(mode='lines+markers', marker=dict(color='#FF5733'))



st.markdown("""---""")
st.markdown("<b>Sales Over Time (Daily)</b>", unsafe_allow_html=True)
st.plotly_chart(fig_sales_over_time, use_container_width=True)
# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
