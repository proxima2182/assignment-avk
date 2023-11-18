import math
import os
import traceback
from datetime import datetime

import mysql.connector
import mysql.connector.pooling
import numpy as np

try:
    config = {
        'host': os.environ.get('DB_HOST'),
        'port': os.environ.get('DB_PORT'),
        'user': os.environ.get('DB_USERNAME'),
        'password': os.environ.get('DB_PASSWORD'),
        'database': os.environ.get('DB_DATABASE'),
        'charset': 'utf8',
    }
    pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="database", pool_size=3,
                                                       auth_plugin='mysql_native_password', **config)
except Exception as e:
    pool = e
    traceback.print_exc()


class Database:
    @staticmethod
    def read(table_name, id):
        def callback(conn, cursor):
            cursor.execute(f"SELECT * FROM {table_name} where id = ?", [id])
            return cursor.fetchall()

        rows = execute_sql(callback)
        json_data = []
        for row in rows:
            data = {}
            for key in row:
                value = row[key]
                if isinstance(value, bytes) or isinstance(value, bytearray):
                    data[key] = value.decode('utf-8')
                elif isinstance(value, datetime):
                    data[key] = value.strftime("%Y-%m-%d, %H:%M:%S")
                else:
                    data[key] = value
            json_data.append(data)
        return json_data

    @staticmethod
    def insert_bulk(table_name, data, chunk_size=1000):
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

        return execute_sql_transaction(callback)

    @staticmethod
    def update(table_name, id, data):
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
                query += prefix + f"{column}=?"
                values.append(data[column])
                prefix = ","

            cursor.execute(f"UPDATE {table_name} SET {query} WHERE id= ?", values + [id])

        return execute_sql_transaction(callback)

    @staticmethod
    def delete(table_name, id):
        def callback(conn, cursor):
            cursor.execute(f"DELETE FROM {table_name}  WHERE id = ?", [id])

        return execute_sql(callback)


def get_columns(table_name):
    def callback(conn, cursor):
        cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'{table_name}'"
                       f" AND TABLE_SCHEMA = '{os.environ.get('DB_DATABASE')}' ORDER BY ORDINAL_POSITION")
        return cursor.fetchall()

    result = execute_sql(callback)
    result = [x['COLUMN_NAME'] for x in result]

    return result


def execute_sql(callback):
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


def execute_sql_transaction(callback):
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
