import requests
import xml.etree.ElementTree as ET
import google.generativeai as genai #Gemini specific
import pathlib                      #Gemini specific
import json                         #Gemini specific
import re #gemini JSON 
import csv #data storage 
import pandas as pd #data wrangling 
import hashlib #duplicated output storage reduction


failed_papers_list = []
error_papers_list = []
successful_papers_list = []


def id(query, result_limit=20):   # Suitable for small batches of papers, this will be replace with get_pmc_ids function for pipeline which will return full pmcid_list for query via batching
    api_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": f'{query} AND (HAS_FT:Y)', # appends to search query to check if FullText is available (alt method to fullTextId parameter to restrict to PMC papers)
        "format": "json",
        "resultType": "core",
        "pageSize": result_limit
    }

    response = requests.get(api_url, params=params)
    data = response.json()

    papers = data.get('resultList', {}).get('result', [])
    pmcid_list = []
    for paper in papers:
        pmcid = paper.get('pmcid')
        if pmcid:
            pmcid_list.append(pmcid) 
    return pmcid_list

def get_pmc_ids(query, batch_size=100):
    api_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": f'{query} AND (HAS_FT:Y)',  # Ensure full text is available via "AND (HAS_FT:Y)"
        "format": "json",
        "resultType": "core",
        "pageSize": batch_size,
        "cursorMark": "*"  # Start with the initial cursor mark
    }

    pmcid_list = []
    more_results = True

    while more_results:
        response = requests.get(api_url, params=params)
        data = response.json()

        papers = data.get('resultList', {}).get('result', [])
        for paper in papers:
            pmcid = paper.get('pmcid')
            if pmcid:
                pmcid_list.append(pmcid)

        # Check if there are more results
        if 'nextCursorMark' in data:
            params['cursorMark'] = data['nextCursorMark']
        else:
            more_results = False

        # Break the loop if no more results are found
        if not papers:
            more_results = False

    return pmcid_list


def XML(pmcid):   # Returns XML structure of relevant papers if available. 
    api_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML" #posters and interviews should not be available in XML format, thus not a problem. 
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.content


def extractify(root): # Function extracts the abstract for the individual paper. 

    root = ET.fromstring(XML_content)

    abstract_element = root.find(".//abstract")

    if abstract_element is not None:
        # Extract the text content of the abstract element
        abstract_text = ET.tostring(abstract_element, method="text", encoding="unicode").strip()
        return abstract_text
    else:
        return "Not Found"

def resultsify(xml_content): # Function extracts the results section for the individual paper.
    root = ET.fromstring(xml_content)

    # Find the <abstract> element and mark it to exclude its children, this prevents the function from mistakenly extracting a results subheading from the abstract.
    abstract_element = root.find(".//abstract")
    if abstract_element is not None:
        for elem in abstract_element.iter():
            elem.tag = "exclude"

    # Find the <sec> element that has a <title> child containing the word "results"
    results_element = None
    for sec in root.findall(".//sec"):
        if sec.tag == "exclude":  
            continue

        title = sec.find(".//title")
        if title is not None and title.text is not None and "results" in title.text.lower():
            results_element = sec
            break

    if results_element is not None:
        results_text = ET.tostring(results_element, method="text", encoding="unicode").strip()
        return results_text
    else:
        return "Results section not found"


def discussionify(xml_content):
    root = ET.fromstring(xml_content)

    # Find the <abstract> element and mark it to exclude its children, this prevents the function from mistakenly extracting a discussion subheading from the abstract.
    abstract_element = root.find(".//abstract")
    if abstract_element is not None:
        for elem in abstract_element.iter():
            elem.tag = "exclude"

    # Find the <sec> element that has a <title> child containing the word "discussion"
    discussion_element = None
    for sec in root.findall(".//sec"):
        if sec.tag == "exclude":  # Skip sections within the abstract
            continue

        title = sec.find(".//title")
        if title is not None and title.text is not None and"discussion" in title.text.lower(): #added title.text is not None (this fix affected one paper 23/5/24)
            discussion_element = sec
            break
        

    if discussion_element is not None:
        discussion_text = ET.tostring(discussion_element, method="text", encoding="unicode").strip()
        return discussion_text
    else:
        return "Discussion section not found"


def extract_json(response_text):
    try:
        # Find all JSON objects in the text
        json_objects = re.findall(r'\{.*?\}', response_text)
        return [json.loads(obj) for obj in json_objects]
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Failed to extract JSON from response: {e}")
        return None


def failed_papers(response, csv_file='failed_papers_output.csv'): # if paper does not contain relevant material according to the LLM, the PMCID is recorded in this csv file. 
    if """{"status": "This paper does not cover genetic mutation and disease association."}""" in response: 
        # Extract paper ID
        paper_id = response.split(":")[0].strip()

        # Check if the paper ID is already in the failed_papers_list to avoid duplicates
        if paper_id not in failed_papers_list:
            # Add the paper ID to the failed papers list
            failed_papers_list.append(paper_id)

            # Create a new DataFrame entry with the new paper ID
            new_entry = pd.DataFrame({'Failed Papers': [paper_id]})

            try:
                # Read the existing data from the CSV file if it exists
                df_failed_papers = pd.read_csv(csv_file)

                # Combine the existing and new data
                df_combined = pd.concat([df_failed_papers, new_entry], ignore_index=True)

                # Write the combined DataFrame to the CSV file
                df_combined.to_csv(csv_file, index=False)
            except FileNotFoundError:
                # If the file does not exist, create it with the new data
                new_entry.to_csv(csv_file, index=False)
    else:
        pass


def error_papers(response, csv_file='error_papers_output.csv'): #if paper produces an error, the PMCID and error are recorded in this csv file. 
    if """: (ERROR)""" in response:

        paper_id = response.split(":")[0]  # From the LLM response, isolate paper_id
        key_error = response.split(":")[1] # Isolate the key error
        error_description = response.split(":")[2] # Isolate the description of the error

        error_papers_list.append({'paper_id': paper_id, 'key_error': key_error, 'error_description': error_description})

        # Create a new DataFrame entry with the new data
        new_entry = pd.DataFrame(error_papers_list)

        try:
            # Read the existing data from the CSV file if it exists
            df_error_papers = pd.read_csv(csv_file)

            # Combine the existing and new data
            df_combined = pd.concat([df_error_papers, new_entry], ignore_index=True)

            # Write the combined DataFrame to the CSV file
            df_combined.to_csv(csv_file, index=False)
        except FileNotFoundError:
            # If the file does not exist, create it with the new data
            new_entry.to_csv(csv_file, index=False)

        # Clear the list to avoid duplicates in future calls
        error_papers_list.clear()
    else:
        pass

def successful_papers(response, csv_file='successful_papers_output.csv'): # If the paper produces a successful response (relevant to gene-disease assocation & JSON like parsable) recorded in this csv file. 
    response = response.replace('\n', ' ')

    paper_id, json_data = response.split(":", 1)

    data_dict = json.loads(json_data)
    data_dict['paper_id'] = paper_id

    successful_papers_list.append(data_dict)

    # Define the order of columns
    columns_order = ['paper_id', 'mutation', 'disease', 'ethnicity', 'association', 'quote']

    # Create a DataFrame for the new data
    df_new = pd.DataFrame(successful_papers_list)

    # Reorder columns if necessary
    df_new = df_new[columns_order]

    try:
        # Read the existing data from the CSV file if it exists
        df_existing = pd.read_csv(csv_file)

        # Combine the existing and new data
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)

        # Write the combined DataFrame to the CSV file
        df_combined.to_csv(csv_file, index=False)
    except FileNotFoundError:
        # If the file does not exist, create it with the new data
        df_new.to_csv(csv_file, index=False)


def sorting_hat(response): # sorts the response into the correct csv-related function., 
    if """{"status": "This paper does not cover genetic mutation and disease association."}""" in response:
        failed_papers(response)
        # print(failed_papers_list)
    elif """: (ERROR)""" in response:
        error_papers(response)
        # print(error_papers_list)
    else:
        successful_papers(response)
        # print(successful_papers_list)

def resume_csv(csv_file='successful_papers_output.csv'): # When resuming loop (if pipeline is interrupted) results are appropriately recorded without rewriting previous entries. 
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        # Check if the DataFrame is not empty
        if not df.empty:
            # Get the last entry in the first column
            last_entry = df.iloc[-1, 0]
            return str(last_entry)
        else:
            return None  # If the DataFrame is empty, return None
    except FileNotFoundError:
        print("FileNotFoundError")

def resume_loop(last_processed_paper_id = "PMC10907708", pmcid_list = None): # PMC10907708 is a placeholder # searches through list of papers relevant to the API search query to find resume point (if pipeline interrupted and resumed)
    if pmcid_list is None:
        raise ValueError("pmcid_list must be provided")

    resume_point = 0

    for paper_position in range(len(pmcid_list)):
        if pmcid_list[paper_position] == last_processed_paper_id:
            resume_point = paper_position + 1 
            break
    resume_list = pmcid_list[resume_point:]
    return resume_list

def hash_output(output): # function to prevent model getting stuck in a repeating loop 
    return hashlib.md5(output.encode()).hexdigest()