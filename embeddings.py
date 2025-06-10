from openai import OpenAI
import voyageai
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
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


def create_embeddings(documents):
  embeddings = []
  for doc in documents:
      allergens = remove_html_tags(doc['nutrition_information']['allergens'])
      ingredients = remove_html_tags(doc['nutrition_information']['ingredients'])
      combined_text = f"nombre: {doc['display_name']} {doc['details']['legal_name']} - descripcion: {doc['details']['description']} - ingredientes: {ingredients} - alergenos: {allergens}"
      try:
        if API_SELECTION == "openai":
          response = client.embeddings.create(
              input=combined_text,
              model="text-embedding-ada-002"
          )
          embedding = response.data[0].embedding
        elif API_SELECTION == "voyageai":
          response = vo.embed(
            texts=[combined_text],
            model="voyage-3-large",
            input_type="document",
            output_dimension=1024
          )
          embedding = response.embeddings[0]
        
        embeddings.append({"_id": doc["_id"], "embedding": embedding})
      except Exception as e:
        print(f"Error processing document {doc['_id']}: {e}")
        continue
      
  return embeddings

def upload_embeddings(embeddings):
  for emb in embeddings:
    print(f"id: {emb['_id']}")
    if API_SELECTION == "openai":
      collection.update_one({"_id": emb["_id"]}, {"$set": {"embedding": emb["embedding"]}})
    elif API_SELECTION == "voyageai":
      collection.update_one({"_id": emb["_id"]}, {"$set": {"vo_embedding": emb["embedding"]}})


def main():
  batch_size = 100
  cooldown_time = 0.4 # time in seconds
  total_documents = collection.count_documents({})
  for i in range(0, total_documents, batch_size):
    documents = list(collection.find(
      {}, 
      {
        "_id": 1, 
        "display_name": 1, 
        "details.legal_name": 1, 
        "details.description": 1, 
        "nutrition_information.ingredients": 1, 
        "nutrition_information.allergens": 1, 
        "categories.name": 1
      })
        .skip(i).limit(batch_size)
    )
    embeddings = create_embeddings(documents)
    upload_embeddings(embeddings)
    print(f"Processed batch {i // batch_size + 1} of {total_documents // batch_size}")
    time.sleep(cooldown_time)
  

if __name__ == "__main__":
  main()