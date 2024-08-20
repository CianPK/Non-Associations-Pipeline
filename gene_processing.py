import pandas as pd
import re
import ast

# Load the list of gene names from the Biomart CSV file
biomart_genes_df = pd.read_csv('biomart_genes.csv')
gene_names_set = set(biomart_genes_df['Gene name'].dropna().str.upper())

# Regular expression pattern for SNPs
snp_pattern = re.compile(r'^rs\d+$')

# Function to check if the mutation list contains only valid genes or SNPs
def is_valid_mutation(mutation_list):
    if isinstance(mutation_list, str):
        try:
            mutation_list = ast.literal_eval(mutation_list)
        except (ValueError, SyntaxError):
            return False
    
    return all(item.upper() in gene_names_set or snp_pattern.match(item) for item in mutation_list)

# Load the DataFrame with the mutation column
df = pd.read_csv('output_unique.csv')

# Filter the DataFrame
filtered_df = df[df['mutation'].apply(is_valid_mutation)]

# Save the filtered DataFrame to a new CSV file
filtered_df.to_csv('final.csv', index=False)

print(f"Number of rows after filtering: {len(filtered_df)}")
