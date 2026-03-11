import pandas as pd

# load dataset
data = pd.read_csv("data/fraud_dataset.csv")

# remove missing values
data = data.dropna()

# convert categorical columns to numeric
data = pd.get_dummies(data)

print("Dataset preview:")
print(data.head())

# save cleaned dataset
data.to_csv("data/processed_dataset.csv", index=False)

print("Processed dataset saved.")