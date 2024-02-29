import os

import psycopg

import db_query

DEFAULT_PORT = 5555


def connect() -> tuple[psycopg.Connection, psycopg.Cursor]:
    port = os.environ.get('PG_PORT')
    creds = {
        'host': os.environ.get('PG_HOST', default='127.0.0.1'),
        'port': int(port) if port.isdigit() else DEFAULT_PORT,
        'dbname': os.environ.get('PG_DBNAME', default='test'),
        'user': os.environ.get('PG_USER', default='test'),
        'password': os.environ.get('PG_PASSWORD'),
    }
    connection = psycopg.connect(**creds)
    cursor = connection.cursor()
    return connection, cursor


def get_cities(cursor: psycopg.Cursor) -> list[tuple]:
    cursor.execute(db_query.CITIES_SELECT)
    return cursor.fetchall()


def get_city(cursor: psycopg.Cursor, city_name: str) -> list[tuple]:
    cursor.execute(db_query.CITY_SINGLE_SELECT, params=(city_name,))
    return cursor.fetchone()


def add_city(connection: psycopg.Connection, cursor: psycopg.Cursor, city_coord: tuple) -> bool:
    cursor.execute(db_query.CITIES_INSERT, params=city_coord)
    connection.commit()
    return bool(cursor.rowcount)


def delete_city(connection: psycopg.Connection, cursor: psycopg.Cursor, city_name: str) -> bool:
    cursor.execute(db_query.CITIES_DELETE, params=(city_name,))
    connection.commit()
    return bool(cursor.rowcount)


def check_token(cursor: psycopg.Cursor, token: str) -> bool:
    cursor.execute(db_query.CHECK_TOKEN, params=(token,))
    return bool(cursor.fetchone()[0])


def check_city(cursor: psycopg.Cursor, city: str) -> bool:
    cursor.execute(db_query.CHECK_CITY, params=(city,))
    return bool(cursor.fetchone()[0])


def update_params(attrs: list[str]) -> str:
    return ', '.join(f'{attr}=%s' for attr in attrs)


def update_city(
    connection: psycopg.Connection,
    cursor: psycopg.Cursor,
    new_attrs: dict,
    city: str
) -> bool:
    attrs, attr_values = [], []
    for attr, attr_val in new_attrs.items():
        attrs.append(attr)
        attr_values.append(attr_val)
    attr_values.append(city)
    query = db_query.UPDATE_CITY.format(params=update_params(attrs))
    cursor.execute(query, params=attr_values)
    connection.commit()
    return bool(cursor.rowcount)
