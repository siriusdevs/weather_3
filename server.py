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
import psycopg


def json_from_cities(cities: list[tuple]) -> str:
    return json.dumps({name: {'lat': lat, 'lon': lon} for name, lat, lon in cities})


def load_creds_to_handler(class_: type) -> type:
    dotenv.load_dotenv()
    setattr(class_, 'yandex_key', os.environ.get('YANDEX_KEY'))
    connection, db_cursor = db.connect()
    setattr(class_, 'db_connection', connection)
    setattr(class_, 'db_cursor', db_cursor)
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
            cities = db.get_cities(self.db_cursor)
            return views.weather_dummy_page([city for city, _, _ in cities])
        response = db.get_city(self.db_cursor, query[CITY_KEY])
        if response:
            weather_params = get_weather(*response, self.yandex_key)
            weather_params['city'] = query[CITY_KEY]
            return views.weather_page(weather_params)
        return views.error_page()

    def cities(self):
        cities = db.get_cities(self.db_cursor)
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

    def respond(self, code: int,
        body: Optional[str] = None,
        headers: Optional[tuple[tuple]] = None,
        message: Optional[str] = None
    ) -> None:
        self.send_response(code, message)
        self.send_header(HEADER_TYPE, f'text/{GET_RETURNS}')
        if headers:
            for header in headers:
                self.send_header(*header)
        self.end_headers()
        if body:
            self.wfile.write(body.encode())

    def read_json_body(self) -> dict | None:
        body_len = self.headers.get(HEADER_LEN)
        if not body_len:
            self.respond(BAD_REQUEST, f'you should have provided header {HEADER_LEN}')
            return None
        try:
            return json.loads(self.rfile.read(int(body_len)))
        except (json.JSONDecodeError, ValueError) as error:
            self.respond(BAD_REQUEST, f'failed decodning json: {error}')
            return None

    def is_changes_allowed(self) -> bool:
        for page in PAGES_CHANGES_ALLOWED:
            if self.path.startswith(page):
                return True
        return False
    
    def allow(self) -> bool:
        if not self.is_changes_allowed():
            self.respond(NOT_ALLOWED, headers=(HEADER_ALLOW,))
            return False
        return True

    def is_authorized(self) -> bool:
        if HEADER_KEY not in self.headers.keys():
            return False
        return db.check_token(self.db_cursor, self.headers.get(HEADER_KEY))
    
    def auth(self) -> bool:
        if not self.is_authorized():
            self.respond(FORBIDDEN)
            return False
        return True

    def allow_and_auth(self) -> bool:
        if not self.allow():
            return False
        if not self.auth():
            return False
        return True

    def do_POST(self) -> None:
        if not self.allow_and_auth():
            return
        body = self.read_json_body()
        if body is None:
            return
        if set(body.keys()) != set(CITY_KEYS):
            self.respond(BAD_REQUEST, f'this instance supports attributes {CITY_KEYS}')
            return
        try:
            response = db.add_city(self.db_connection, self.db_cursor, tuple([body[key] for key in CITY_KEYS]))
        except psycopg.errors.UniqueViolation:
            self.respond(OK, f'already exists')
            self.db_connection.rollback()
            return
        except psycopg.Error as error:
            self.respond(SERVER_ERROR, f'db error: {error}')
            self.db_connection.rollback()
            return
        if response:
            self.respond(CREATED)
        else:
            self.respond(SERVER_ERROR, 'was not posted')

    def do_DELETE(self) -> None:
        if not self.allow_and_auth():
            return
        if self.path.count('/') != 1:
            self.respond(BAD_REQUEST)
            return
        path = unquote(self.path)
        city_name = path[path.find('/')+1:]
        try:
            response = db.delete_city(self.db_connection, self.db_cursor, city_name)
        except psycopg.Error as error:
            self.respond(SERVER_ERROR, f'db error: {error}')
            self.db_connection.rollback()
            return
        if response:
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
