import streamlit as st
import pandas as pd
import numpy as np
from fetch_data import get_open_data_elia_df
from forecast_prophet import forecast_prophet

st.title("Timeseries Forecaster")

st.write("Select the data you would like to forecast.")
button_solar = st.button("Solar Data")
button_total_load = st.button("Total Load")
df = pd.DataFrame()

## Fetching the Data from The API
if button_solar:
    dataset_solar =  "ods032" # total_load_dataset 
    df = get_open_data_elia_df(dataset_solar, 1000)
    df = df.loc[:,["datetime", "eliagridload"]]

if button_total_load: 
    dataset_load = "ods003" # solar_dataset 
    df = get_open_data_elia_df(dataset_load, 1000)
    df = df.loc[:,["datetime", "eliagridload"]]
    df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)
    

if not df.empty:

    # Display the data from the API
    st.write(df)
    st.line_chart(df.set_index("datetime"))


    # Do the prediction
    df_ts = df.rename(columns = {df.columns[0]: "ds", df.columns[1]:"y"})
    forecast, fig_forecast, fig_comp = forecast_prophet(df_ts, 72)

    st.write(forecast)
    st.write("This is the forecast plot")
    st.write(fig_forecast)
    st.write(fig_comp)



