import pandas as pd

# Load the CSV file
df = pd.read_csv('successful_papers_output_cleaned.csv')

# Define the list of diseases to keep
diseases_to_keep = ["Crohn's disease", "Crohn's Disease", "Crohn's", "CD", "Crohns disease"]

# Filter the DataFrame
filtered_df = df[df['disease'].isin(diseases_to_keep)]

# Save the filtered DataFrame to a new CSV file
filtered_df.to_csv('successful_papers_output_filtered.csv', index=False)

# Print the number of rows after filtering
print(f"Number of rows after filtering: {len(filtered_df)}")