# Page Scraper

This project uses an LLM and fitz to extract text from a PDF and use it to run inference
to get data.

## Clone the repo

Copy this from the Green code button or `https://github.com/ShadowAlzazel/Page-Scraper.git` 

1. Clone the repo 
    ```bash 
    git clone https://github.com/ShadowAlzazel/Page-Scraper.git
    ```

2. Install/Integrate LLM
    
    a. Install Ollama locally
    Here is the link to install on a local machine https://ollama.com/download 
    This will install the ollama SDK locally. Install local checkpoints seperately.

    b. To use a custom OPENAI key, copy and paste your openAI key under the `keys.json`

3. Start a python environment of your choice. 

    a. Create a virtual enviroment. 
    ```bash
    py -m venv "venv"
    ```
    b. Start the virtual enviroment.  
    ```bash
    venv\Scripts\activate
    ```

4. Install packages.
    ```bash 
    pip install -r requirements.tx
    ```

5. Run the program. 
    NOTE: Make sure there is a pdf in the pdfs folder.
    ```bash
    py main.py
    ```

Outputs will be formatted into the proper json under `cases.json`. The runtime will depend on what LLM you are running, the context size, the parameters, etc.

Config: Under `settings.py` there is a set of options for controlling what is being scraped.

Please check the settings file to configure the size of the file you want to scrape. 