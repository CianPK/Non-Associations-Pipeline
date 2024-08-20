import pandas as pd

# Load the CSV file
df = pd.read_csv('genes_snps.csv')

# Filter rows where the "association" column contains "no", "non", "non-association" (case-insensitive)
filtered_df = df[df['association'].str.contains(r'\bno\b|\bnon\b|non-association', case=False, na=False)]

# Save the filtered DataFrame to a new CSV file
filtered_df.to_csv('filtered_association.csv', index=False)

# Print the number of rows after filtering
print(f"Number of rows after filtering: {len(filtered_df)}")