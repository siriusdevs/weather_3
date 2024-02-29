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
