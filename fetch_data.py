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
    