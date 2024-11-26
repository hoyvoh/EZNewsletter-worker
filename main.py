from fastapi import FastAPI, HTTPException
from models import connect, SubscriptionModel

app = FastAPI()

connection = connect()
subscription_model = SubscriptionModel(connection)

subscription_model.create_table()

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI Subscription App!"}

@app.get("/subscribers")
def get_subscribers():
    """Fetch all subscribers."""
    try:
        return subscription_model.get_all_subscriptions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/subscribers")
def create_subscriber(sub_email: str):
    """Add a new subscriber."""
    try:
        return subscription_model.add_subscription(sub_email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
