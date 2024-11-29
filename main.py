from fastapi import FastAPI, HTTPException
from models import connect, SubscriptionModel, PostModel
from emails.emails import send_welcome_email, send_newsletter
from celery.result import AsyncResult
from app import celery
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://52.65.28.64:8080", # sso public
    "http://52.65.190.185:8000", # server public
    "https://sso.ezgroups.com.vn", # sso domain
    "https://blog.ezgroups.com.vn", # server domain
    "https://ezgroups.com.vn", # FE domain
    "https://ezlife-real-estate-frontend.vercel.app", # FE vercel domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   
    allow_credentials=True,  
    allow_methods=["*"],  
    allow_headers=["*"],  
)

connection = connect()
subscription_model = SubscriptionModel(connection)
post_model = PostModel(connection)

class PostCreateRequest(BaseModel):
    id: int
    title: str
    content: str
    category: str
    user_id: str
    user_name: str
    user_email: str
    likes_count: Optional[int] = 0
    shares_count: Optional[int] = 0
    comments_count: Optional[int] = 0
    first_image: str
    created_at: Optional[datetime] = None
    class Config:
        orm_mode = True

subscription_model.create_table()
post_model.create_table()

@app.get("/subscribers")
def get_subscribers():
    try:
        return subscription_model.get_all_subscriptions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/subscribers")
async def create_subscriber(sub_email: str):
    try:
        send_welcome_email(sub_email)
        return subscription_model.add_subscription(sub_email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-newsletter/")
def send_newsletter_to_all():
    try:
        print("(0) Start sending newsletters to all...")
        result = send_newsletter(connection)
        return {"message": "Newsletter sent successfully to all subscribers"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/check-task/{task_id}")
async def check_task_status(task_id: str):
    try:
        result = AsyncResult(task_id, app=celery)

        if result.state == 'SUCCESS':
            return {"status": "Success", "result": result.result}
        elif result.state == 'FAILURE':
            return {"status": "Failure", "error": str(result.result)}
        else:
            return {"status": result.state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking task status: {str(e)}")

@app.post("/posts/")
async def create_post(post: PostCreateRequest):
    try:
        post_model.create_post(post_data=post)
        return {"message": "Post and images added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while creating post: {e}")
    
@app.get("/posts/")
async def get_posts():
    try:
        posts = post_model.get_all_posts() 
        return {"posts": posts}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while fetching posts: {e}")
