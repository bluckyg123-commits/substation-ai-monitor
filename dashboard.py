"""Run:  streamlit run dashboard.py
Mode 1: Live (reads live.csv written by server.py from the ESP32)
Mode 2: Demo (replays substation_dataset.csv, no hardware needed)"""
import time, joblib, pandas as pd, streamlit as st
st.set_page_config(page_title="Substation AI Monitor", layout="wide")
F = ["input_voltage", "output_voltage", "load_current", "temperature"]
model = joblib.load("model.joblib")
mode = st.sidebar.radio("Data source", ["Live (ESP32)", "Demo (dataset replay)"])
refresh = st.sidebar.slider("Refresh (s)", 1, 5, 1)
st.title("⚡ AI-Based Substation Monitoring & Protection")

if mode.startswith("Live"):
    try: df = pd.read_csv("live.csv")
    except Exception: df = pd.DataFrame()
    if df.empty:
        st.info("Waiting for ESP32 data… start server.py and power the hardware."); time.sleep(refresh); st.rerun()
    cur = df.iloc[-1]; label = cur.label
    hist = df.tail(100)
else:
    data = pd.read_csv("substation_dataset.csv")
    i = st.session_state.get("i", 0)
    st.session_state.i = (i + 1) % len(data)
    hist = data.iloc[max(0, i - 99): i + 1].copy()
    cur = hist.iloc[-1]; label = model.predict(hist[F].tail(1))[0]

ok = label == "Normal"
(st.success if ok else st.error)(f"STATUS: {label.replace('_',' ')}" + ("" if ok else "  —  RELAY TRIPPED"))
c = st.columns(4)
c[0].metric("Input voltage", f"{cur.input_voltage:.1f} V")
c[1].metric("Output voltage", f"{cur.output_voltage:.2f} V")
c[2].metric("Load current", f"{cur.load_current:.2f} A")
c[3].metric("Temperature", f"{cur.temperature:.1f} °C")
l, r = st.columns(2)
l.subheader("Voltage"); l.line_chart(hist[["input_voltage"]].reset_index(drop=True))
r.subheader("Current & output voltage"); r.line_chart(hist[["load_current", "output_voltage"]].reset_index(drop=True))
st.subheader("Temperature"); st.line_chart(hist[["temperature"]].reset_index(drop=True))
if mode.startswith("Live"):
    st.subheader("Fault log"); st.dataframe(df[df.label != "Normal"].tail(20), use_container_width=True)
time.sleep(refresh); st.rerun()
