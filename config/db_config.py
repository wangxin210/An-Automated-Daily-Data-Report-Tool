import pymysql
from db_config import DB_CONFIG

class Database:

    def __init__(self):
        self.connection = None

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                charset=DB_CONFIG['charset'],
                cursorclass=pymysql.cursors.DictCursor
            )
            print("DB connection success!")
            return self.connection
        except Exception as e:
            print(f"DB connection error: {e}")
            return None

    def close(self):
        if self.connection:
            self.connection.close()
            print("DB connection is closed.")

    def get_cursor(self):
        if not self.connection:
            self.connect()
        return self.connection.cursor()

    def execute_query(self, query, params=None):
        try:
            cursor = self.get_cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            print(f"Query error: {e}")
            return []

    def execute_update(self, query, params=None):
        try:
            cursor = self.get_cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            affected_rows = cursor.rowcount
            self.connection.commit()
            cursor.close()
            return affected_rows
        except Exception as e:
            print(f"Update error: {e}")
            if self.connection:
                self.connection.rollback()
            return 0

db = Database()
