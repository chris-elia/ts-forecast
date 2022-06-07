import pandas as pd
import requests
import streamlit as st

def get_open_data_elia_df(dataset, start_date, end_date):
    """
    params:
    
    output:
    
    """

    url = f"https://opendata.elia.be/api/v2/catalog/datasets/{dataset}/exports/"
    json_string = f"json?where=datetime in [date'{start_date}' .. date'{end_date}']"
    print(url + json_string)
    response = requests.get(url = url + json_string)
    # calling the Elia Open Data API
    print(response.json)
    df = pd.DataFrame(response.json())
    print(df)
    df.sort_values(by = "datetime", inplace = True)
    df.reset_index(inplace = True, drop =  True)    
    df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)
    return df


## getting the solar forecast from Realto
def get_weather_forecast(start_date, end_date, latitude, longitude):

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    print("Start_date in weather_Forecast: " + str(start_date))
    print("End date in  weather_Forecast:" + str(end_date))
    # Authentication
    url = "https://api.rebase.energy/weather/v2/query"
    headers = {"Authorization": st.secrets["REBASE_KEY"]}
    params = {
        'model': 'FMI_HIRLAM',
        'start-date': start_date,
        'end-date': end_date,
        'reference-time-freq': '24H',
        'forecast-horizon': 'latest',
        'latitude': latitude,
        'longitude': longitude,
        'variables': 'Temperature, WindSpeed, SolarDownwardRadiation'
    }
    response = requests.get(url, headers=headers, params=params)
    # Clean data
    df = pd.DataFrame(response.json())
    df = df.drop('ref_datetime', axis=1)
    df["valid_datetime"] = pd.to_datetime(df["valid_datetime"]).dt.tz_localize(None)

    df = df.rename(columns={'valid_datetime': 'datetime'})
    #df = df.set_index('valid_datetime')
    df = df.drop_duplicates(keep='last')
    df = df.fillna(0)

    return df
  

  