# !/usr/bin/env python3

from flask import Flask, redirect, render_template, request, url_for
from peewee import *

app = Flask(__name__)

global appType
appType = "Monolith"

database = SqliteDatabase("carsweb.db")


class BaseModel(Model):
    class Meta:
        database = database


class TBCars(BaseModel):
    id = AutoField(primary_key=True)
    carname = TextField()
    carbrand = TextField()
    carmodel = TextField()
    carprice = TextField()


def create_tables():
    with database:
        database.create_tables([TBCars])


@app.route("/")
def indeks():
    return render_template("index.html", appType=appType)


@app.route("/createcar")
def createcar():
    return render_template("createcar.html", appType=appType)


@app.route("/createcarsave", methods=["GET", "POST"])
def createcarsave():
    fName = request.form["carName"]
    fBrand = request.form["carBrand"]
    fModel = request.form["carModel"]
    fPrice = request.form["carPrice"]

    viewData = {"name": fName, "brand": fBrand, "model": fModel, "price": fPrice}

    # simpan di DB
    car_simpan = TBCars.create(
        carname=fName, carbrand=fBrand, carmodel=fModel, carprice=fPrice
    )
    return redirect(url_for("readcar"))


@app.route("/readcar")
def readcar():
    rows = TBCars.select()
    return render_template("readcar.html", rows=rows, appType=appType)


@app.route("/updatecar", methods=["GET"])
def updatecar():
    name = request.args.get("name", "").strip()
    rows = []

    if name:
        rows = list(TBCars.select().where(TBCars.carname.contains(name)))

    return render_template(
        "updatecar.html", rows=rows, car=None, appType=appType, search_name=name
    )


@app.route("/updatecar/<int:car_id>", methods=["GET", "POST"])
def updatecar_by_id(car_id):
    car = TBCars.get_or_none(TBCars.id == car_id)

    if car is None:
        return "Data mobil tidak ditemukan", 404

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        brand = request.form.get("brand", "").strip()
        model = request.form.get("model", "").strip()
        price = request.form.get("price", "").strip()

        if not all([name, brand, model, price]):
            return render_template(
                "updatecar.html",
                car=car,
                rows=[],
                search_name="",
                appType=appType,
                error="Semua field harus diisi.",
            )

        car.carname = name
        car.carbrand = brand
        car.carmodel = model
        car.carprice = price
        car.save()

        return redirect(url_for("readcar", updated=True))

    return render_template(
        "updatecar.html", car=car, rows=[], search_name="", appType=appType
    )


@app.route("/deletecar")
def deletecar():
    return render_template("deletecar.html", appType=appType)


@app.route("/deletecarsave", methods=["GET", "POST"])
def deletecarsave():
    fName = request.form["carName"]
    car_delete = TBCars.delete().where(TBCars.carname == fName)
    car_delete.execute()
    return redirect(url_for("readcar"))


@app.route("/searchcar")
def searchcar():
    name = request.args.get("name", "").strip()
    rows = []

    if name:
        rows = list(TBCars.select().where(TBCars.carname.contains(name)))

    return render_template(
        "searchcar.html", rows=rows, search_name=name, appType=appType
    )


@app.route("/help")
def help():
    return "ini halaman Helps"


if __name__ == "__main__":
    create_tables()
    app.run(port=5010, host="0.0.0.0", debug=True)
