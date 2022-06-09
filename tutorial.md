[Anaconda]

pip install streamlit
pip install pystan==2.19.1.1
conda install prophet

[JupyterNotebook]


[Visual code studio]

streamlit run main.py


[Streamlit Cloud]
pip list --format=freeze > requirements.txt
requirement file
adapt pywin
typing extension = =3.7.4.3



## change interpreter
Shift+CRTL+P






integrated download box
"""
    st.write(now.strftime("%d/%m/%Y_%H:%M:%S"))
    col1, col2 = st.columns(2)
    col1.download_button(
        "Download your selected data source (input)",
        convert_df(df),
        f'input_data_{now.strftime("%d/%m/%Y_%H:%M:%S")}.csv',
        "text/csv",
        key="input_data_csv"
    )

    col2.download_button(
        "Download the forecast results",
        convert_df(forecast),
        f'forecast_data_{now.strftime("%d/%m/%Y_%H:%M:%S")}.csv',
        "text/csv",
        key="forecast_data_csv"
    )
    """
    or 


    https://gist.github.com/chad-m/6be98ed6cf1c4f17d09b7f6e5ca2978f