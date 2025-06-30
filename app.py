from flask import Flask, render_template, request
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import certifi
import voyageai
from openai import OpenAI
from openai import AzureOpenAI
from PIL import Image
import markdown
import os

# Load environment variables from .env file
load_dotenv(override=True)

if os.environ.get("VOYAGE_API_KEY") != None:
  # Set up VoyageAI API Key
  vo = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])
else:
  raise ValueError("No VoyageAI API key found in environment variables.")

# Decide if using OpenAI or Azure OpenAI
if os.environ.get("OPENAI_API_KEY") != None:
  # Set up OpenAI API Key and client
  client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
elif os.environ.get("AZURE_OPENAI_API_KEY") != None and \
     os.environ.get("AZURE_OPENAI_ENDPOINT") != None:
  # Set up Azure OpenAI API Key, Azure OpenAI Endpoint and client
  client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
      api_version="2024-07-01-preview",
      azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
  )
else:
  raise ValueError("No OpenAI or Azure OpenAI API key or Azure OpenAI Endpoint found in environment variables.")

# Set up MongoDB client
try: 
  mongo_client = MongoClient(
    os.getenv("CLUSTER_URI"), 
    serverSelectionTimeoutMS=5000, 
    server_api=ServerApi("1"),
    tlsCAFile=certifi.where())
  db = mongo_client["mercasmart"]
  collection = db["products"]
except Exception as e:
  print(e)

app = Flask(__name__)

def remove_html_tags(text):
  if text is None:
    return ""
  return text.replace('<strong>', '').replace('</strong>', '').replace('<p>', '')

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/images')
def about():
  return render_template('images.html')

@app.route('/search', methods=['POST'])
def search():
  query = request.form['description']
  api_selection = request.form['api_selection']
  print("RAG", request.form.get("rag"))
  is_rag = request.form.get('rag') == 'true'
  if api_selection == "openai":
    response =  client.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    )
    embedding = response.data[0].embedding
    
  elif api_selection == "voyageai" or api_selection == "voyageai_reranking":
    response = vo.embed(
      texts=[query],
      model="voyage-3-large",
      input_type="query",
      output_dimension=1024
    )
    embedding = response.embeddings[0]
    
  # print(embedding)
  # Determine the path based on the API selection
  path = "vo_vector_index" if (api_selection == "voyageai" or api_selection == "voyageai_reranking") else "vector_index"
  embedding_field = "vo_embedding" if (api_selection == "voyageai" or api_selection == "voyageai_reranking") else "embedding"
     
  # Vector Search in Atlas
  pipeline = [
    { "$vectorSearch": {
      "index": path,
      "numCandidates": 1000 if (api_selection == "voyageai_reranking") else 150,
      "path": embedding_field,
      "limit": 50 if (api_selection == "voyageai_reranking") else 5,
      "queryVector": embedding
      },
    },
    {
      "$project": {
        "_id": 0,
        "display_name": 1,
        "details.legal_name": 1,
        "details.description": 1,
        "thumbnail": 1,
        "nutrition_information.ingredients": 1,
        "price_instructions.bulk_price": 1,
        "score": { 
          "$meta": "vectorSearchScore" 
        }
      }
    }
  ]
  results = list(collection.aggregate(pipeline))
  
  if api_selection == "voyageai_reranking":
    # Transform the results to a format that VoyageAI can understand (List[str])
    inputs = []
    for doc in results:
      combined_text = f"nombre: {doc['display_name']} - ingredientes: {remove_html_tags(doc['nutrition_information']['ingredients'])}"      
      inputs.append(combined_text)
    
    # Perform reranking with VoyageAI
    rk_results = vo.rerank(
      query,
      inputs,
      model="rerank-2",
      top_k=5
    )
   
    # Return the results to the user
    for r in rk_results.results:
      print(f"Document: {r.document}")
      print(f"Relevance Score: {r.relevance_score}")
      print()
  
  # Use retrieved results to render the context for the chatGPT model
  if is_rag:
    print("rag enabled")
    context = "\n\n".join([f"{doc['display_name']} - {doc['details']['description']}" for doc in results])
    prompt = f"Using the following ingredients, providing nutrition valuable information and one recipe with those as well as the price in euros:\n{context}\nanswer the query: {query}"
    gpt_response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
          {"role": "system", "content": "You are a helpful expert nutrition and chef assistant."},
          {"role": "user", "content": prompt},
        ],
    )
    print(gpt_response) 
    chatbot_response_markdown = gpt_response.choices[0].message.content
    chatbot_response = markdown.markdown(chatbot_response_markdown)
  else:
    chatbot_response = None
  return render_template('results.html', results=results, chatbot_response=chatbot_response)


@app.route('/upload_image', methods=['POST'])
def upload_image():
  file = request.files['image']
  # api_selection = request.form['api_selection']
  if file:
    image = Image.open(file.stream)
    input = [["Esto es una imagen de un plato de comida", image]]
    
    # vectorize the image
    result = vo.multimodal_embed(input, model="voyage-multimodal-3")
        
    # Perform vector search in MongoDB
    pipeline = [
        { "$vectorSearch": {
            "index": "vo_image_index",
            "numCandidates": 250,
            "path": "vo_img_embedding",
            "limit": 10,
            "queryVector": result.embeddings[0]
        }},
        {
            "$project": {
                "_id": 0,
                "display_name": 1,
                "details.legal_name": 1,
                "details.description": 1,
                "thumbnail": 1,
                "price_instructions.bulk_price": 1,
                "score": { 
                    "$meta": "vectorSearchScore" 
                }
            }
        }
    ]
    results = list(collection.aggregate(pipeline))
    return render_template('results.html', results=results)
  
if __name__ == '__main__':
  app.run(debug=True, host="0.0.0.0", port=9080)