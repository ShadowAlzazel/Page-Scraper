SETTINGS = {
    "output": "cases.json", # The name of the output file
    "input": "25_0106-LEG-LegalTrainingReferenceBook.pdf", # The name of the input file
    
    "content_start": 19, # Where to start inference.
    "table_start": 5, # Where the table of content starts.
    "table_stop": 6, # Where the table of content ends.
    
    "max_scrapes": 3, # How many pages to run inference on. 
    
    "client_api": "ollama", #openai #What api to use, if openai, put in a key in keys.json 
    "model": "llama3.2:latest" # What model to use
}