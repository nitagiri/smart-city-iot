import secrets
from fastapi import Header, Depends
import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = FastAPI(title="Smart City IoT API")
API_KEY = os.environ["SENSOR_API_KEY"]

def verify_sensor_key(x_api_key: str | None = Header(default=None)):
    if x_api_key is None or not secrets.compare_digest(
        x_api_key, API_KEY
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

mongo_user = os.environ["MONGO_ROOT_USERNAME"]
mongo_password = os.environ["MONGO_ROOT_PASSWORD"]

client = MongoClient(
    host="mongodb",
    port=27017,
    username=mongo_user,
    password=mongo_password,
    authSource="admin",
    serverSelectionTimeoutMS=5000,
)

db = client["smartcity"]
collection = db["sensor_readings"]


class SensorReading(BaseModel):
    timestamp: datetime
    epoch: int
    sensor_id: int
    temperature: float = Field(ge=-20, le=60)
    humidity: float = Field(ge=0, le=100)
    light: float = Field(ge=0)
    voltage: float = Field(gt=0)


@app.get("/health")
def health():
    try:
        client.admin.command("ping")
        return {
            "status": "ok",
            "service": "smart-city-api",
            "mongodb": "connected",
        }
    except PyMongoError:
        raise HTTPException(
            status_code=503,
            detail="MongoDB unavailable",
        )


@app.post("/readings", status_code=201)
def receive_reading(
    reading: SensorReading,
    _: None = Depends(verify_sensor_key),
):
    document = reading.model_dump()

    if document["timestamp"].tzinfo is None:
        document["timestamp"] = document["timestamp"].replace(
            tzinfo=timezone.utc
        )

    try:
        result = collection.insert_one(document)
    except PyMongoError:
        raise HTTPException(
            status_code=503,
            detail="Database write failed",
        )

    return {
        "status": "stored",
        "id": str(result.inserted_id),
        "sensor_id": reading.sensor_id,
    }


@app.get("/readings")
def get_readings(
    limit: int = 1000,
    _: None = Depends(verify_sensor_key),
):
    if limit < 1 or limit > 10000:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 10000"
        )

    readings = list(
        collection.find(
            {},
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit)
    )

    return {
        "count": len(readings),
        "readings": readings
    }
