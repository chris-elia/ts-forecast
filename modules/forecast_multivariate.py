from prophet import Prophet
from prophet.utilities import regressor_coefficients
from datetime import timedelta
import pandas as pd

from prophet.utilities import regressor_coefficients
from modules.fetch_data import get_weather_forecast, get_open_data_elia_df



def prepare_data_for_mv_fc(dataset, start_date, end_date, solar, wind, temp, lat,long):
    """
    Prepares and merges data for Wind and PV multivariate forecast

    Parameters
    ----------
    dataset: str
        the selected dataset identifier from the Elia Open Data Platform
    start_date: str
        The start date of the selected dataset, Format: "YYYY-MM-DD"
    end_date: str
        The end date of the selected dataset, Format: "YYYY-MM-DD"    
    solar: bool
        if True, solar data will be added as additional regressor
    wind: bool
        if True, wind data will be added as additional regressor
    temp: bool
        if True, temp data will be added as additional regressor
    lat: str
        The latitude value (Geo location) of the city for the weather forecast
    long: str
        The longitude value (Geo location) of the city for the weather forecast


    Returns
    -------
    pd.Dataframe
        a dataframe containing the selected data
    

    """
    # catch open data
    if (dataset == "ods003"): # total load
        df = get_open_data_elia_df(dataset,start_date, end_date) 
        df.set_index(df["datetime"], inplace = True)
        df = df.resample("H").mean()
        df.reset_index(inplace = True)
        
    else:  # for solar & wind 
        df = get_open_data_elia_df(dataset,start_date, end_date) 
        df = df.groupby("datetime").sum()
        df = df.resample("H").mean()
        df.reset_index(inplace = True)
        df = df.loc[:,["datetime", "mostrecentforecast"]]
        df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)

    # specifying variables
    start_date= df["datetime"].iloc[0]
    end_date = df["datetime"].iloc[-1]
    latitude = lat
    longitude = long

    # get weather forecast
    df_weather = get_weather_forecast(start_date, end_date, latitude, longitude)
    columns = []
    if solar:
        columns.append("SolarDownwardRadiation")
    if wind:  
        columns.append("WindSpeed")
    if temp:
        columns.append("Temperature")

    columns.append("datetime")
    df_weather = df_weather.loc[:,columns]    
    df_merged = merge_df_with_add_reg(df, df_weather, "datetime", "datetime")
    df_merged.rename(columns = {df.columns[0]: "ds", df.columns[1]:"y"}, inplace = True)

    return df_merged



def run_forecast_multivariate(df_merged, lat, long, forecast_horizon):

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