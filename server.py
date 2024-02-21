import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Optional
from urllib.parse import unquote

import db
from config import *
import views
from weather import get_weather
import dotenv
import os


def json_from_cities(cities: list[tuple]) -> str:
    return json.dumps({name: {'lat': lat, 'lon': lon} for name, lat, lon in cities})


def load_creds_to_handler(class_: type) -> type:
    dotenv.load_dotenv()
    setattr(class_, 'yandex_key', os.environ.get('YANDEX_KEY'))
    connection, cursor = db.connect()
    setattr(class_, 'db_connection', connection)
    setattr(class_, 'cursor', cursor)
    return class_


class CustomHandler(SimpleHTTPRequestHandler):
    def router(self):
        if self.path.startswith('/cities'):
            return self.cities()
        elif self.path.startswith('/weather'):
            return self.weather()
        return views.main_page()

    def get_query(self) -> dict:
        quest_mark = '?'
        if quest_mark not in self.path:
            return {}
        query_text = self.path[self.path.index(quest_mark)+1:]
        query = {}
        for pair in query_text.split('&'):
            key, value = pair.split('=')
            if value.isdigit():
                query[key] = int(value)
                continue
            try:
                float(value)
            except ValueError:
                query[key] = views.plusses_to_spaces(value)
            else:
                query[key] = float(value)
        return query

    def weather(self):
        CITY_KEY = 'city'
        query = self.get_query()
        if CITY_KEY not in query.keys():
            cities = db.get_cities(self.cursor)
            return views.weather_dummy_page([city for city, _, _ in cities])
        response = db.get_city(self.cursor, query[CITY_KEY])
        if response:
            weather_params = get_weather(*response, self.yandex_key)
            weather_params['city'] = query[CITY_KEY]
            return views.weather_page(weather_params)
        return views.error_page()

    def cities(self):
        cities = db.get_cities(self.cursor)
        if GET_RETURNS == 'json':
            body = json_from_cities(cities)
        elif GET_RETURNS == 'html':
            body = views.cities_page(cities)
        else:
            body = ''
        return body

    def do_GET(self) -> None:
        self.respond(OK)
        self.wfile.write(self.router().encode())

    def respond(self, code: int, message: Optional[str] = None) -> None:
        self.send_response(code, message)
        self.send_header(HEADER_TYPE, f'text/{GET_RETURNS}')
        self.end_headers()

    def do_POST(self) -> None:
        body_len = self.headers.get(HEADER_LEN)
        if not body_len:
            self.respond(BAD_REQUEST)
            return
        try:
            body = json.loads(self.rfile.read(int(body_len)))
        except (json.JSONDecodeError, ValueError):
            self.respond(BAD_REQUEST)
            return
        if any(key not in body for key in POST_KEYS) or len(POST_KEYS) != len(body):
            self.respond(BAD_REQUEST)
            return
        if db.add_city(self.db_connection, self.cursor, tuple([body[key] for key in POST_KEYS])):
            self.respond(CREATED)
        else:
            self.respond(SERVER_ERROR, 'was not posted')

    def do_DELETE(self) -> None:
        if self.path.count('/') != 1:
            self.respond(BAD_REQUEST)
            return
        path = unquote(self.path)
        city_name = path[path.find('/')+1:]
        if db.delete_city(self.db_connection, self.cursor, city_name):
            self.respond(NO_CONTENT)
        else:
            self.respond(NOT_FOUND)


if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), load_creds_to_handler(CustomHandler))
    print(f'Server started at {HOST}:{PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped by user')
    finally:
        server.server_close()
