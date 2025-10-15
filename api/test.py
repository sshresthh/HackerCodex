import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

print("Attempting to connect to Azure OpenAI...")
try:

    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT") 
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")

    DEPLOYMENT_NAME = "gpt-5-mini"
    if not AZURE_OPENAI_KEY:
        raise RuntimeError("Missing AZURE_OPENAI_KEY.")

    client = OpenAI(
        api_key=AZURE_OPENAI_KEY,
        base_url=f"{AZURE_OPENAI_ENDPOINT}openai/v1/"
    )

    response = client.responses.create(
        model=DEPLOYMENT_NAME,
        input="Hello, world!"
    )
    print("\nSuccess! The API call worked.")
    print("\nModel's response:")

    print(response.model_dump_json(indent=2))
except Exception as e:
    print(f"\nFailed. The API call did not work.")
    print("\nHere is the error message:")
    print(e)
