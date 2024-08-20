import pandas as pd
import re
import ast

# Load the CSV file
df = pd.read_csv('output_filtered_mutation.csv')

# Regular expressions for gene symbols and SNPs
gene_pattern = re.compile(r'^[A-Za-z0-9_-]+$')  # Updated pattern for gene symbols
snp_pattern = re.compile(r'^rs\d+$')  # Pattern for SNPs (rs followed by digits)

# Function to check if the mutation list contains only genes or SNPs
def is_valid_mutation(mutation_list):
    if isinstance(mutation_list, str):
        try:
            mutation_list = ast.literal_eval(mutation_list)
        except (ValueError, SyntaxError):
            return False
    return all(gene_pattern.match(item) or snp_pattern.match(item) for item in mutation_list)

# Filter the DataFrame
filtered_df = df[df['mutation'].apply(is_valid_mutation)]

# Save the filtered DataFrame to a new CSV file
filtered_df.to_csv('genes_snps.csv', index=False)

# Print the number of rows after filtering
print(f"Number of rows after filtering: {len(filtered_df)}")
