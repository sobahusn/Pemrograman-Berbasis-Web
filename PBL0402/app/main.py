import math
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from peewee import CharField, Model, SqliteDatabase

# Inisialisasi dan Load Database
db = SqliteDatabase("carsweb.db")


class BaseModel(Model):
    class Meta:
        database = db


class TBCars(BaseModel):
    id = CharField(primary_key=True)
    carname = CharField()
    carbrand = CharField()
    carmodel = CharField()
    carprice = CharField()


# Path directory route
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Inisialisasi FastAPI sebagai app
app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


# Membuat Database SQLite
def create_tables():
    with db:
        db.create_tables([TBCars], safe=True)


# Get All Cars
@app.get("/", response_class=HTMLResponse)
async def list_cars(request: Request, page: int = 1, limit: int = 10):
    base_query = TBCars.select()

    total_cars = base_query.count()
    total_pages = math.ceil(total_cars / limit) if total_cars > 0 else 1

    cars = base_query.paginate(page, limit)
    start_index = (page - 1) * limit

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "cars": cars,
            "page": page,
            "total_pages": total_pages,
            "start_index": start_index,
        },
    )


# Create Car
@app.post("/cars/create")
async def create_car(
    carname: str = Form(...),
    carbrand: str = Form(...),
    carmodel: str = Form(...),
    carprice: str = Form(...),
):
    TBCars.create(
        carname=carname.strip(),
        carbrand=carbrand.strip(),
        carmodel=carmodel.strip(),
        carprice=carprice.strip(),
    )

    return RedirectResponse(url="/?created=true", status_code=303)


# Update / Edit Car
@app.post("/cars/update/{car_id}")
async def update_car(
    car_id: int,
    name: str = Form(None),
    brand: str = Form(None),
    model: str = Form(None),
    price: str = Form(None),
):
    car = TBCars.get_or_none(TBCars.id == car_id)

    if car:
        if name and name.strip() != "":
            car.carname = name.strip()
        if brand and brand.strip() != "":
            car.carbrand = brand.strip()
        if model and model.strip() != "":
            car.carmodel = model.strip()
        if price and price.strip() != "":
            car.carprice = price.strip()
        car.save()

    return RedirectResponse(url="/?updated=true", status_code=303)


# Search Car
@app.get("/cars/search", response_class=HTMLResponse)
async def search_cars(request: Request, query: str = ""):

    if not query:
        return RedirectResponse(url="/", status_code=303)

    cars = TBCars.select().where(
        (TBCars.carname.contains(query))
        | (TBCars.carbrand.contains(query))
        | (TBCars.carmodel.contains(query))
        | (TBCars.carprice.contains(query))
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"cars": cars, "query": query},
    )


# Delete Car
@app.post("/cars/delete/{car_id}")
async def delete_car(car_id: int):
    car = TBCars.get_or_none(TBCars.id == car_id)

    if car:
        car.delete_instance()
        return {"message": "Berhasil menghapus data mobil"}

    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    create_tables()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
