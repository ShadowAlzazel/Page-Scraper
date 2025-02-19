import sys
import os 
import json
import asyncio
import PIL 
import re
import logging
from typing import Optional, Union

# Get the logger instance
logger = logging.getLogger(__name__)

from extractor import extract_text_from_pdf
from analysis import analysis_inference

# Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
logger.setLevel(logging.DEBUG)
# Create a handler to direct the logs (in this case, to the console)
stream_handler = logging.StreamHandler()
# Create a formatter to define the log message format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# Set the formatter for the handler
stream_handler.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(stream_handler)


### --------------------------------------------------------------------

SYSTEM_PROMPT = """ 
    Here I have text of pdfs that need analysis.
    Ascertain and analyze the text in each page and convert it into the following format:

    The name of the case (title) will be provided, and you will get text pertaining to that case,
    and others.   
    Return only one object inside "cases", and that object MUST be complete.

    Each case is comprised of: title, citation, facts, issue, held, discussion.
    I want a json of all the cases comprised of the above fields into:

    {
    "cases": [
        {
            "title": "",
            "citation": "",
            "facts": "",
            "issue": "",
            "held": "",
            "discussion": ""
        },
        ...etc
    ]
    }
    
  
    Only respond with the json and only the json.
"""

TABLE_OF_CONTENTS_PROMPT = """ 
    I have a table of contetns that I need to get the cases from and their respective names. 
    This is a cumulative list of all the cases, so I do NOT need sub-lists or levels.
    Do not inculde the section headers or chapters.
    
    Return the case name and only the name of the case in the list cases. Here is the format:
    {
        "cases": [
            {
                "title": "",
                "page": 123,
            },
            ...etc
        ]
    }
   
    
    Only respond with the json and only the json.
"""

SUMMARY_PROMPT = """ 
    Here I have text of pdfs that need analysis.
    Ascertain and analyze the text in each page and convert it into the following format

    Each case is comprised of: title, citation, facts, issue, held, discussion and a very brief summary.
    I want a json of all the cases comprised of the above fields into. 
    Summarize into summary.

    {
    "cases": [
        {
            "title": "",
            "citation": "",
            "facts": "",
            "issue": "",
            "held": "",
            "discussion": ""
        },
        ...etc
    ]
    }
    
    
    Only respond with the json and only the json.
"""

### --------------------------------------------------------------------

# The function to handle and process text like cleaning and removing artifacats from inference
async def process_text(text: str, sys_prompt: str):
    max_retries = 3
    for attempt in range(max_retries):
        clean_text = ""
        try:
            inf_completion = await analysis_inference(text=text, sys_prompt=sys_prompt)  # Await from API/local
            #print(inf_completion)
            
            clean_text = re.sub(r'```json|```', '', inf_completion).strip()  # Clean
            inf_data = json.loads(clean_text)  # Attempt to parse JSON
            
            return inf_data  # Return the successfully parsed data
        
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            # Fauly data
            logger.info("Fauly data:")
            print(clean_text)
            
            if attempt == max_retries - 1:
                logger.error("Skipping to the next text after multiple failures.")
                return None  # Return None or handle the failure case appropriately
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None  # Handle any unexpected errors and continue

# Main 
async def main(): 
    # vars and page paths
    file_name = "25_0106-LEG-LegalTrainingReferenceBook"
    full_path = f'pdfs/{file_name}.pdf'
    
    content_start = 19 
    table_start = 5
    table_stop = 6

    # the available cases in the pdf
    table_of_cases = {"cases": []}
    
    # Get the cases from the table of contents
    table_pages = extract_text_from_pdf(pdf_path=full_path, start=table_start, stop=table_stop)
    for p, text in enumerate(table_pages):
        inf_data = await process_text(text=text, sys_prompt=TABLE_OF_CONTENTS_PROMPT)
        if inf_data is not None:
            # Logging inf_data
            logger.info("Proccesed inference and got data: ")
            print(inf_data)
            print("")
            # Process inf_data
            # NOTE: This dict access and method will be different depending on the format 
            inf_cases = inf_data["cases"]
            table_of_cases["cases"].extend(inf_data["cases"])
        else: 
            logger.warning(f'Page ({p}) did not return good data.')

    logger.info(f"Finished extracting text of pdf file {file_name}")

    # Write to disk 
    output_path = f"outputs/table_of_cases.json"
    with open(output_path, "w") as output_file:
        output_file.seek(0)
        json.dump(table_of_cases, output_file, indent=2)

    # Extracted data from the pdf
    #text_pages = extract_text_from_pdf(pdf_path=full_path, start=19, stop=34)

    data_of_cases = {"cases": []}
    
    max_i = 10
    for i, case in enumerate(table_of_cases["cases"]):
        if i >= max_i:
            break
        
        page, title = int(case["page"]), str(case["title"])
        # Create pages, merge to teext, to then scan through then extract   
        p_start = content_start + page - 1
        print(f'Reading from PDF-Page ({p_start}) for case ({title})')
        pdf_pages = extract_text_from_pdf(pdf_path=full_path, start=p_start, stop=(p_start + 1))
        page_text = ''.join(pdf_pages)
        # Get data from text
        case_prompt = SYSTEM_PROMPT + f'The name/title of this case is ({title}).'
        inf_data = await process_text(text=page_text, sys_prompt=case_prompt)
        if inf_data is not None:
            # Logging inf_data
            logger.info("Proccesed page and got data: ")
            print(inf_data)
            print("")
            # Somtimes spits out multiple cases
            analyzed_cases = inf_data["cases"]
            for a in analyzed_cases:
                if a["title"] == title:
                    data_of_cases["cases"].append(a)
            
            #data_of_cases["cases"].extend(inf_data["cases"])
            
        i += 1
    
    # Write to disk 
    output_path = f"outputs/cases.json"
    with open(output_path, "w") as output_file:
        output_file.seek(0)
        json.dump(data_of_cases, output_file, indent=2)


if __name__ == "__main__":
    args = None
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        # Process the arguments
        for arg in args:
            print(f"Argument: {arg}")
    else:
        print("No arguments provided.")
    # Run 
    asyncio.run(main())
    