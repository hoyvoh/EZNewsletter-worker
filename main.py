from fastapi import FastAPI, HTTPException
from models import connect, SubscriptionModel
from emails.emails import send_welcome_email, send_newsletter
from celery.result import AsyncResult
from app import celery
import asyncio

app = FastAPI()

connection = connect()
subscription_model = SubscriptionModel(connection)

subscription_model.create_table()

@app.get("/subscribers")
def get_subscribers():
    try:
        return subscription_model.get_all_subscriptions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/subscribers")
async def create_subscriber(sub_email: str):
    try:
        send_welcome_email.apply_async(args=[sub_email])
        return subscription_model.add_subscription(sub_email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-newsletter/")
def send_newsletter_to_all():
    try:
        print("(0) Start sending newsletters to all...")
        result = send_newsletter.apply_async()
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
