import os
from dotenv import load_dotenv
import mysql.connector
import uuid


load_dotenv()

MYSQL_DBNAME = os.getenv("RDS_NAME", "default_dbname")
MYSQL_USER = os.getenv("MASTER_USERNAME", "default_user")
MYSQL_PASS = os.getenv("MASTER_PASSWORD", "default_pass")
MYSQL_HOST = os.getenv("RDS_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("RDS_PORT", "3306")

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

class PostModel:
    def __init__(self, connection):
        self.connection = connection
    
    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS posts (
            id INT PRIMARY KEY,                
            title VARCHAR(255) NOT NULL,        
            content TEXT NOT NULL,             
            category VARCHAR(100),              
            user_id VARCHAR(255) NOT NULL,     
            user_name VARCHAR(255),             
            user_email VARCHAR(255),            
            likes_count INT DEFAULT 0,          
            shares_count INT DEFAULT 0,         
            comments_count INT DEFAULT 0,       
            first_image VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()

    def create_post(self, post_data):
        try:
            cursor = self.connection.cursor()

            post_query = """
                INSERT INTO posts (
                    id, title, content, category, user_id, user_name, user_email, 
                    likes_count, shares_count, comments_count, first_image, created_at
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            post_data_tuple = (
                post_data.id if post_data.id else str(uuid.uuid4()), 
                post_data.title,
                post_data.content,
                post_data.category,
                post_data.user_id,
                post_data.user_name,
                post_data.user_email,
                post_data.likes_count or 0, 
                post_data.shares_count or 0, 
                post_data.comments_count or 0, 
                post_data.first_image,
                post_data.created_at
            )

            print("Post data tuple:", post_data_tuple)

            cursor.execute(post_query, post_data_tuple)
            self.connection.commit()

        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            raise Exception(f"Error inserting post into database: {e}")

        finally:
            cursor.close()

    def get_all_posts(self):
        try:
            cursor = self.connection.cursor()

            query = """
                SELECT id, title, content, category, user_id, user_name, user_email, 
                    likes_count, shares_count, comments_count, first_image
                FROM posts
                ORDER BY created_at DESC
            """
            cursor.execute(query)

            posts = cursor.fetchall()

            posts_data = []
            for post in posts:
                post_data = {
                    "id": post[0],
                    "title": post[1],
                    "content": post[2],
                    "category": post[3],
                    "user_id": post[4],
                    "user_name": post[5],
                    "user_email": post[6],
                    "likes_count": post[7],
                    "shares_count": post[8],
                    "comments_count": post[9],
                    "first_image": post[10]
                }
                posts_data.append(post_data)

            return posts_data

        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            raise Exception(f"Error fetching posts from database: {e}")
        
        finally:
            cursor.close()