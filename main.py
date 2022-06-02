from doctest import DocFileCase
from lib2to3.pgen2.pgen import DFAState
import streamlit as st
import pandas as pd
import numpy as np
from fetch_data import get_open_data_elia_df
from forecast_prophet import forecast_prophet
from datetime import datetime
from download_button import download_button



st.image("data/TimeSeriesForecaster.png")
"""
### Introduction
With this app you can forecast the Total Load, the PV production as well as the Wind production of the Belgium Electricity Grid. The live data is fetched from the
[Elia Open Data Platform](https://www.elia.be/en/grid-data/open-data). At the moment it is a univariate forecast only.
In case you do not see any results, you might need to wait a moment as the API only allows a limited number of requests.
"""

st.markdown(
    """ ### Data Selection 
    Select the data from Elia grid you would like to forecast."""
    )


col1, col2, col3 = st.columns(3)
button_total_load = col1.button("Total Load ")
button_solar = col2.button("PV production")
button_wind = col3.button("Wind production")

"""
### Training Data and Forecast Horizon
Select the number of days from historical data that will be used for the model training. Next, choose the number of days that you like to predict.

"""
col1, col2 = st.columns(2)
no_days = col1.slider("Historical data in days.", min_value=1, max_value=14 )
button_periods_to_predict = col2.slider("Forecast Horizon in days", min_value = 1, max_value = 7 )


no_of_quarter_hours = no_days*24*4

df = pd.DataFrame()

## Fetching the Data from The API
if button_solar:
    dataset_solar =  "ods032" # solar data set
    try:    
        df = get_open_data_elia_df(dataset_solar, no_of_quarter_hours*14)
        df = df.groupby("datetime").sum()
        df.reset_index(inplace = True)
        df = df.loc[:,["datetime", "mostrecentforecast"]]
        df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)
    except:
          "**The API was not able to provide the data. Try to reduce the historical data in days or wait a moment.**"
if button_total_load: 
    dataset_load = "ods003" #  total load dataset
    try:
        df = get_open_data_elia_df(dataset_load, no_of_quarter_hours)
        df = df.loc[:,["datetime", "eliagridload"]]
    except:
          "**The API was not able to provide the data. Try to reduce the historical data in days or wait a moment.**"
if button_wind:
    dataset_solar =  "ods031" # solar data set
    try:
        df = get_open_data_elia_df(dataset_solar, no_of_quarter_hours*14)
        df = df.groupby("datetime").sum()
        df.reset_index(inplace = True)
        df = df.loc[:,["datetime", "mostrecentforecast"]]
    except:
        "**The API was not able to provide the data. Try to reduce the historical data in days or wait a moment.**"


if not df.empty:

    """
    ### Historical Data
    The following section displays the selected historical data.
    """
    # Display the data from the API
    st.line_chart(df.set_index("datetime"))
    st.dataframe(df)

    # Do the prediction
    df_ts = df.rename(columns = {df.columns[0]: "ds", df.columns[1]:"y"})
    forecast, fig_forecast, fig_comp = forecast_prophet(df_ts, 72)
    """
    ### Forecast Results
    The following section displays the forecast results. It is divided into the forecast and a component plot.
    """

    """
    #### Forecast Plot
    """
    st.write(fig_forecast)
    forecast.rename(columns={"ds":"datetime"}, inplace = True)

    # selection of the most important columns of forecast dataframe
    st.write(forecast.loc[:,["datetime","yhat","yhat_lower","yhat_upper"]])
    st.markdown("#### Components Plot")
    st.write(fig_comp)

    """
    ### Download Section
    You can download the **Input Data** and the **Forecast Results** as a .csv file. 
    The Input Data is fetched from the Elia Open Data Platform. 
    The Forecast Results include in-sample prediction (historical) and the out-of-sample prediction.
    """
    # get current data
    now = datetime.now()

    # function to convert dataframe to csv
    def convert_df(df):
        return df.to_csv().encode("utf-8")

    col1, col2 = st.columns(2)
    col1.markdown(
        download_button(
            convert_df(df), 
            f'input_data_{now.strftime("%d/%m/%Y_%H:%M:%S")}.csv', 
            "Download Input Data Source"),
            unsafe_allow_html=True
        )

    col2.markdown(
        download_button(
            convert_df(forecast),
            f'forecast_data_{now.strftime("%d/%m/%Y_%H:%M:%S")}.csv',
            "Download Forecast Results"),
            unsafe_allow_html=True
        )
    

