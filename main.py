from doctest import DocFileCase
from lib2to3.pgen2.pgen import DFAState
import streamlit as st
import pandas as pd
import numpy as np
from fetch_data import get_open_data_elia_df
from forecast_prophet import forecast_prophet, run_forecast_univariate
from datetime import datetime, timedelta
from download_button import download_button
from forecast_multivariate import prepare_data_for_mv_fc_total_load, forecast_prophet_multivariate, prepare_data_for_mv_fc_wind_solar
import logging
import sys
from helper import check_regressors



## setting the config of the logger: 
# stream = sys.stdout ->  print the log directly under the notebook window
# level -> sets the level of the logger. available levels are: DEBUG, INFO, WARNING, ERROR, CRITICAL


logging.debug("Test")

st.image("data/TimeSeriesForecaster.png")
"""
### Introduction
With this app you can forecast the Total Load, the PV production as well as the Wind production of the Belgium Electricity Grid. The live data is fetched from the
[Elia Open Data Platform](https://www.elia.be/en/grid-data/open-data). 
In case you do not see any results, you might need to wait a moment as the API only allows a limited number of requests.
"""

"""
### Forecasting Method

"""

forecast_model = st.radio(
     "Select your forecasting method:",
     ('Univariate', 'Multivariate'))

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
no_of_hours_to_predict = button_periods_to_predict *24
no_days_hours = no_days*24
no_of_quarter_hours = no_days*24*4
forecast = None
fig_forecast = None
fig_comp = None
reg_coef = None
df = pd.DataFrame()
forecast_ready= False
reg_coef = None
end_date_hist = datetime.now()
start_date_hist = end_date_hist - timedelta(days = no_days)

if forecast_model == "Univariate":
    ## Fetching the Data from The API
    if button_solar:
                dataset_solar =  "ods032" # solar data set
         
                df = get_open_data_elia_df(dataset_solar,start_date_hist, end_date_hist) ###### no_of_quarter_hours*14
                df = df.groupby("datetime").sum()
                df.reset_index(inplace = True)
                df = df.loc[:,["datetime", "mostrecentforecast"]]
                df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)
                forecast, fig_forecast, fig_comp= run_forecast_univariate(df, no_of_hours_to_predict)
                forecast_ready = True
        
                "**The API was not able to provide the data. Try to reduce the historical data in days or wait a moment.**"
    if button_total_load: 
            dataset_load = "ods003" #  total load dataset
        
            df = get_open_data_elia_df(dataset_load, start_date_hist, end_date_hist)
            df = df.loc[:,["datetime", "eliagridload"]]
            forecast, fig_forecast, fig_comp= run_forecast_univariate(df, no_of_hours_to_predict)
            forecast_ready = True
        
            "**The API was not able to provide the data. Try to reduce the historical data in days or wait a moment.**"
    if button_wind:
            dataset_wind =  "ods031" # wind data set
            df = get_open_data_elia_df(dataset_wind, start_date_hist, end_date_hist) # 14 different departments
            df = df.groupby("datetime").sum()
            df.reset_index(inplace = True)
            df = df.loc[:,["datetime", "mostrecentforecast"]]
            forecast, fig_forecast, fig_comp= run_forecast_univariate(df, no_of_hours_to_predict)
            forecast_ready = True
        
            "**The API was not able to provide the data. Try to reduce the historical data in days or wait a moment.**"


 
if forecast_model == "Multivariate":
    
    """
    ### Choose Additional Regressors
    
    """
    add_regressors = st.multiselect(
        "Select the additional parameters for the forecast. At least, one has to be selected.",
        options = ["Sun Radiation", "Wind Speed", "Temperature"])

    if add_regressors:
        
        solar, wind, temp = check_regressors(add_regressors) 
        lat = "50.85045"
        long= "4.34878"

        if button_solar:
               dataset =  "ods032" # solar data set
               df_merged = prepare_data_for_mv_fc_wind_solar(dataset, start_date_hist, end_date_hist, solar, wind, temp, lat,long)
               forecast, fig_forecast, fig_comp, reg_coef = forecast_prophet_multivariate(df_merged, lat, long, no_of_hours_to_predict)
               forecast_ready = True
               df = df_merged.loc[:,["ds","y"]].rename(columns= {"ds":"datetime"})
            
        if button_wind:
                dataset = "ods031" # wind
            
                dataset = "ods031" # solar data set
                df_merged = prepare_data_for_mv_fc_wind_solar(dataset, start_date_hist, end_date_hist, solar, wind, temp, lat,long)
                print("This is df_merged" + str(df_merged))
                forecast, fig_forecast, fig_comp, reg_coef = forecast_prophet_multivariate(df_merged, lat, long, no_of_hours_to_predict)
                forecast_ready = True
                df = df_merged.loc[:,["ds","y"]].rename(columns= {"ds":"datetime"})
            
            
        if button_total_load:
                dataset = "ods003" ## total load
            
                df_merged = prepare_data_for_mv_fc_total_load(dataset, start_date_hist, end_date_hist, solar, wind, temp, lat,long)
                forecast, fig_forecast, fig_comp, reg_coef = forecast_prophet_multivariate(df_merged, lat, long, no_of_hours_to_predict)
                forecast_ready = True
                df = df_merged.loc[:,["ds","y"]].rename(columns= {"ds":"datetime"})
           
               
          

    else:
        st.write("Please select at least one regressor.")


if not df.empty:

    """
    ### Historical Data
    The following section displays the selected historical data.
    """
    # Display the data from the API
    st.line_chart(df.set_index("datetime"))
    st.dataframe(df)





if forecast_ready:
    
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

    if reg_coef is not None:

        """
        ### Additional Regressors
        
        """
        st.write(reg_coef)
        
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
        

