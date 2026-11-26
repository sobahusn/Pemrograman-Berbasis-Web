from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from peewee import AutoField, Model, SqliteDatabase, TextField
from pydantic import BaseModel


class CarCreate(BaseModel):
    carname: str
    carbrand: str
    carmodel: str
    carprice: str
    description: str | None = None


class CarUpdate(CarCreate):
    id: int


class CarDelete(BaseModel):
    id: int


def create_service(db_path: Path, service_name: str) -> FastAPI:
    db = SqliteDatabase(db_path)

    class BaseModelDB(Model):
        class Meta:
            database = db

    class TBCarsWeb(BaseModelDB):
        id = AutoField()
        carname = TextField()
        carbrand = TextField()
        carmodel = TextField()
        carprice = TextField()
        description = TextField(null=True)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        with db.connection_context():
            db.create_tables([TBCarsWeb], safe=True)
            columns = {column.name for column in db.get_columns("tbcarsweb")}
            if "description" not in columns:
                db.execute_sql('ALTER TABLE "tbcarsweb" ADD COLUMN "description" TEXT')
        yield
        db.close()

    app = FastAPI(title=f"{service_name} Cars Service", lifespan=lifespan)

    def serialize(car: TBCarsWeb) -> dict[str, Any]:
        return {
            "id": car.id,
            "carname": car.carname,
            "carbrand": car.carbrand,
            "carmodel": car.carmodel,
            "carprice": car.carprice,
            "description": car.description,
        }

    @app.get("/")
    def service_status():
        return {"message": f"{service_name} Server Ready"}

    @app.get("/cars/")
    def list_cars():
        with db.connection_context():
            return [serialize(car) for car in TBCarsWeb.select()]

    @app.post("/cars/", status_code=201)
    def create_car(data: CarCreate):
        values = data.model_dump()
        for field in ("carname", "carbrand", "carmodel", "carprice"):
            values[field] = values[field].strip()
        with db.connection_context():
            car = TBCarsWeb.create(**values)
            return serialize(car)

    @app.put("/cars/")
    def update_car(data: CarUpdate):
        with db.connection_context():
            car = TBCarsWeb.get_or_none(TBCarsWeb.id == data.id)
            if car is None:
                raise HTTPException(
                    status_code=404, detail="Data mobil tidak ditemukan"
                )
            for field in ("carname", "carbrand", "carmodel", "carprice"):
                setattr(car, field, getattr(data, field).strip())
            if data.description is not None:
                car.description = data.description
            car.save()
            return {"message": "Data berhasil diperbarui"}

    @app.delete("/cars/")
    def delete_car(data: CarDelete):
        with db.connection_context():
            car = TBCarsWeb.get_or_none(TBCarsWeb.id == data.id)
            if car is None:
                raise HTTPException(
                    status_code=404, detail="Data mobil tidak ditemukan"
                )
            car.delete_instance()
            return {"message": "Data berhasil dihapus"}

    return app
