import os
from dotenv import load_dotenv
import mysql.connector
import uuid

load_dotenv()

MYSQL_DBNAME = os.getenv("MYSQL_DBNAME", "default_dbname")
MYSQL_USER = os.getenv("MYSQL_USER", "default_user")
MYSQL_PASS = os.getenv("MYSQL_PASS", "default_pass")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")

def connect():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DBNAME
    )

class SubscriptionModel:
    def __init__(self, connection):
        self.connection = connection

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS subscriptions (
            sub_id VARCHAR(36) PRIMARY KEY,
            sub_email VARCHAR(255) UNIQUE NOT NULL
        );
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()

    def add_subscription(self, sub_email: str):
        try:
            query = "INSERT INTO subscriptions (sub_id, sub_email) VALUES (%s, %s)"
            sub_id = str(uuid.uuid4())
            cursor = self.connection.cursor()
            cursor.execute(query, (sub_id, sub_email))
            self.connection.commit()
            return {"sub_id": sub_id, "sub_email": sub_email}
        except mysql.connector.Error as e:
            self.connection.rollback()
            raise Exception(f"Error adding subscription: {e}")

    def get_all_subscriptions(self):
        try:
            query = "SELECT sub_id, sub_email FROM subscriptions"
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [{"sub_id": row[0], "sub_email": row[1]} for row in rows]
        except mysql.connector.Error as e:
            raise Exception(f"Error fetching subscriptions: {e}")
