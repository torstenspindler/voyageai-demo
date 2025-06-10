from openai import OpenAI
import voyageai
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import requests
import certifi
import time

# Configuration variable to select the API
API_SELECTION = "voyageai"  # Change to "voyageai" to use VoyageAI

# Load environment variables from .env file
load_dotenv(override=True)

# Set up OpenAI API Key
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
# Set up VoyageAI API Key
vo = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"], max_retries=3, timeout=10)

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
  
def remove_html_tags(text):
  if text is None:
    return ""
  return text.replace('<strong>', '').replace('</strong>', '').replace('<p>', '')
  
def upload_embeddings(embeddings):
  for emb in embeddings:
    print(f"id: {emb['_id']}")
    if API_SELECTION == "openai":
      print("todo")
      #collection.update_one({"_id": emb["_id"]}, {"$set": {"embedding": emb["embedding"]}})
    elif API_SELECTION == "voyageai":
      print(f"updating document {emb['_id']} with embedding")
      collection.update_one({"_id": emb["_id"]}, {"$set": {"vo_img_embedding": emb["embedding"]}})
  
def create_embeddings(documents):
  embeddings = []
  for doc in documents:
      ingredients = remove_html_tags(doc['nutrition_information']['ingredients'])
      ingredientes = f"ingredientes: {ingredients}"
      try:
        if API_SELECTION == "openai":
          response = client.embeddings.create(
              #input=ingredientes,
              #model="text-embedding-ada-002"
          )
          # embedding = response.data[0].embedding
        elif API_SELECTION == "voyageai":
          image_url = doc['photos']
          response = requests.get(image_url)
          image = Image.open(BytesIO(response.content))
          response = vo.multimodal_embed(
            inputs=[[f"product ingredients {ingredientes}", image]],
            model="voyage-multimodal-3",
            input_type="document",
          )
          embedding = response.embeddings[0]
        
        print(f"Embedding for document {doc['_id']} created with total tokens: {response.total_tokens}")
        embeddings.append({"_id": doc["_id"], "embedding": embedding})
      except Exception as e:
        print(f"Error processing document {doc['_id']}: {e}")
        continue # skip the document if there is an error
      
  return embeddings


def main():
  batch_size = 10
  total_documents = collection.count_documents({})
  for i in range(0, total_documents, batch_size):
    documents = list(collection.find(
      {}, 
      {
        "_id": 1, 
        "nutrition_information.ingredients": 1, 
        "photos": {
          "$arrayElemAt": ["$photos.regular", 1]
        }
      }).skip(i).limit(batch_size)
    )
    embeddings = create_embeddings(documents)
    upload_embeddings(embeddings)
    print(f"Processed batch {i // batch_size + 1} of {total_documents // batch_size}")
    time.sleep(0.4)
  

if __name__ == "__main__":
  main()