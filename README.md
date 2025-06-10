# Vector Search Playground

Vector search playground with Mercasmart products catalog and VoyageAI vs OpenAI comparision

## Setup Instructions

There is a folder named `Database` with the sample documents needed to be restore to a MongoDB Database to test the application.

1. **Rename `.env.sample` to `.env` and add the values needed.**
   - You find the API keys on: 
     - https://platform.openai.com/api-keys
     - https://dashboard.voyageai.com/api-keys
     - The CLUSTER_URI is found from the 'connect to' info in Atlas
2. **Install Dependencies**:
   - Open a terminal and navigate to the top level directory of this repository
   - Create a virtual environment (optional but recommended):
     - Consider using Python 3.11 or higher
     - `python -m venv venv`
     - Activate it:
       - On macOS/Linux: `source venv/bin/activate`
   - Run the command:
     ```
     pip install -r requirements.txt
     ```

3. **Run the Application**:
   - In the terminal run:
     ```
     python app.py
     ```
   - Open a web browser and go to `http://127.0.0.1:9080/` to see the webpage with the input text.