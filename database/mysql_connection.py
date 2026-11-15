import threading
from datetime import datetime

import mysql.connector
from mysql.connector import Error

from config import Config


class MySQLConnection:
    """MySQL access with one connection per thread.

    Flask serves requests on multiple threads, and a single MySQL connection
    cannot be used concurrently (it loses sync), so each thread keeps its own.
    """

    def __init__(self):
        self._local = threading.local()

    def get_connection(self):
        """Get (or reconnect) this thread's MySQL connection"""
        connection = getattr(self._local, 'connection', None)

        if connection is not None:
            try:
                connection.ping(reconnect=True, attempts=2, delay=1)
                return connection
            except Error:
                self.close_connection()

        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE
        )
        self._local.connection = connection
        return connection

    def close_connection(self):
        """Close this thread's MySQL connection"""
        connection = getattr(self._local, 'connection', None)
        if connection is not None:
            try:
                if connection.is_connected():
                    connection.close()
            except Error:
                pass
            finally:
                self._local.connection = None

    def execute_query(self, query, params=None, fetch=True):
        """Execute a SQL query"""
        connection = self.get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(query, params or ())

            if fetch:
                result = cursor.fetchall()
                # Convert datetime objects to strings for JSON serialization
                for row in result:
                    for key, value in row.items():
                        if isinstance(value, datetime):
                            row[key] = value.isoformat()
                return result

            connection.commit()
            return cursor.lastrowid
        except Error as e:
            try:
                connection.rollback()
            except Error:
                self.close_connection()
            print(f"Error executing query: {e}")
            raise
        finally:
            cursor.close()

    def execute_many(self, query, params_list):
        """Execute multiple SQL queries"""
        connection = self.get_connection()
        cursor = connection.cursor()

        try:
            cursor.executemany(query, params_list)
            connection.commit()
            return cursor.rowcount
        except Error as e:
            try:
                connection.rollback()
            except Error:
                self.close_connection()
            print(f"Error executing batch query: {e}")
            raise
        finally:
            cursor.close()


# Global instance (thread-safe: it only holds per-thread connections)
db = MySQLConnection()
