from prophet import Prophet

def forecast_prophet(df, periods):
    # creating a Prophet object 
    ## optional parameters can be set here like:
    ## seasonality, changepoints, uncertainty intervals etc. see help(Prophet)
    m = Prophet(yearly_seasonality=True) 

    # fit() methods expects a dataframe with the column heads ds and y
    # fits the prophet model to the data
    m.fit(df)

    # Definition of forecast range
     ## periods: Int number of periods to forecast forward. 
     ## req: Any valid frequency for pd.date_range, such as 'D' or 'M'.
    future = m.make_future_dataframe(periods=periods, freq = "H")
    

    # Prediction
     ## expects a dataframe with dates for predictions 
     ## (created above with make_future_dataframe)
    forecast = m.predict(future)
    
    # plotting
    fig_forecast = m.plot(forecast)
    fig_comp = m.plot_components(forecast)
    
    return forecast, fig_forecast, fig_comp


def run_forecast_univariate(df, no_of_hours_to_predict):
    # Do the prediction
    df_ts = df.rename(columns = {df.columns[0]: "ds", df.columns[1]:"y"})
    forecast, fig_forecast, fig_comp = forecast_prophet(df_ts, no_of_hours_to_predict)
    return  forecast, fig_forecast, fig_comp