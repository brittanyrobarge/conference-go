import json
from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY
import requests


def get_photo(city, state):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"per_page": 1, "query": city + " " + state}
    url = f"https://api.pexels.com/v1/search"
    response = requests.get(url, params=params, headers=headers)

    content = json.loads(response.content)
    try:
        return {"picture_url": content["photos"][0]["src"]["original"]}
    except (KeyError, IndexError):
        return {"picture_url": None}


def get_weather_data(city, state):
    # headers = {"Authorization": OPEN_WEATHER_API_KEY}
    params = {
        "q": city + "," + state + "," + "US",
        "appid": OPEN_WEATHER_API_KEY,
    }
    url = "http://api.openweathermap.org/geo/1.0/direct"
    response = requests.get(url, params=params)  # geo-location
    content = json.loads(response.content)
    print("GEOLOCATION JSON", content)
    try:
        latitude = content[0]["lat"]
        longitude = content[0]["lon"]
    except KeyError:
        return {
            "lat": None,
            "lon": None,
        }

    params = {"lat": latitude, "lon": longitude, "appid": OPEN_WEATHER_API_KEY}
    url = "https://api.openweathermap.org/data/2.5/weather"

    weather_response = requests.get(url, params=params)  # get-weather

    weather_content = json.loads(weather_response.content)
    # Get the main temperature and the weather's description and put
    #   them in a dictionary
    # Return the dictionary
    try:
        weather_dict = {
            "main_temperature": weather_content["main"]["temp"],
            "description": weather_content["weather"][0]["description"],
        }
        return weather_dict
    except KeyError:
        return None
