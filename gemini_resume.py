import requests
import xml.etree.ElementTree as ET
import google.generativeai as genai #Gemini specific
import pathlib                      #Gemini specific
import json                         #Gemini specific
import re #gemini JSON 
import csv #data storage 
import pandas as pd #data wrangling
from tqdm import tqdm #progress bar


from my_functions import *


## DATA STORAGE SECTION ##  

failed_papers_list = []
error_papers_list = []
successful_papers_list = []

## API KEY ##

api_key =""

## Pipeline Start ##

query = "Crohn's Disease Genetics"

pmcid_list = get_pmc_ids(query= query)

last_processed_paper_id = resume_csv() # Checks which paper was the last processed according to the successful csv

pmcid_resume_list = resume_loop(last_processed_paper_id = last_processed_paper_id, pmcid_list = pmcid_list)

for paper in tqdm(pmcid_resume_list, desc="Resuming Processing Papers"):
    XML_content = XML(paper)

    if XML_content != None: #Some "papers" returned from Europe PMC are not available. 

        #abstract_extracted = "Abstract Section: " + extractify(XML_content) + "\n" # Extracts abstract if available
    
        results_extracted = "Results Section: " + resultsify(XML_content) + "\n"   # Extracts results section if available

        # ar_extracted = abstract_extracted + results_extracted # Combines abstract and results section for LLM.

        discussion_extracted = "Discussion Section: " + discussionify(XML_content) + "\n" # Extracts discussion section if available

        # ad_extracted = abstract_extracted + discussion_extracted # Combines abstract and discussion section for LLM.

        rd_extracted = results_extracted + discussion_extracted # Combines results and discussion section for LLM.

        # If the user wishes to alter the sections extracted and provided to the LLM, this can be done by editing the code above.
            

        prompt = """You are a scientific bot designed to find non-associations between specific genes or genetic mutations/variants and only Crohn's disease in regards to ethnicity from unstructured text found scientific papers.

    Non-associations are defined as no significant or lack of a significant relationship between Crohn's disease and a gene or genetic mutation. For example, a non-association between a certain gene mutation and Crohn's disease indicates that the presence or absence of the mutation does not significantly affect the likelihood of developing the disease.

    Treat Crohn's disease as a separate entity to Inflammatory Bowel Disease. 

    Be cautious in your classification of non-associations. Only classify a relationship as a non-association if it is explicitly clear in the text that no significant relationship between the gene or genetic mutation and Crohn's disease was found. 

    In the following section, if genetic non-associations with Crohn's disease that are explicitly clear in the text are present, respond with this schema:

    {
      "mutation": list[str],
      "disease": str,
      "ethnicity": str,
      "association": str,
      "quote": str
    }

    else, respond with this schema:

        {"status": "This paper does not cover genetic mutation and disease association."}
    """


        user_message = prompt + '\n' + rd_extracted # combines prompt with previously extracted sections from papers.

        # Send the request to the model
        genai.configure(api_key=api_key) ##ENTER API KEY

        # Initialise the model
        model = genai.GenerativeModel("gemini-1.5-flash-latest", generation_config={ "temperature": 0.0, "response_mime_type": "application/json"})

        raw_response = model.generate_content(user_message) # Unparsed response from LLM.

        try: 
            response = extract_json(raw_response._result.candidates[0].content.parts[0].text)
            if response:
                for obj in response: 
                    obj = (f"{paper}:{json.dumps(obj)}") 
                    sorting_hat(obj) # Decides which csv the parsed response should be recorded in.
                    print(obj)
            else: # Error handling in case there are output consistency issues (not JSON like)
                obj = (f"{paper}: (ERROR) No valid JSON found in response.")
                sorting_hat(obj) # Decides which csv the parsed response should be recorded in.
                print(obj)
        except AttributeError as e:
            obj = (f"{paper}: (ERROR) AttributeError: {e}")
            sorting_hat(obj) # Decides which csv the parsed response should be recorded in. 
            print(obj)
        except IndexError as e:
            obj = (f"{paper} : (ERROR) IndexError: {e}")
            sorting_hat(obj) # Decides which csv the parsed response should be recorded in. 
            print(obj)
        except Exception as e:
            obj = (f"{paper}: (ERROR) An unexpected error occurred: {e}")
            sorting_hat(obj) # Decides which csv the parsed response should be recorded in. 
            print(obj)

print("Job Complete")