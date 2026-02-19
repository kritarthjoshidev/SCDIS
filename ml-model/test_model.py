import joblib
import numpy as np

model = joblib.load("../backend/model/energy_model.pkl")

sample = np.array([[2, 32, 220]])
prediction = model.predict(sample)

print("Predicted usage:", prediction[0])
