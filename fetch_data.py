import pandas as pd
import requests
def get_open_data_elia_df(dataset, no_rows):
    """
    params:
    
    output:
    
    """
    # parameters for the query
    dataset_url = "https://opendata.elia.be/api/records/1.0/search"
    dataset_params = {
    "dataset" : dataset,
    "rows":no_rows,
    "sort":"datetime",
    "timezone":"Europe/Berlin"
    }
    
    # calling the Elia Open Data API
    response = requests.get(dataset_url,dataset_params).json()
    
    # Converting the results to a formatted dataframe
    dfs = []
    for i in range(len(response["records"])):
        dfs.append(pd.DataFrame(response["records"][i]["fields"],index = [i]))
    dfs = pd.concat(dfs)
    dfs["datetime"] = pd.to_datetime(dfs["datetime"]).dt.tz_localize(None)
    
    return dfs


## getting the solar forecast from Realto
def get_weather_forecast(start_date, end_date, latitude, longitude):

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # Authentication
    url = "https://api.rebase.energy/weather/v2/query"
    headers = {"Authorization": "W-cRKEYdwzL6mdWCYO2_UZSOWI1MxET07dquSY9Fck4"}
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
  

  