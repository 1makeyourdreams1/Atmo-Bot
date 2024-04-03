import sqlite3

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("database.db", check_same_thread=False)
        self.cursor = self.connection.cursor()

    def get_last_message(self, user_id):
        with self.connection:
            result = self.cursor.execute(f"SELECT last_message FROM users WHERE id = {user_id}").fetchall()
            for row in result:
                last_message = int(row[0])
            return last_message

    def set_last_message(self, user_id, last_message):
        with self.connection:
            return self.cursor.execute(f"UPDATE users SET last_message = {last_message} WHERE id = {user_id}")

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchall()
            return bool(len(result))

    def add_user(self, user_id):
        with self.connection:
            self.cursor.execute(f"INSERT INTO users ('id') VALUES ({user_id})")