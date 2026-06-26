from loader import load_data

df = load_data()

print("\n")
print("=" * 60)
print("DATASET INFO")
print("=" * 60)

print(df.info())

print("\nMissing Values")
print(df.isna().sum())

print("\nFirst 5 Rows")
print(df.head())

print("\nRandom Row")
print(df.sample(1).T)