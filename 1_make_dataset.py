"""Generate a labelled dataset that matches YOUR hardware.
Edit the CONFIG numbers to match your transformer / sensors.
Better: replace/merge with the real data you logged from the ESP32 (same columns)."""
import numpy as np, pandas as pd
rng = np.random.default_rng(42)

# ---- CONFIG (change to your hardware) ----
V_IN_NOM   = 230.0   # mains input (V AC)
V_OUT_NOM  = 12.0    # transformer secondary (12-0-12 -> use 12 per half)
RATED_A    = 1.0     # transformer rated secondary current (A)
N_PER_CLASS = 3000
# -----------------------------------------

def make(label, n):
    vin = rng.normal(V_IN_NOM, 3, n)
    if label == "Normal":
        i = rng.uniform(0.05, 0.85, n) * RATED_A
    elif label == "Overload":
        i = rng.uniform(1.15, 2.0, n) * RATED_A
    elif label == "Short_Circuit":
        i = rng.uniform(3.0, 8.0, n) * RATED_A
    elif label == "Over_Voltage":
        vin = rng.uniform(1.10, 1.25, n) * V_IN_NOM
        i = rng.uniform(0.05, 0.9, n) * RATED_A
    elif label == "Under_Voltage":
        vin = rng.uniform(0.60, 0.88, n) * V_IN_NOM
        i = rng.uniform(0.05, 0.9, n) * RATED_A
    # secondary follows primary, sags with load; collapses on short circuit
    vout = V_OUT_NOM * vin / V_IN_NOM * (1 - 0.06 * i / RATED_A)
    if label == "Short_Circuit":
        vout *= rng.uniform(0.05, 0.35, n)
    # temperature rises with I^2 (heating)
    temp = 30 + 12 * (i / RATED_A) ** 2 + rng.normal(0, 1.2, n)
    return pd.DataFrame(dict(input_voltage=vin, output_voltage=vout + rng.normal(0, .08, n),
                             load_current=i + rng.normal(0, .02, n), temperature=temp, label=label))

labels = ["Normal", "Overload", "Short_Circuit", "Over_Voltage", "Under_Voltage"]
df = pd.concat([make(l, N_PER_CLASS) for l in labels]).sample(frac=1, random_state=1).reset_index(drop=True)
df["load_current"] = df["load_current"].clip(lower=0)
df.round(3).to_csv("substation_dataset.csv", index=False)
print(df.label.value_counts()); print("saved substation_dataset.csv")
