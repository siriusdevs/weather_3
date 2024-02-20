import requests
import config
import json
from exceptions import ForeignApiError


def get_weather(latitude: float, longtitude: float, yandex_key: str) -> dict:
    headers = {'X-Yandex-API-Key': yandex_key}
    coordinates = {'lat': latitude, 'lon': longtitude}
    response = requests.get(config.YANDEX_URL, headers=headers, params=coordinates)
    if response.status_code != config.OK:
        raise ForeignApiError('Yandex.Weather', response.status_code)
    fact = json.loads(response.content)['fact']
    return {key: fact[key] for key in config.WEATHER_FACT_KEYS}
