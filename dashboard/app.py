
import os
import ssl
import json
import urllib.request

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Smart City IoT Monitoring",
    page_icon="🌆",
    layout="wide"
)

API_URL = os.environ.get(
    "API_URL",
    "https://10.10.2.2:8000/readings?limit=10000"
)

API_KEY = os.environ["SENSOR_API_KEY"]
CERT_FILE = os.environ.get(
    "API_CERT_FILE",
    "/certs/server.crt"
)


@st.cache_data(ttl=10)
def fetch_readings():
    context = ssl.create_default_context(
        cafile=CERT_FILE
    )

    request = urllib.request.Request(
        API_URL,
        headers={"X-API-Key": API_KEY}
    )

    with urllib.request.urlopen(
        request,
        context=context,
        timeout=15
    ) as response:
        return json.load(response)["readings"]


st.title("🌆 Smart City IoT Monitoring Dashboard")
st.caption("Intel Berkeley Research Lab Sensor Dataset")

try:
    readings = fetch_readings()
except Exception as error:
    st.error(f"Unable to retrieve sensor readings: {error}")
    st.stop()

if not readings:
    st.warning("No sensor readings available.")
    st.stop()

df = pd.DataFrame(readings)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

df = df.sort_values("timestamp")

st.sidebar.header("Sensor Filters")

sensor_ids = sorted(df["sensor_id"].unique().tolist())

selected_sensors = st.sidebar.multiselect(
    "Select Sensor IDs",
    options=sensor_ids,
    default=sensor_ids
)

filtered = df[
    df["sensor_id"].isin(selected_sensors)
].copy()

if filtered.empty:
    st.warning("Select at least one sensor.")
    st.stop()

st.subheader("Sensor Overview")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Readings", len(filtered))
col2.metric(
    "Avg Temperature",
    f"{filtered['temperature'].mean():.2f} °C"
)
col3.metric(
    "Avg Humidity",
    f"{filtered['humidity'].mean():.2f} %"
)
col4.metric(
    "Avg Light",
    f"{filtered['light'].mean():.2f}"
)
col5.metric(
    "Avg Voltage",
    f"{filtered['voltage'].mean():.3f} V"
)

st.divider()

st.subheader("Temperature Over Time")
st.line_chart(
    filtered,
    x="timestamp",
    y="temperature"
)

st.subheader("Humidity Over Time")
st.line_chart(
    filtered,
    x="timestamp",
    y="humidity"
)

st.subheader("Light and Voltage")

left, right = st.columns(2)

with left:
    st.line_chart(
        filtered,
        x="timestamp",
        y="light"
    )

with right:
    st.line_chart(
        filtered,
        x="timestamp",
        y="voltage"
    )

st.subheader("Recent Sensor Readings")

st.dataframe(
    filtered.sort_values(
        "timestamp",
        ascending=False
    ).head(100),
    use_container_width=True
)

st.caption(
    "Historical sensor data replayed through "
    "FastAPI HTTPS and stored in MongoDB."
)
