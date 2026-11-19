# AI Substation Monitor (ESP32 + ML + Streamlit)

pip install -r requirements.txt
python 1_make_dataset.py      # creates labelled dataset (or use your own CSV, same columns)
python 2_train_model.py       # trains model.joblib
streamlit run dashboard.py    # choose "Demo" -> works without hardware

With hardware:
1. Edit WiFi + PC IP + pins in esp32_substation.ino, flash it.
2. python server.py           (AI + logging)
3. streamlit run dashboard.py -> "Live (ESP32)"

Best accuracy: log your real readings with known faults (normal / overload / short),
add a `label` column, merge into substation_dataset.csv, re-run step 2.
Safety: never connect 230 V directly to ESP32 pins; use isolated sensors (ZMPT101B, ACS712).
