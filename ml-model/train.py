import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

df = pd.read_csv("dataset/campus_energy_dataset.csv")

X = df[["building_id","temperature","occupancy"]]
y = df["usage_kwh"]

model = LinearRegression()
model.fit(X,y)

joblib.dump(model,"../backend/model/energy_model.pkl")
print("Model saved successfully")
