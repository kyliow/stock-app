import yfinance
import streamlit

from figures import Figures

def main():
    streamlit.title("Stock Analysis App")

    stock = yfinance.Ticker("4715.KL")
    df = stock.history(period="max").reset_index()

    streamlit.write(df)
    
    Figures.show_historical_chart(data=df)
    

    


if __name__ == "__main__":
    main()
