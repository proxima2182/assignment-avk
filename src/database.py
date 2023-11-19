import math
import os
import traceback
from datetime import datetime

import mysql.connector
import mysql.connector.pooling
import numpy as np

from src import app


class DatabasePool:
    def __new__(cls):
        if hasattr(cls, 'instance'):
            return cls.instance
        try:
            config = {
                'host': os.environ.get('DB_HOST'),
                'port': os.environ.get('DB_PORT'),
                'user': os.environ.get('DB_USERNAME'),
                'password': os.environ.get('DB_PASSWORD'),
                'database': os.environ.get('DB_DATABASE'),
                'charset': 'utf8',
            }
            if app.config['TESTING'] is True:
                config.update({'database': os.environ.get('DB_TEST_DATABASE')})
            cls.instance = mysql.connector.pooling.MySQLConnectionPool(pool_name="database", pool_size=5,
                                                                       auth_plugin='mysql_native_password',
                                                                       **config)
        except Exception as e:
            cls.instance = e
            traceback.print_exc()
        return cls.instance


class TestDatabasePool:
    def __new__(cls):
        if hasattr(cls, 'instance'):
            return cls.instance
        try:
            config = {
                'host': os.environ.get('DB_HOST'),
                'port': os.environ.get('DB_PORT'),
                'user': os.environ.get('DB_USERNAME'),
                'password': os.environ.get('DB_PASSWORD'),
                'database': os.environ.get('DB_TEST_DATABASE'),
                'charset': 'utf8',
            }
            cls.instance = mysql.connector.pooling.MySQLConnectionPool(pool_name="database", pool_size=3,
                                                                       auth_plugin='mysql_native_password',
                                                                       **config)
        except Exception as e:
            cls.instance = e
            traceback.print_exc()
        return cls.instance


class Database:

    @staticmethod
    def read(table_name, id, isTest=False):
        def callback(conn, cursor):
            cursor.execute(f"SELECT * FROM {table_name} where id = {id}")
            return cursor.fetchall()

        rows = execute_sql(callback, isTest)
        json_data = []
        for row in rows:
            data = {}
            for key in row:
                data[key] = parse_string(row[key])
            json_data.append(data)
        return json_data

    @staticmethod
    def insert_bulk(table_name, data, isTest=False, chunk_size=1000):
        def callback(conn, cursor):
            table_columns = get_columns(table_name)
            data_columns = data.keys().values
            columns = []

            for tc in table_columns:
                if len(np.where(data_columns == tc)[0]) != 0:
                    columns.append(tc)
            # column 이 하나도 매치 되지 않는 경우 custom error throw
            if len(columns) == 0:
                raise InternalProgrammingError("Wrong Data Input")
            frame = data[columns]

            column_query = ""
            value_query = ""
            prefix = ""
            for column in columns:
                column_query += prefix + column
                value_query += prefix + "?"
                prefix = ","

            base_query = "INSERT INTO " + table_name + "(" + column_query + ") VALUES"
            query = base_query
            values = np.array(frame.values, dtype=object).astype(str)

            values_length = len(values)
            loop = math.floor(values_length / chunk_size)
            if values_length % chunk_size != 0:
                loop += 1

            prefix = ""
            for i in range(chunk_size):
                query += prefix + "(" + value_query + ")"
                prefix = ","

            for i in range(loop):
                chunk_values = []
                if i + 1 == loop:
                    query = base_query
                    prefix = ""
                    for j in range(values_length % chunk_size):
                        query += prefix + "(" + value_query + ")"
                        prefix = ","
                    for x in values[i * chunk_size:]:
                        chunk_values = np.concatenate((chunk_values, x), axis=0)
                else:
                    for x in values[i * chunk_size:(i + 1) * chunk_size]:
                        chunk_values = np.concatenate((chunk_values, x), axis=0)
                cursor.execute(query, tuple(chunk_values))

        return execute_sql_transaction(callback, isTest)

    @staticmethod
    def update(table_name, id, data, isTest=False):
        def callback(conn, cursor):
            table_columns = get_columns(table_name)
            data_columns = list(data.keys())
            columns = []

            for tc in table_columns:
                if tc in data_columns:
                    columns.append(tc)

            # column 이 하나도 매치 되지 않는 경우 custom error throw
            if len(columns) == 0:
                raise InternalProgrammingError("Wrong Data Input")

            query = ""
            values = []
            prefix = ""
            for column in columns:
                if column != 'id':
                    query += prefix + f"{column}=?"
                    values.append(data[column])
                    prefix = ","

            cursor.execute(f"UPDATE {table_name} SET {query} WHERE id = {id}", values)

        return execute_sql_transaction(callback, isTest)

    @staticmethod
    def delete(table_name, id, isTest=False):
        def callback(conn, cursor):
            cursor.execute(f"DELETE FROM {table_name} WHERE id = {id}")

        return execute_sql(callback, isTest)


# string parser for json result
def parse_string(value):
    if isinstance(value, bytes):
        value = value.decode('utf-8')
    if isinstance(value, bytearray):
        value = bytes(value).decode('utf-8')
    elif isinstance(value, datetime):
        value = value.strftime("%Y-%m-%d, %H:%M:%S")
    return value


# to check inserted data keys are same with database column
def get_columns(table_name):
    def callback(conn, cursor):
        cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'{table_name}'"
                       f" AND TABLE_SCHEMA = '{os.environ.get('DB_DATABASE')}' ORDER BY ORDINAL_POSITION")
        return cursor.fetchall()

    result = execute_sql(callback)
    result = [x['COLUMN_NAME'] for x in result]

    return result


def execute_sql(callback, isTest=False):
    pool = TestDatabasePool() if isTest else DatabasePool()
    if isinstance(pool, Exception):
        raise pool
        return
    db_exception = None
    conn = None
    cursor = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        result = callback(conn, cursor)
        conn.commit()
    except Exception as e:
        traceback.print_exc()
        db_exception = e
    if cursor is not None:
        cursor.close()
    if conn is not None:
        conn.close()
    if db_exception is not None:
        raise db_exception
    return result


def execute_sql_transaction(callback, isTest=False):
    pool = TestDatabasePool() if isTest else DatabasePool()
    if isinstance(pool, Exception):
        raise pool
        return
    db_exception = None
    conn = None
    cursor = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(prepared=True)
        conn.start_transaction()
        result = callback(conn, cursor)
        conn.commit()
    except Exception as e:
        if conn is not None:
            conn.rollback()
        traceback.print_exc()
        db_exception = e
    if cursor is not None:
        cursor.close()
    if conn is not None:
        conn.close()
    if db_exception is not None:
        raise db_exception
    return result


class InternalProgrammingError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
