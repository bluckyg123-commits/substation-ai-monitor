"""Receives ESP32 readings, runs the AI model, logs to live.csv, replies with trip command.
Run:  python server.py   (PC and ESP32 must be on same WiFi)"""
import csv, os, time, joblib, pandas as pd
from flask import Flask, request, jsonify
app = Flask(__name__)
model = joblib.load("model.joblib")
F = ["input_voltage", "output_voltage", "load_current", "temperature"]
COLS = ["time"] + F + ["label", "trip"]
if not os.path.exists("live.csv"):
    csv.writer(open("live.csv", "w", newline="")).writerow(COLS)

@app.post("/data")
def data():
    d = request.get_json(force=True)
    row = pd.DataFrame([[float(d[k]) for k in F]], columns=F)
    label = str(model.predict(row)[0])
    trip = label != "Normal"
    csv.writer(open("live.csv", "a", newline="")).writerow(
        [time.strftime("%H:%M:%S")] + [d[k] for k in F] + [label, int(trip)])
    return jsonify(label=label, trip=trip)

app.run(host="0.0.0.0", port=5000)
