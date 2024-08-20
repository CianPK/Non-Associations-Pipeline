import pandas as pd

# Load the CSV file
df = pd.read_csv('successful_papers_output.csv')

# Remove duplicates based on all columns
df_unique = df.drop_duplicates()

# Save the cleaned data to a new CSV file
df_unique.to_csv('successful_papers_output_cleaned.csv', index=False)

print(f"Original rows: {len(df)}, Unique rows: {len(df_unique)}")