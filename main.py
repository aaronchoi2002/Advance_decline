import yfinance as yf
import pandas as pd
import streamlit as st
from language import languages
import mplfinance as mpf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt



# Define the ticker symbol
#df = pd.read_csv("C:/Users/aaron/OneDrive/文档/web_app/advance_decline/sp500_adj_close.csv")

@st.cache_data
def download_stock_data(tickers, start_date):
    df = yf.download(tickers, start=start_date)["Adj Close"]
    return df


def assign_stock_return_labels(neutral_threshold_percent):
    df_diff_sign = df_diff.applymap(
        lambda x: 'positive' if x > neutral_threshold_percent else (
            'negative' if x < -neutral_threshold_percent else (
                'neutral' if -threshold_percent <= x <= neutral_threshold_percent else 'no data')))
    return df_diff_sign


tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']
tickers = tickers.to_list()
df = download_stock_data(tickers, "2022-01-01")

# Calculating the price difference
df_diff = df.pct_change() * 100

selected_language = st.sidebar.selectbox("Choose a language", options=['English', '簡體', '繁體'])
threshold_percent = st.sidebar.number_input(f"{languages['Neutral_Threshold(%)'][selected_language]}", min_value=0.0, max_value=10.0, value=0.0, step=0.1)

st.title(f"{languages['title'][selected_language]}")

df_diff_sign = assign_stock_return_labels(threshold_percent)



positive_counts = df_diff_sign[df_diff_sign == 'positive'].count(axis=1)
neutral_counts = df_diff_sign[df_diff_sign == 'neutral'].count(axis=1)
negative_counts = df_diff_sign[df_diff_sign == 'negative'].count(axis=1)
no_data_counts = df_diff_sign[df_diff_sign == 'no data'].count(axis=1)

# Creating a DataFrame to show the counts
df_counts = pd.DataFrame({
    'positive_returns': positive_counts,
    'neutral_returns': neutral_counts,
    'negative_returns': negative_counts,
    'no_data': no_data_counts
})

df_counts["total"] = df_counts["positive_returns"] + df_counts["neutral_returns"] + df_counts["negative_returns"]
df_counts["AD"] = df_counts["positive_returns"] - df_counts["negative_returns"]
df_counts["positive_percentage"] = round((df_counts["positive_returns"] / df_counts["total"])*100,2)
df_counts["positive_neutral_percentage"] = round(((df_counts["positive_returns"] + df_counts["neutral_returns"]) / df_counts["total"])*100,2)

Col1, Col2, Col3  = st.columns(3)
with Col1:
    st.metric(label=languages['AD'][selected_language], value=df_counts["AD"].iloc[-1])

with Col2:
    st.metric(label=languages['positive_percentage'][selected_language], value=f'{df_counts["positive_percentage"].iloc[-1]}%')

with Col3:
    st.metric(label=languages['positive_neutral_percentage'][selected_language], value=f'{df_counts["positive_neutral_percentage"].iloc[-1]}%')



st.write("_______________")

Col1, Col2, Col3, Col4 = st.columns(4)
with Col1:
    st.metric(label=languages['Positive Return'][selected_language], value=df_counts["positive_returns"].iloc[-1])

with Col2:
    st.metric(label=languages['Neutral Returns'][selected_language], value=df_counts["neutral_returns"].iloc[-1])

with Col3:
    st.metric(label=languages['Negative Returns'][selected_language], value=df_counts["negative_returns"].iloc[-1])

with Col4:
    st.metric(label=languages['No Data'][selected_language], value=df_counts["no_data"].iloc[-1])
st.write(df_counts["AD"].index[-1])

st.markdown("""<hr style="border-top: 2px solid black; border-bottom: 2px solid black;">""", unsafe_allow_html=True)
st.subheader(languages['chart'][selected_language])
Col1, Col2 = st.columns(2)
with Col1:
    trade_day = st.number_input(f"{languages['Trading days covered'][selected_language]}", min_value=1.0, max_value=360.0, value=60.0, step=1.0)
    # Get last 30 days data
    df_last_days = df_counts.tail(int(trade_day))

with Col2:
    average = st.number_input(f"{languages['Average Days'][selected_language]}", min_value=1.0, max_value=60.0, value=10.0, step=1.0)
    #Get the average of the last 30 days
    df_last_days["positive_percentage_average"] = df_last_days["positive_percentage"].rolling(int(average)).mean()
    df_last_days["positive_neutral_percentage_average"] = df_last_days["positive_neutral_percentage"].rolling(int(average)).mean()

# Create line charts
st.write(f"Start from: {df_last_days.index[0]}")

df_dow = yf.download("^GSPC", start="2022-01-01")
df_dow = df_dow.tail(int(trade_day))

#Create subplots
fig = make_subplots(rows=2, cols=1)

# Add candlestick chart
fig.add_trace(go.Candlestick(x=df_dow.index, 
                             open=df_dow['Open'], 
                             high=df_dow['High'], 
                             low=df_dow['Low'], 
                             close=df_dow['Close'], 
                             name='S&P 500'), row=1, col=1)

# Add line charts
fig.add_trace(go.Scatter(x=df_last_days.index, y=df_last_days['positive_percentage_average'], mode='lines', name='positive_percentage_average'), row=2, col=1)
fig.add_trace(go.Scatter(x=df_last_days.index, y=df_last_days['positive_neutral_percentage_average'], mode='lines', name='positive_neutral_percentage_average'), row=2, col=1)

# Update layout
fig.update_layout(height=800, width=1200, title_text="^GSPC Prices and Average Percentages")
fig.update_layout(xaxis_rangeslider_visible=False)
#Show the plot in Streamlit
st.plotly_chart(fig)