import config

def page_from_cities(cities: list[str]) -> str:
    cities = '<br>'.join(cities)
    with open(config.TEMPLATE_CITIES, 'r') as file:
        return file.read().format(cities=cities)


def weather_page(weather_params: dict) -> str:
    with open(config.TEMPLATE_WEATHER, 'r') as file:
        return file.read().format(**weather_params)


def main_page() -> str:
    with open(config.TEMPLATE_MAIN, 'r') as file:
        return file.read()


def error_page() -> str:
    with open(config.TEMPLATE_ERROR, 'r') as file:
        return file.read()