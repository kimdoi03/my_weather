import requests
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


@st.cache_data(ttl=600)
def get_weather(lat, lon):
    response = requests.get(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,wind_speed_10m",
            "hourly": "temperature_2m",
            "forecast_days": 1,
            "timezone": "auto",
        },
        timeout=10,
    )

    response.raise_for_status()
    data = response.json()

    current = data["current"]
    hourly = data["hourly"]

    df = pd.DataFrame({
        "Time": pd.to_datetime(hourly["time"]),
        "Temperature (°C)": hourly["temperature_2m"],
    })

    return current, df


st.set_page_config(
    page_title="Weather Map",
    layout="centered"
)

st.title("Click the Map, Check the Weather")
st.caption("Open API Weather Service")

st.subheader("1. Select a location")

weather_map = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=7
)

map_result = st_folium(
    weather_map,
    height=400,
    width=700
)

clicked = (map_result or {}).get("last_clicked")

if not clicked:
    st.info("Click a location on the map.")
    st.stop()


lat = round(clicked["lat"], 3)
lon = round(clicked["lng"], 3)

st.subheader("2. Selected Location")

st.write(f"Latitude: {lat}")
st.write(f"Longitude: {lon}")


try:
    current, df = get_weather(lat, lon)

except requests.RequestException:
    st.error("Could not load weather data.")
    st.stop()


st.subheader("3. Current Weather")

col1, col2 = st.columns(2)

col1.metric(
    "Temperature",
    f"{current['temperature_2m']:.1f} °C"
)

col2.metric(
    "Wind Speed",
    f"{current['wind_speed_10m']:.1f} km/h"
)


st.subheader("4. Hourly Temperature")

st.line_chart(
    df.set_index("Time")
)

st.caption("Weather data provided by Open-Meteo.")
