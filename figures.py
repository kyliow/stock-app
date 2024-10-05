import plotly.express as px 
import pandas 
import streamlit

class Figures:
    def show_historical_chart(data: pandas.DataFrame):

        fig = px.line(data, x='Date', y='Open')
        streamlit.plotly_chart(fig)