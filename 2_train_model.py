import pandas as pd, joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_csv("substation_dataset.csv")
FEATURES = ["input_voltage", "output_voltage", "load_current", "temperature"]
X_tr, X_te, y_tr, y_te = train_test_split(df[FEATURES], df.label, test_size=0.2, stratify=df.label, random_state=0)
model = RandomForestClassifier(n_estimators=150, random_state=0).fit(X_tr, y_tr)
pred = model.predict(X_te)
print(classification_report(y_te, pred)); print(confusion_matrix(y_te, pred))
joblib.dump(model, "model.joblib"); print("saved model.joblib")
