# Extracting gene-disease non-associations from literature using LLMs

## Description
This project is utilising Google's Gemini-1.5-flash-latest via API to extract non-associations between genetic elements (genes & SNPs) and Crohn's disease.
The results and discussion sections of papers relevant to the query are fed to the LLM (Via Europe PMC RESTful API) with a prompt to return a JSON-like answer.
This method does produce significant false positives but the resulting "final.csv" can be easily manually verified through the excerpt provided within for each non-association. 
However, the initial csv file produce will need to go through several steps of data-wrangling to remove partial and irrelevant answers. Instructions provided below. 

## Alternative prompts, LLMs and Europe PMC RESTful API queries (diseases).
Any one of the above may be accessed and altered via 'gemini_pipeline.py' using a text editior.
This method can easily be applied to other diseases, associations and alternative LLMs may be swapped in (depending on your budget!)

## Running Pipeline (via Windows CMD)

1. **Setup and activate a virtual environment (optional)**
   - Create and activate a virtual environment if you prefer to keep dependencies isolated.

2. **Install required packages**
   - Install the necessary packages by running:
     ```cmd
     python -m pip install -r requirements.txt

3. **Enter your Gemini API Key**
   - Access 'gemini_pipeline.py' using a text editior and assign your API key to the variable "api_key" under the "## API KEY ##" section heading. 
   
4. **Run the pipeline**
   - In the same directory, run the script via:
     ```cmd
     python gemini_pipeline.py run
     ```

5. **Resume interrupted process**
   - If the process is interrupted, you can resume it by running:
     ```cmd
     python gemini_resume.py run
     ```

## Data Wrangling of Results CSV

After running the initial pipeline, follow these steps to process and refine the data. Each step takes in the previous csv and outputs a new csv,
the latter will be listed for each step. 

1. **Remove duplicate entries**:
   - Run the `remove_duplicates.py` script to eliminate any duplicate entries in the initial CSV file. 
   - Produces 'successful_papers_output_cleaned.csv'
     ```cmd
     python remove_duplicates.py
     ```

2. **Filter for unique disease entries**:
   - Use the `unique_disease.py` script to see how many unique diseases have been listed, this can help you tweak the following "filter_diseases.py".
     ```cmd
     python unique_disease.py
     ```

3. **Filter relevant diseases**:
   - Run `filter_diseases.py` to filter out diseases that are not relevant to Crohn's disease.
   - Produces 'successful_papers_output_filtered.csv'.
     ```cmd
     python filter_diseases.py
     ```

4. **Filter mutations**:
   - Use `filter_mutation.py` to remove entries related to mutations that are empty.
   - Produces 'output_filtered_mutation.csv'.
     ```cmd
     python filter_mutation.py
     ```

5. **Filter for SNPs and gene entries**:
   - Execute `snp_gene_filter.py` utilises regex patterns to remove any results not gene or snp related. 
   - Produces 'genes_snps.csv'.
     ```cmd
     python snp_gene_filter.py
     ```

6. **Filter associations**:
   - Run `filter_association.py` to filter out any unwanted associations from the dataset.
   - Produces 'filtered_association.csv'.
     ```cmd
     python filter_association.py
     ```

8. **Remove any remaining duplicates**:
   - Use `filter_duplicates(f4c).py` to ensure all duplicate entries have been removed from the dataset.
   - Produces 'output_unique.csv'. 
     ```cmd
     python filter_duplicates(f4c).py
     ```

9. **Process gene data**:
   - Finally, run `gene_processing.py` to remove any remaining results that are not genes nor SNPs by utilising "biomart_genes.csv".
   - Produces 'final.csv'. 
     ```cmd
     python gene_processing.py
     ```

After completing these steps, the `final.csv` file will be ready for manual verification. 

## 👥 Author

- **CianPK** - [GitHub](https://github.com/CianPK)

