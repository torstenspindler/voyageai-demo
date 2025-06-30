# Vector Search Playground

Vector search playground with Mercasmart products catalog and VoyageAI vs OpenAI comparison.

## Setup Instructions

There is a folder named `Database` with the sample documents needed to be restore to a MongoDB Database to test the application. Check the README.md in the Database directory.

1. **Rename `.env.sample` to `.env` and add the values needed.**
   - The API keys needed are
     - VoyageAI
       - [VoyageAI](https://dashboard.voyageai.com/api-keys)
     - OpenAI or Azure OpenAI and Azure OpenAI endpoint
       - [OpenAI](https://platform.openai.com/api-keys)
       - [Azure Portal](https://portal.azure.com)
   - The CLUSTER_URI is found from the 'connect to' info in Atlas

2. **Install Dependencies**:
   - Open a terminal and navigate to the top level directory of this repository
   - Create a virtual environment (optional but recommended):
     - This has been tested using Python 3.11
     - `python -m venv venv`
     - Activate it:
       - On macOS/Linux: `source venv/bin/activate`
   - Run the command:

     ```bash
     pip install -r requirements.txt
     ```

3. **Run the Application**:
   - In the terminal run:

     ```bash
     python app.py
     ```

   - Open a web browser and go to `http://127.0.0.1:9080/` to see the webpage with the input text. Visit `http://127.0.0.1:9080/images` for the image based search