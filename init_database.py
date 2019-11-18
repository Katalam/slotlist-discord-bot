import os, sqlite3
from sqlite3 import Error

def create_connection(db_path):
    """
    create a database connection to a SQLite database, if db is not existing it will create a new one.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
    except Error as e:
        print(e)
    finally:
        if conn:
            sql = "CREATE TABLE missions (mission_id INTEGER PRIMARY KEY, mission_name TEXT NOT NULL)"
            conn.execute(sql)
            conn.commit()
            conn.close()

if __name__ == '__main__':
    create_connection(os.path.join(os.getcwd(), "slotlist.db"))
