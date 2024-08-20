import pandas as pd

# Load the CSV file
df = pd.read_csv('successful_papers_output_cleaned.csv')

# Get the unique values in the 'disease' column
unique_diseases = df['disease'].unique()

# Print the unique diseases
print("Unique diseases:")
for disease in unique_diseases:
    print(disease)
