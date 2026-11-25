from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from peewee import AutoField, CharField, Model, SqliteDatabase
from pydantic import BaseModel

PROJECT_DIR = Path(__file__).resolve().parent.parent
db = SqliteDatabase(str(PROJECT_DIR / "carsweb.db"))


class BaseModelDB(Model):
    class Meta:
        database = db


class TBCars(BaseModelDB):
    id = AutoField()
    carname = CharField()
    carbrand = CharField()
    carmodel = CharField()
    carprice = CharField()


class CarCreate(BaseModel):
    carname: str
    carbrand: str
    carmodel: str
    carprice: str


class CarUpdate(BaseModel):
    carname: str | None = None
    carbrand: str | None = None
    carmodel: str | None = None
    carprice: str | None = None


def serialize_car(car: TBCars) -> dict[str, int | str]:
    return {
        "id": car.id,
        "carname": car.carname,
        "carbrand": car.carbrand,
        "carmodel": car.carmodel,
        "carprice": car.carprice,
    }


@asynccontextmanager
async def lifespan(_: FastAPI):
    with db.connection_context():
        db.create_tables([TBCars], safe=True)
    yield


app = FastAPI(title="Cars Web Service", lifespan=lifespan)


@app.get("/")
def service_status():
    return {"message": "Car service ready"}


@app.get("/api/cars")
def list_cars(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    query: str = "",
):
    with db.connection_context():
        cars_query = TBCars.select()
        if query:
            cars_query = cars_query.where(
                (TBCars.carname.contains(query))
                | (TBCars.carbrand.contains(query))
                | (TBCars.carmodel.contains(query))
                | (TBCars.carprice.contains(query))
            )

        total_cars = cars_query.count()
        total_pages = max(1, (total_cars + limit - 1) // limit)
        cars = cars_query.paginate(page, limit)
        return {
            "cars": [serialize_car(car) for car in cars],
            "page": page,
            "total_pages": total_pages,
        }


@app.post("/api/cars", status_code=201)
def create_car(car_data: CarCreate):
    values = {
        field: getattr(car_data, field).strip()
        for field in ("carname", "carbrand", "carmodel", "carprice")
    }
    with db.connection_context():
        car = TBCars.create(**values)
        return serialize_car(car)


@app.patch("/api/cars/{car_id}")
def update_car(car_id: int, car_data: CarUpdate):
    with db.connection_context():
        car = TBCars.get_or_none(TBCars.id == car_id)
        if car is None:
            raise HTTPException(status_code=404, detail="Car not found")

        for field, value in car_data.model_dump(exclude_unset=True).items():
            if value is not None and value.strip():
                setattr(car, field, value.strip())
        car.save()
        return serialize_car(car)


@app.delete("/api/cars/{car_id}", status_code=204)
def delete_car(car_id: int):
    with db.connection_context():
        car = TBCars.get_or_none(TBCars.id == car_id)
        if car is None:
            raise HTTPException(status_code=404, detail="Car not found")
        car.delete_instance()


if __name__ == "__main__":
    uvicorn.run(
        "server.main:app",
        app_dir=str(PROJECT_DIR),
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
