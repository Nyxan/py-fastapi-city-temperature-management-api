from datetime import datetime
from typing import List

from app.crud import (
    get_temperatures,
    create_temperature,
    get_cities,
    get_temperatures_by_city,
)
import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas import TemperatureCreate, Temperature

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/temperatures/", response_model=List[Temperature])
def read_temperatures(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    temperatures = get_temperatures(db, skip=skip, limit=limit)
    return temperatures


@router.get("/temperatures/", response_model=List[Temperature])
def read_temperatures_by_city(
    city_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    temperatures = get_temperatures_by_city(db, city_id=city_id, skip=skip, limit=limit)
    return temperatures


@router.post("/temperatures/update")
async def update_temperatures(db: Session = Depends(get_db)):
    cities = get_cities(db)
    async with httpx.AsyncClient() as client:
        for city in cities:
            response = await client.get(
                f"https://api.weatherapi.com/v1/current.json?key=YOUR_API_KEY&q={city.name}"
            )
            data = response.json()
            temperature = data["current"]["temp_c"]
            temp_data = TemperatureCreate(
                city_id=city.id, date_time=datetime.now(), temperature=temperature
            )
            create_temperature(db=db, temperature=temp_data)
    return {"status": "temperatures updated"}
