import os, sys
# import openai
from openai import AzureOpenAI
# !pip install python-dotenv
from dotenv import load_dotenv
import json
from openai import OpenAI



def APIKeyManager(model_type, key_path):
    
    load_dotenv(dotenv_path=key_path, override=True)
    if model_type=='azure':
        client = AzureOpenAI(
            api_version=os.environ["AZURE_API_VERSION"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_API_KEY"],
        )
        return client
    elif model_type=='fanar':
        client = OpenAI(
            base_url = "https://api.fanar.qa/v1",
            api_key  = os.environ["FANAR_API_KEY"],
        )
        client.default_params = {"model": "Fanar-C-1-8.7B"}    
    elif model_type=='gemini':
        pass
    return client

# Load environment variables
def get_deployment():
    model_type="fanar"
    deployment = APIKeyManager(model_type, "./azure.env")
    return deployment
