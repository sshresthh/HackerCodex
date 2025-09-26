from dotenv import load_dotenv
from openai import OpenAI
import googlemaps
import os
import json
import base64

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_API_KEY"))

JSON_FORMAT = """
{
    "Title": "string",
    "Description": "string",
    "Date": "string",
    "Time": "string",
    "Location": "string",
    "Longitude": "string", 
    "Latitude": "string",  
    "Organizer": "string",
    "Source": "Community Poster"
}
"""

PROMPT = f"""
    You are an expert event information extractor for an app in Adelaide, South Australia.
    Analyze the provided image of a event poster. Your one and only task is to extract the event details and return them in a clean, valid JSON object.

    Follow this exact JSON structure:
    {JSON_FORMAT}

    Strict Rules:
    - If a field is not present on the poster, return an empty string "" for its value.
    - The event is in South Australia, so use that context to identify venue names.
    - "Source" must always be "Community Poster".
    - You don't have to find the longitude and latitude, just return empty strings for them.
    - "Date" and "Time" must be in the format of a date and time.
    - "Description" must be a short description of the event.
    - "Title" must be the title of the event.
    - Do not add any text or markdown formatting before or after the JSON object.
"""

def process_image_with_openai(image_content: bytes) -> dict:
    """
    Takes image bytes, sends them to GPT-4o, and asks it to return structured JSON.
    It both reads the poster and structures the data.
    """
    base64_image = base64.b64encode(image_content).decode('utf-8')
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )

        json_string = response.choices[0].message.content
        return json.loads(json_string)

    except Exception as e:
        print(f"Error calling the OpenAI API: {e}")
        return None

def get_coordinates_from_location(location_string: str) -> dict:
    """
    Takes a location string and uses the Google Geocoding API to find its precise latitude and logitute locatons.
    """
    if not location_string:
        return {
            "Latitude": "",
            "Longitude": ""
        }

    try:
        geocode_result = gmaps.geocode(f"{location_string}, South Australia")

        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return {
                "Latitude": str(location['lat']),
                "Longitude": str(location['lng'])
            }

    except Exception as e:
            print(f"Error during geocoding: {e}")
    return {
        "Latitude": "",
        "Longitude": ""
    }