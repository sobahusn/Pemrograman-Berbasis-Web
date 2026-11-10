from flask import Flask, render_template, request, redirect, url_for
import json, requests

app = Flask(__name__)

global appType

appType = "Web Service"


@app.route("/")
def index():
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

    datacar = {
        "carname": fName,
        "carbrand": fBrand,
        "carmodel": fModel,
        "carprice": fPrice,
    }

    datacar_json = json.dumps(datacar)

    alamatserver = "http://localhost:5012/cars/"

    headers = {"Content-Type": "application/json", "Accept": "text/plain"}

    kirimdata = requests.post(alamatserver, data=datacar_json, headers=headers)

    return redirect(url_for("readcar"))


@app.route("/readcar")
def readcar():
    alamatserver = "http://localhost:5012/cars"
    datas = requests.get(alamatserver)

    rows = json.loads(datas.text)

    return render_template("readcar.html", rows=rows, appType=appType)


@app.route("/updatecar", methods=["GET"])
def updatecar():
    name = request.args.get("name", "").strip()
    rows = []

    if name:
        alamatserver = "http://localhost:5012/cars"
        datas = requests.get(alamatserver)
        datas.raise_for_status()
        rows = [row for row in datas.json() if name.lower() in row["carname"].lower()]

    return render_template(
        "updatecar.html", rows=rows, car=None, appType=appType, search_name=name
    )


@app.route("/updatecar/<int:car_id>", methods=["GET", "POST"])
def updatecar_by_id(car_id):
    alamatserver = "http://localhost:5012/cars"
    datas = requests.get(alamatserver)
    datas.raise_for_status()
    car = next((row for row in datas.json() if row["id"] == car_id), None)

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

        datacar = {
            "id": car_id,
            "carname": name,
            "carbrand": brand,
            "carmodel": model,
            "carprice": price,
        }
        response = requests.put(alamatserver, json=datacar)
        response.raise_for_status()

        return redirect(url_for("readcar"))

    return render_template(
        "updatecar.html", car=car, rows=[], search_name="", appType=appType
    )


@app.route("/deletecar")
def deletecar():
    return render_template("deletecar.html", appType=appType)


@app.route("/deletecarsave", methods=["GET", "POST"])
def deletecarsave():
    alamatserver = "http://localhost:5012/cars/"
    fName = request.form["carName"]
    datacar = {"carname": fName}
    datacar_json = json.dumps(datacar)
    headers = {"Content-Type": "application/json", "Accept": "text/plain"}

    kirimdata = requests.delete(alamatserver, data=datacar_json, headers=headers)
    return redirect(url_for("readcar"))


@app.route("/searchcar")
def searchcar():
    alamatserver = "http://localhost:5012/cars"
    name = request.args.get("name", "").strip()
    rows = []

    datas = requests.get(alamatserver)
    datas.raise_for_status()

    datas = datas.json()

    if name:
        rows = [row for row in datas if name.lower() in row["carname"].lower()]

    return render_template(
        "searchcar.html", rows=rows, search_name=name, appType=appType
    )


if __name__ == "__main__":

    app.run(host="0.0.0.0", debug="True", port=5011)
