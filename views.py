from config import TEMPLATE_CITIES, TEMPLATE_MAIN, TEMPLATE_WEATHER

def page_from_cities(cities: list[str]) -> str:
    cities = '<br>'.join(cities)
    with open(TEMPLATE_CITIES, 'r') as file:
        return file.read().format(cities=cities)


def weather_page(weather_params: dict) -> str:
    with open(TEMPLATE_WEATHER, 'r') as file:
        return file.read().format(**weather_params)


def main_page() -> str:
    with open(TEMPLATE_MAIN, 'r') as file:
        return file.read()
