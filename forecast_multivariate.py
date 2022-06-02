from prophet.utilities import regressor_coefficients
from prophet import Prophet
from datetime import timedelta
from prophet.utilities import regressor_coefficients

import requests
import pandas
from datetime import timedelta
from fetch_data import get_weather_forecast, get_open_data_elia_df

import logging
import sys
import pandas as pd

logger = logging.getLogger('LOG_Forecast_MV') # create logger object 


def prepare_data_for_mv_fc_total_load(dataset, start_date, end_date, solar, wind, temp, lat,long):
    """
    dataset:  API dataset id 
    
    """
    # catch open data
    df = get_open_data_elia_df(dataset,start_date, end_date) 
    df.set_index(df["datetime"], inplace = True)
    df = df.resample("H").mean()
    df.reset_index(inplace = True)
    print(df)
    # variables
    start_date= df["datetime"].iloc[0]
    end_date = df["datetime"].iloc[-1]
    latitude = lat
    longitude = long

    # get weather forecast
    print()
    logger.debug("Start_date:" + str(start_date))
    logger.debug("End_date:" + str(end_date))
    df_weather = get_weather_forecast(str(start_date), str(end_date), latitude, longitude)
    columns = []
    if solar:
        columns.append("SolarDownwardRadiation")
    if wind:  
        columns.append("WindSpeed")
    if temp:
        columns.append("Temperature")
    logger.debug("These are the selected columns" + str(columns))
    columns.append("datetime")
    df_weather = df_weather.loc[:,columns]
    
    # join dataframe
    logger.debug("this is the df" + str(df.head()))
    logger.debug("this is the weather_Df" + str(df_weather.head()))

    print("This is the weather df: " + str(df_weather))
    
    df_merged = merge_df_with_add_reg(df, df_weather, "datetime", "datetime")
    df_merged.rename(columns = {df.columns[0]: "ds", df.columns[1]:"y"}, inplace = True)
    return df_merged

def prepare_data_for_mv_fc_wind_solar(dataset, start_date, end_date, solar, wind, temp, lat,long):
    """
    dataset:  API dataset id 
    
    """
    print(dataset)
    print(start_date)
    print(end_date)
    print(solar)
    print(wind)
    print(temp)
    print(lat)
    print(long) 
    # catch open data
    df = get_open_data_elia_df(dataset,start_date, end_date) 
    print("open data df")
    print(df)
    df = df.groupby("datetime").sum()
    print(df)
    #df.set_index(df["datetime"], inplace = True)    
    df = df.resample("H").mean()
    df.reset_index(inplace = True)
    df = df.loc[:,["datetime", "mostrecentforecast"]]
    df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)

    print("This is the input df: " + str(df))

    # variables
    start_date= df["datetime"].iloc[0]
    end_date = df["datetime"].iloc[-1]
    latitude = lat
    longitude = long

    # get weather forecast
    print("fc_mv: Start_date:" + str(start_date))
    print("fc_mv: End_date:" + str(end_date))

    df_weather = get_weather_forecast(start_date, end_date, latitude, longitude)
    columns = []
    if solar:
        columns.append("SolarDownwardRadiation")
    if wind:  
        columns.append("WindSpeed")
    if temp:
        columns.append("Temperature")
    logger.debug("These are the selected columns" + str(columns))
    print("These are the selected columns" + str(columns))
    columns.append("datetime")
    df_weather = df_weather.loc[:,columns]
    print("This is the df_weatherdf" + str(df_weather))
    
    # join dataframe
    logger.debug("this is the df" + str(df.head()))
    logger.debug("this is the weather_Df" + str(df_weather.head()))
    
    df_merged = merge_df_with_add_reg(df, df_weather, "datetime", "datetime")
    df_merged.rename(columns = {df.columns[0]: "ds", df.columns[1]:"y"}, inplace = True)
    return df_merged


def forecast_prophet_multivariate(df_merged, lat, long, forecast_horizon):

    end_date = df_merged["ds"].sort_values().iloc[-1]
    logger.debug(df_merged["ds"].sort_values())
    start_date_forecast = end_date + timedelta(hours = 1)
    end_date_forecast = start_date_forecast + timedelta(hours = forecast_horizon)
    weather_forecast = get_weather_forecast(start_date_forecast, end_date_forecast, lat, long)

    m = Prophet(yearly_seasonality=True) 
    
    for each in df_merged.columns[2:]:
        m.add_regressor(each)

    # fit() methods expects a dataframe with the column heads ds and y
    # fits the prophet model to the data
    m.fit(df_merged)

    # Definition of forecast range
    ## periods: Int number of periods to forecast forward. 
    ## req: Any valid frequency for pd.date_range, such as 'D' or 'M'.
    future = m.make_future_dataframe(periods=forecast_horizon, freq = "H")
    future = merge_df_with_add_reg(future, weather_forecast, left_on = "ds", right_on="datetime")

    # Prediction
    ## expects a dataframe with dates for predictions 
    ## (created above with make_future_dataframe)
    forecast = m.predict(future)

    # plotting
    fig_forecast = m.plot(forecast)
    fig_components = m.plot_components(forecast)

    reg_coef = regressor_coefficients(m)
    
    return forecast, fig_forecast, fig_components, reg_coef



def merge_df_with_add_reg(df1, df2, left_on, right_on):
    df = df1.merge(df2, left_on= left_on, right_on = right_on)
    return df