# google_maps_service.py
import json
import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not GOOGLE_MAPS_API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY is not set in the environment variables")
    
async def search_restaurants_api(town: str, name: str) -> dict:
    url = 'https://places.googleapis.com/v1/places:searchText'

    # The data to be sent in the POST request
    data = {
        "textQuery": f"{name} in {town}",
        'includedType' : 'restaurant',
        'pageSize': 5
    }

    # Fields to display, from Google Maps Places API
    fields = ["id", "displayName", "formattedAddress", "nationalPhoneNumber", "servesVegetarianFood", "priceLevel", "rating"]
    fields = [f"places.{field}" for field in fields]
    fields_str = ",".join(fields)

    # The headers for the POST request
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': GOOGLE_MAPS_API_KEY,
        'X-Goog-FieldMask': fields_str
    }

    try:
        # Make the asynchronous POST request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        data = response.json()
        if 'places' in data:
            places = data['places']
            print(places)
            print(json.dumps(places, indent=2))
            return places
        else:
            print('No results:', data['status'])
            return None
    except httpx.RequestError as e:
        print('Error searching restaurants:', e)
        return None
