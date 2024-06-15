import streamlit as st
import pandas as pd
import requests
import altair as alt
from interval_timer import IntervalTimer
type_of_trash = ["Organic", "Recycle"]


# Function to fetch data from API
@st.cache_data
def fetch_data(api_url):
    response_organic = requests.get(api_url + "getOrganics")
    response_recycle = requests.get(api_url + "getRecycles")
    if response_organic.status_code == 200 and response_recycle.status_code == 200:
        data_organic = response_organic.json()
        data_recycle = response_recycle.json()
        return pd.DataFrame(data_organic + data_recycle)
    else:
        # st.error(f"Failed to fetch data from API. Status code: {response_organic.status_code}")
        return pd.DataFrame()

place_holder = st.empty()

# Streamlit app
def main():
    api_url = "http://localhost:1323/"
    for interval in IntervalTimer(5):
        #re-render the chart
        with place_holder.container():
            data = fetch_data(api_url)
            # print(data)
            # Filter data based on selected trash types
            data = data[data["type"].isin(type_of_trash)]
            # st.write(data)
            summary = data.groupby(["id"]).sum().reset_index()
            print(summary)
            st.title("Trashort Data Analysis App")
            st.write("Amount of Trash Sorted by Time")

            # Count number of lines based on type and render on the current month
            count_by_month = data.groupby(["type"]).size().reset_index(name="Amount")
            # create a new column for month
            count_by_month["Month"] = pd.to_datetime("today").month

            # Filter data for the current month
            current_month = pd.to_datetime("today").month
            count_by_month = count_by_month[count_by_month["Month"] == current_month]
            st.altair_chart(
            alt.Chart(count_by_month)
            .mark_bar()
            .encode(
                # move data position to the top
                x=alt.X(
                    "Month:N",
                    scale=alt.Scale(domain=list(range(1, 13))),
                    axis=alt.Axis(labelAngle=0),
                ),
                y=alt.Y(
                    "Amount:N",
                    axis=alt.Axis(title="Amount of Trash"),
                ),
                color=alt.Color(
                    "type:N",
                    scale=alt.Scale(domain=type_of_trash),
                    legend=alt.Legend(title="Type of Trash"),
                ),
            ).properties(width=600, height=400), use_container_width=True)

if __name__ == "__main__":
    main()
