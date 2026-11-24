import json

import requests
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)


@app.route("/")
def masukkeindeks():
    alamatserver_ms1_dba = "http://localhost:5051/cars"
    datas_dba = requests.get(alamatserver_ms1_dba)
    rows_dba = json.loads(datas_dba.text)

    alamatserver_ms3_dbb = "http://localhost:5053/cars"
    datas_dbb = requests.get(alamatserver_ms3_dbb)
    rows_dbb = json.loads(datas_dbb.text)

    return render_template("index.html", rows_dba=rows_dba, rows_dbb=rows_dbb)


@app.route("/ms1")
def ms1():
    servermana = "MS1"
    alamatserver = "http://localhost:5051/cars"
    datas = requests.get(alamatserver)
    rows = json.loads(datas.text)
    return render_template("indexms.html", rows=rows, servermana=servermana, DB="DB-A")


@app.route("/ms2")
def ms2():
    servermana = "MS2"
    alamatserver = "http://localhost:5052/cars"
    datas = requests.get(alamatserver)
    rows = json.loads(datas.text)
    return render_template("indexms.html", rows=rows, servermana=servermana, DB="DB-A")


@app.route("/ms3")
def ms3():
    servermana = "MS3"
    alamatserver = "http://localhost:5053/cars"
    datas = requests.get(alamatserver)
    rows = json.loads(datas.text)
    return render_template("indexms.html", rows=rows, servermana=servermana, DB="DB-B")


@app.route("/createcar/<ms>")
def createcar(ms):
    try:
        return render_template("createcar.html", servermana=ms)
    except:
        ms = "MS1"
        return render_template("createcar.html", servermana=ms)


@app.route("/createcarsave_ms1", methods=["GET", "POST"])
def createcarsave_ms1():
    fName = request.form["carName"]
    fBrand = request.form["carBrand"]
    fModel = request.form["carModel"]
    fPrice = request.form["carPrice"]
    fdesc = "input from appx to MS1"

    datacar = {
        "carname": fName,
        "carbrand": fBrand,
        "carmodel": fModel,
        "carprice": fPrice,
        "description": fdesc,
    }

    datacar_json = json.dumps(datacar)

    alamatserver = "http://localhost:5051/cars/"

    headers = {"Content-Type": "application/json", "Accept": "text/plain"}

    kirimdata = requests.post(alamatserver, data=datacar_json, headers=headers)

    return redirect(url_for("ms1"))


@app.route("/createcarsave_ms2", methods=["GET", "POST"])
def createcarsave_ms2():
    fName = request.form["carName"]
    fBrand = request.form["carBrand"]
    fModel = request.form["carModel"]
    fPrice = request.form["carPrice"]
    fdesc = "input from appx to MS2"

    datacar = {
        "carname": fName,
        "carbrand": fBrand,
        "carmodel": fModel,
        "carprice": fPrice,
        "description": fdesc,
    }

    datacar_json = json.dumps(datacar)

    alamatserver = "http://localhost:5052/cars/"

    headers = {"Content-Type": "application/json", "Accept": "text/plain"}

    kirimdata = requests.post(alamatserver, data=datacar_json, headers=headers)

    return redirect(url_for("ms2"))


@app.route("/createcarsave_ms3", methods=["GET", "POST"])
def createcarsave_ms3():
    fName = request.form["carName"]
    fBrand = request.form["carBrand"]
    fModel = request.form["carModel"]
    fPrice = request.form["carPrice"]
    fdesc = "input from appx to MS3"

    datacar = {
        "carname": fName,
        "carbrand": fBrand,
        "carmodel": fModel,
        "carprice": fPrice,
        "description": fdesc,
    }

    datacar_json = json.dumps(datacar)

    alamatserver = "http://localhost:5053/cars/"

    headers = {"Content-Type": "application/json", "Accept": "text/plain"}

    kirimdata = requests.post(alamatserver, data=datacar_json, headers=headers)

    return redirect(url_for("ms3"))


@app.route("/readcar/<ms>")
def readcar(ms):
    if ms == "MS1":
        alamatserver = "http://localhost:5051/cars"
        db_name = "DB-A"

    elif ms == "MS2":
        alamatserver = "http://localhost:5052/cars"
        db_name = "DB-A"

    elif ms == "MS3":
        alamatserver = "http://localhost:5053/cars"
        db_name = "DB-B"

    else:
        return "Microservice tidak ditemukan", 404

    datas = requests.get(alamatserver, timeout=5)
    datas.raise_for_status()

    return render_template(
        "readcar.html",
        rows=datas.json(),
        servermana=ms,
        DB=db_name,
    )


@app.route("/updatecar/<ms>", methods=["GET"])
def updatecar(ms):
    if ms == "MS1":
        alamatserver = "http://localhost:5051/cars/"
    elif ms == "MS2":
        alamatserver = "http://localhost:5052/cars/"
    elif ms == "MS3":
        alamatserver = "http://localhost:5053/cars/"
    else:
        return "Microservice tidak ditemukan", 404

    name = request.args.get("name", "").strip()
    datas = requests.get(alamatserver, timeout=5)
    datas.raise_for_status()

    rows = datas.json()
    if name:
        rows = [row for row in rows if name.lower() in row["carname"].lower()]

    return render_template(
        "updatecar.html",
        rows=rows,
        car=None,
        search_name=name,
        servermana=ms,
    )


@app.route("/updatecar/<ms>/<int:car_id>", methods=["GET", "POST"])
def updatecar_by_id(ms, car_id):
    if ms == "MS1":
        alamatserver = "http://localhost:5051/cars/"
    elif ms == "MS2":
        alamatserver = "http://localhost:5052/cars/"
    elif ms == "MS3":
        alamatserver = "http://localhost:5053/cars/"
    else:
        return "Microservice tidak ditemukan", 404

    datas = requests.get(alamatserver, timeout=5)
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
                rows=datas.json(),
                search_name="",
                servermana=ms,
                error="Semua field harus diisi.",
            )

        datacar = {
            "id": car_id,
            "carname": name,
            "carbrand": brand,
            "carmodel": model,
            "carprice": price,
        }

        response = requests.put(alamatserver, json=datacar, timeout=5)
        response.raise_for_status()

        return redirect(url_for("readcar", ms=ms))

    return render_template(
        "updatecar.html",
        car=car,
        rows=[],
        search_name="",
        servermana=ms,
    )


@app.route("/deletecar/<ms>", methods=["GET", "POST"])
def deletecar(ms):
    if ms == "MS1":
        alamatserver = "http://localhost:5051/cars/"
    elif ms == "MS2":
        alamatserver = "http://localhost:5052/cars/"
    elif ms == "MS3":
        alamatserver = "http://localhost:5053/cars/"
    else:
        return "Microservice tidak ditemukan", 404

    datas = requests.get(alamatserver, timeout=5)
    datas.raise_for_status()

    return render_template(
        "deletecar.html",
        rows=datas.json(),
        servermana=ms,
    )


@app.route("/deletecar/<ms>/<int:car_id>", methods=["POST"])
def deletecar_by_id(ms, car_id):
    if ms == "MS1":
        alamatserver = "http://localhost:5051/cars/"
    elif ms == "MS2":
        alamatserver = "http://localhost:5052/cars/"
    elif ms == "MS3":
        alamatserver = "http://localhost:5053/cars/"
    else:
        return "Microservice tidak ditemukan", 404

    try:
        response = requests.delete(
            alamatserver,
            json={"id": car_id},
            timeout=5,
        )
        response.raise_for_status()
    except requests.HTTPError:
        if response.status_code == 404:
            return "Data mobil tidak ditemukan", 404
        return "Gagal menghapus data", response.status_code
    except requests.RequestException:
        return "Microservice tidak dapat dijangkau", 503

    return redirect(url_for("readcar", ms=ms))


@app.route("/searchcar/<ms>")
def searchcar(ms):
    if ms == "MS1":
        alamatserver = "http://localhost:5051/cars/"
    elif ms == "MS2":
        alamatserver = "http://localhost:5052/cars/"
    elif ms == "MS3":
        alamatserver = "http://localhost:5053/cars/"
    else:
        return "Microservice tidak ditemukan", 404

    name = request.args.get("name", "").strip()

    datas = requests.get(alamatserver, timeout=5)
    datas.raise_for_status()

    rows = datas.json()

    if name:
        rows = [row for row in rows if name.lower() in row["carname"].lower()]

    return render_template(
        "searchcar.html",
        rows=rows,
        search_name=name,
        servermana=ms,
    )


if __name__ == "__main__":

    app.run(host="0.0.0.0", debug=True)
