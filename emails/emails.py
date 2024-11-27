from jinja2 import Environment, FileSystemLoader
import smtplib
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from email.message import EmailMessage
from django.template.loader import render_to_string
import requests
from models import SubscriptionModel, PostModel
from celery import shared_task

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

print("Template env flag")
template_env = Environment(loader=FileSystemLoader("templates"))

def send_welcome_email(user_email: str):
    subject = "Welcome to Our Service"
    print("Welcome template flag")
    template = template_env.get_template("greetings.html")
    message = template.render(user_email=user_email)
    
    email = EmailMessage()
    email.set_content(message, subtype="html")
    email["Subject"] = subject
    email["From"] = DEFAULT_FROM_EMAIL
    email["To"] = user_email

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(email)
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    return True

def get_post_and_images(connection):
    print("(2) At emails.get_post_and_images...")
    try:
        post_model = PostModel(connection)
        posts = post_model.get_all_posts()  
        
        if len(posts) > 6:
            posts = posts[:6] 

        posts_data = []
        for post in posts:
            first_image_url = post.get("first_image", "")
            posts_data.append({
                "title": post.get("title", ""),
                "content": post.get("content", ""),
                "category": post.get("category", ""),
                "author_name": post.get("user_name", ""),
                "last_modified": post.get("last_modified", ""),
                "first_image": first_image_url
            })

        return posts_data
    except Exception as e:
        print(f"Error fetching posts from the database: {e}")
        return []

@shared_task
def send_newsletter(connection):
    print("(3) At emails.send_newsletter...")
    try:
        subscription_model = SubscriptionModel(connection=connection)
        subscriptions = subscription_model.get_all_subscriptions()

        posts_data = get_post_and_images(connection)
        subject = "Latest Blog Posts Newsletter"
        print("Newsletter template flag")

        template = template_env.get_template("newsletter.html")

        print(subscriptions)
        print(posts_data)
        for subscription in subscriptions:
            user_email = subscription['sub_email']
            html_message = template.render(user_email=user_email, posts=posts_data)

            email = EmailMessage()
            email.set_content(html_message, subtype="html")
            email["Subject"] = subject
            email["From"] = DEFAULT_FROM_EMAIL
            email["To"] = user_email

            try:
                with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                    server.starttls()  
                    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
                    server.send_message(email)
                    print(f"Email sent to {user_email} successfully!!!")
            except Exception as e:
                print(f"Error sending email to {user_email}: {e}")
                continue
    except Exception as e:
        print(f"Error in send_newsletter task: {e}")

