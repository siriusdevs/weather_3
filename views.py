import config
from typing import Optional

def load_page(template_path: str, params: Optional[dict] = None) -> str:
    with open(template_path, 'r') as file:
        content =  file.read()
    return content.format(**params) if params else content


def cities_page(cities: list[str]) -> str:
    return load_page(config.TEMPLATE_CITIES, {'cities': cities_html(cities)})


def weather_page(weather_params: dict) -> str:
    return load_page(config.TEMPLATE_WEATHER, weather_params)


def weather_dummy_page(cities: list) -> str:
    return load_page(config.TEMPLATE_WEATHER_DUMMY, {'form_options': form_options(cities)})


def main_page() -> str:
    return load_page(config.TEMPLATE_MAIN)


def error_page() -> str:
    return load_page(config.TEMPLATE_ERROR)


def cities_html(cities: tuple[str, float, float]) -> str:
    html = '<ul>{0}</ul>'
    href = '<a href="/weather?city='
    items = []
    for city, lat, lon in cities:
        items.append(f'<li>{href}{city}">{city}</a>, lat: {lat}, lon: {lon}</li>')
    return html.format('\n'.join(items))


def form_options(values: list) -> str:
    return '\n'.join(f'<option value="{value}">{value}</option>' for value in values)
