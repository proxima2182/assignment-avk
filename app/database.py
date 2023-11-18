import os
import traceback
from datetime import datetime

import mysql.connector
import mysql.connector.pooling

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
except Exception:
    traceback.print_exc()


class Database:
    @staticmethod
    def read(query, values=[]):
        print("start >> query \"" + query + "\"")
        if pool is None:
            print("can't execute")
            return
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, values)
        rows = cursor.fetchall()
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
        cursor.close()
        conn.close()
        print("finish >> query \"" + query + "\"")
        # return rows
        return json_data

# def readBulk(query, values, chunk_size=20000):
#     print("start >> query \"" + query + "\"")
#     if pool is None:
#         print("can't execute")
#         return
#     offset = 0
#     result = pd.DataFrame()
#     previous_length = chunk_size
#     while previous_length == chunk_size:
#         conn = pool.get_connection()
#         try:
#             cursor = conn.cursor(dictionary=True)
#             offset_query = query + " LIMIT " + str(chunk_size) + " OFFSET " + str(offset * chunk_size)
#             print("read (" + str(offset) + ")")
#             cursor.execute(offset_query, values)
#             output = cursor.fetchall()
#             outputs = [result, pd.DataFrame(output)]
#             result = pd.concat(outputs)
#             offset += 1
#             previous_length = len(output)
#             cursor.close()
#         except Exception:
#             traceback.print_exc()
#         conn.close()
#     print("finish >> query \"" + query + "\"")
#     return result
#
#
# def write(query, values):
#     if pool is None:
#         print("can't execute")
#         return
#     conn = pool.get_connection()
#     try:
#         cursor = conn.cursor(prepared=True)
#         conn.start_transaction()
#         if values is not None and isinstance(values, list):
#             cursor.executemany(query, values)
#         else:
#             cursor.executemany(query, [values])
#         conn.commit()
#     except Exception:
#         traceback.print_exc()
#         conn.rollback()
#     cursor.close()
#     conn.close()
#     return
#
#
# def __getColumns(table_name):
#     conn = pool.get_connection()
#     try:
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute(
#             "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'" + table_name + "' AND TABLE_SCHEMA = 'data_preprocessing' ORDER BY ORDINAL_POSITION",
#             [])
#         result = cursor.fetchall()
#     except Exception:
#         traceback.print_exc()
#     cursor.close()
#     conn.close()
#
#     result = [x['COLUMN_NAME'] for x in result]
#
#     return result
#
#
# def writeBulk(table_name, frame, chunk_size=1000):
#     if pool is None:
#         print("can't execute")
#         return
#
#     table_columns = __getColumns(pool, table_name)
#     mat_columns = frame.keys().values
#     columns = []
#
#     for tc in table_columns:
#         if len(np.where(mat_columns == tc)[0]) != 0:
#             columns.append(tc)
#
#     frame = frame[columns]
#
#     column_query = ""
#     value_query = ""
#     prefix = ""
#     for column in columns:
#         column_query += prefix + column
#         value_query += prefix + "?"
#         prefix = ","
#
#     base_query = "INSERT INTO " + table_name + "(" + column_query + ") VALUES"
#     query = base_query
#     # values = [tuple(x) for x in frame.values]
#     values = np.array(frame.values, dtype=object).astype(str)
#
#     values_length = len(values)
#     loop = math.floor(values_length / chunk_size)
#     if values_length % chunk_size != 0:
#         loop += 1
#
#     prefix = ""
#     for i in range(chunk_size):
#         query += prefix + "(" + value_query + ")"
#         prefix = ","
#
#     conn = pool.get_connection()
#     try:
#         cursor = conn.cursor(prepared=True)
#
#         conn.start_transaction()
#         for i in range(loop):
#             chunk_values = []
#             if i + 1 == loop:
#                 query = base_query
#                 prefix = ""
#                 for j in range(values_length % chunk_size):
#                     query += prefix + "(" + value_query + ")"
#                     prefix = ","
#                 # cursor.executemany(query, values[i * chunk_size:])
#                 for x in values[i * chunk_size:]:
#                     chunk_values = np.concatenate((chunk_values, x), axis=0)
#             else:
#                 for x in values[i * chunk_size:(i + 1) * chunk_size]:
#                     chunk_values = np.concatenate((chunk_values, x), axis=0)
#             cursor.execute(query, tuple(chunk_values))
#
#         conn.commit()
#     except Exception:
#         traceback.print_exc()
#         conn.rollback()
#     cursor.close()
#     conn.close()
#     return
