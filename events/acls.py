
from .keys import PIXEL_API_KEY, OPEN_WEATHER_API_KEY
import json, requests



# funcs that send requests and clean the data returned


# get location image
def get_location_image(city, state):
    print("getting location url")

    url = f"https://api.pexels.com/v1/search?query={city},{state}&per_page=1"
    headers = { "authorization": PIXEL_API_KEY }
    response = requests.get(url,headers=headers)

    response = json.loads(response.content)

    if "status" in response:
        return None
    else:
        img_url = response["photos"].pop()["url"]
        return(img_url)



def get_weather(location):


        # location object
    city,state = location.city,location.state.abbreviation
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{state},US&appid={OPEN_WEATHER_API_KEY}"
        # api call for lat/long

    geo_response = requests.get(geo_url)


    geo_response = json.loads(geo_response.content)

    # check if lat/long was returned
    if geo_response == []:
        return None
    else:
        geo_response = geo_response.pop()

    # check if lat/long are present
    try:
        lat,lon = geo_response["lat"],geo_response["lon"]
    except KeyError:
        return None

        # api call for weather data
    weather_url = f"https://api.openweathermap.org/data/2.5/weather"
    weather_params = {
        "lat": lat,
        "lon": lon,
        "units": "imperial",
        "appid": OPEN_WEATHER_API_KEY,
    }

    weather_response = json.loads(requests.get(weather_url,params=weather_params).content)

    try:
        temp = weather_response["main"]["temp"]
        description = weather_response["weather"][0]["description"]
    except KeyError:
        return None

    weather_data = {"temp":temp,"description":description}

    return weather_data
