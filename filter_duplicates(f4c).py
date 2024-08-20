import pandas as pd

# Load the CSV file
df = pd.read_csv('filtered_association.csv')

# Drop duplicates based on specified columns
df_unique = df.drop_duplicates(subset=['paper_id', 'mutation', 'disease', 'ethnicity'])

# Save the filtered DataFrame to a new CSV file
df_unique.to_csv('output_unique.csv', index=False)

# Print the number of rows after removing duplicates
print(f"Number of rows after removing duplicates: {len(df_unique)}")
