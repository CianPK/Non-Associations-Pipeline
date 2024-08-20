import pandas as pd

# Load the CSV file
df = pd.read_csv('successful_papers_output_filtered.csv')

# Define a function to check if the mutation column is empty or contains only an empty list
def is_empty_mutation(value):
    return pd.isna(value) or value == '[]' or value == '' or value.strip() == '[]'

# Filter the DataFrame to remove rows where the "mutation" column is empty or contains only an empty list
filtered_df = df[~df['mutation'].apply(is_empty_mutation)]

# Save the filtered DataFrame to a new CSV file
filtered_df.to_csv('output_filtered_mutation.csv', index=False)

# Print the number of rows after filtering
print(f"Number of rows after filtering: {len(filtered_df)}")