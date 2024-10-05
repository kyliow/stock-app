import pandas
import streamlit
import plotly.express as px


def main():
    streamlit.title("Candlestick Lookback Analysis App")

    file = streamlit.file_uploader("Upload excel here", type=["xlsx"])
    if file is None:
        streamlit.warning("No excel file given!", icon="❗")
        return None

    df = pandas.read_excel(file, skiprows=[0])

    streamlit.write("### Whole dataset")
    df = df[["time", "open", "high", "low", "close", "Order", "Entry", "Exit"]]
    streamlit.write(df)

    # Get all the rows where 'Order' is either 'L' or 'S'
    entries_and_exits = df[df["Order"].isin(["L", "S"]) | (df["Entry"] == "OUT")]

    streamlit.write("### Entries and exits")
    streamlit.write(entries_and_exits)
    streamlit.metric("Number of entries and exits: ", value=len(entries_and_exits))

    streamlit.write("### Lookback analysis")
    col1, col2, col3 = streamlit.columns(3)
    lookback_min = col1.number_input("Minimum lookback value: ", value=150)
    lookback_max = col2.number_input("Maximum lookback value: ", value=350)
    lookback_interval = col3.number_input("Lookback interval: ", value=20)

    N_lookback_range = range(lookback_min, lookback_max + 1, lookback_interval)
    total_profits = []

    is_generate_analysis = streamlit.button("Generate analysis", type="primary")
    progress_bar = streamlit.progress(0.0)

    if not is_generate_analysis:
        return None

    lookback_range_len = len(N_lookback_range)
    for i, N_lookback in enumerate(N_lookback_range):
        progress_bar.progress(i / lookback_range_len, text="Analysis in progress.")
        profits = []
        iterator = entries_and_exits.iterrows()
        for index, row in iterator:
            lookback_index = index - N_lookback
            exit_index, exit_row = next(iterator)

            if row["Order"] == "L":
                optim_price = (
                    max(
                        [
                            df.iloc[lookback_index + i : index + i]["high"].max()
                            for i in range(1, exit_index - index + 1)
                        ]
                    )
                    + 0.1
                )
                is_second_order = (
                    df.iloc[index : exit_index + 1]["high"] >= optim_price
                ).any()

            else:
                optim_price = (
                    min(
                        [
                            df.iloc[lookback_index + i : index + i]["low"].min()
                            for i in range(1, exit_index - index + 1)
                        ]
                    )
                    - 0.1
                )
                is_second_order = (
                    df.iloc[index : exit_index + 1]["low"] <= optim_price
                ).any()

            if is_second_order:
                price_diff = (row["Entry"] + optim_price) / 2 - exit_row["Exit"]
            else:
                price_diff = row["Entry"] - exit_row["Exit"]

            if row["Order"] == "S":
                price_diff *= -1

            profits.append(price_diff)

        total_profits.append(sum(profits))

    progress_bar.progress(1.0, "Analysis complete.")

    fig = px.line(x=N_lookback_range, y=total_profits)
    fig.update_layout(xaxis_title="Lookback range", yaxis_title="Total profit")
    streamlit.plotly_chart(fig)

    percentage_diff = (max(total_profits) / min(total_profits) - 1) * 100
    streamlit.metric(
        "Percentage difference between max and min", value=f"{percentage_diff:.2f}"
    )


if __name__ == "__main__":
    main()
