from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader
import smtplib
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from email.message import EmailMessage
from django.template.loader import render_to_string
import requests
from models import SubscriptionModel  
from celery import shared_task

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

template_env = Environment(loader=FileSystemLoader("templates"))

def send_welcome_email(user_email: str):
    subject = "Welcome to Our Service"
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

API_SERVICE_URL = os.getenv('API_SERVICE_URL')

def get_post_and_images():
    print("(2) At emails.get_post_and_images...")
    try:
        posts = requests.get(f"{API_SERVICE_URL}/api/v1/posts").json()[:6]
        posts_data = []

        for post in posts:
            post_id = post.get('id')
            if not post_id:
                continue  
            
            post_images = requests.get(f"{API_SERVICE_URL}/api/v1/posts/{post_id}/images").json()

            if post_images:
                images = [{"url": image['image_url'], "label": image.get('label', 'No label available')} for image in post_images]
            else:
                images = [{'url': 'https://ezgroup-static-files-bucket.s3.ap-southeast-2.amazonaws.com/media/1/Screenshot+2024-06-25+130353.png', 'label': 'Default Image'}]

            posts_data.append({
                "title": post.get('title', 'No Title'),
                "content": post.get('content', 'No Content'),
                "category": post.get('category', 'Uncategorized'),
                "author_name": post.get('user_name', 'Anonymous'),
                "last_modified": post.get('last_modified', 'Unknown'),
                "first_image": images[0] if images else images, 
            })

        return posts_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return []

@shared_task
def send_newsletter():
    print("(3) At emails.send_newsletter...")
    subscriptions = SubscriptionModel.objects.all() 
    posts_data = get_post_and_images()
    subject = "Latest Blog Posts Newsletter"
    html_message = render_to_string("newsletter.html", {"posts": posts_data})

    for subscription in subscriptions:
        user_email = subscription.sub_email

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
