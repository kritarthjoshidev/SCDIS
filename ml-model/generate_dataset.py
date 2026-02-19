import pandas as pd
import numpy as np
from datetime import datetime, timedelta

rows = []
start = datetime(2025,1,1)

for i in range(365):
    date = start + timedelta(days=i)
    for building in range(1,6):
        temperature = np.random.uniform(20,40)
        occupancy = np.random.randint(50,500)

        usage = 0.5*temperature + 0.05*occupancy + np.random.normal(0,3)

        rows.append([date,building,temperature,occupancy,usage])

df = pd.DataFrame(rows, columns=[
    "date","building_id","temperature","occupancy","usage_kwh"
])

df.to_csv("dataset/campus_energy_dataset.csv", index=False)
print("Dataset created successfully")
