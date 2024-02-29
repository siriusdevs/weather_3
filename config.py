YANDEX_URL = 'https://api.weather.yandex.ru/v2/informers'

HOST, PORT = '127.0.0.1', 8000

# http codes
OK = 200
BAD_REQUEST = 400
SERVER_ERROR = 500
CREATED = 201
NO_CONTENT = 204
NOT_FOUND = 404
NOT_ALLOWED = 405
FORBIDDEN = 403

# headers
HEADER_TYPE = 'Content-Type'
HEADER_LEN = 'Content-Length'
HEADER_ALLOW = ('Allow', '[GET, HEAD]')
HEADER_KEY = 'WEATHER_API_KEY'
HEADER_LOCATION = 'Content-Location'

CITY_KEYS = 'name', 'latitude', 'longtitude'
GET_RETURNS = 'html' # switch to json if you like

TEMPLATES = 'templates/'
TEMPLATE_CITIES = f'{TEMPLATES}cities.html'
TEMPLATE_MAIN = f'{TEMPLATES}index.html'
TEMPLATE_WEATHER = f'{TEMPLATES}weather.html'
TEMPLATE_ERROR = f'{TEMPLATES}error_page.html'
TEMPLATE_WEATHER_DUMMY = f'{TEMPLATES}weather_dummy.html'

WEATHER_FACT_KEYS = 'temp', 'feels_like', 'wind_speed'

PAGES_CHANGES_ALLOWED = ('/cities',)
