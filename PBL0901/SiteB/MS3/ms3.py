from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from peewee import *

app = Flask(__name__)
api = Api(app)

db = SqliteDatabase("DB-B.db")


class BaseModel(Model):
    class Meta:
        database = db


class TBCarsWeb(BaseModel):
    carname = TextField()
    carbrand = TextField()
    carmodel = TextField()
    carprice = TextField()
    description = TextField()


def create_tables():
    with db:
        db.create_tables([TBCarsWeb])


@app.route("/")
def masukkeindeks():
    return "MS3 Server Ready"


class CAR(Resource):
    def get(self):
        rows = TBCarsWeb.select()
        datas = []

        for row in rows:
            datas.append(
                {
                    "id": row.id,
                    "carname": row.carname,
                    "carbrand": row.carbrand,
                    "carmodel": row.carmodel,
                    "carprice": row.carprice,
                    "description": row.description,
                }
            )
        return jsonify(datas)

    def post(self):
        parserData = reqparse.RequestParser()
        parserData.add_argument("carname")
        parserData.add_argument("carbrand")
        parserData.add_argument("carmodel")
        parserData.add_argument("carprice")
        parserData.add_argument("description")

        parserAmbilData = parserData.parse_args()

        fName = parserAmbilData.get("carname")
        fBrand = parserAmbilData.get("carbrand")
        fModel = parserAmbilData.get("carmodel")
        fPrice = parserAmbilData.get("carprice")
        fDescription = parserAmbilData.get("description")

        car_simpan = TBCarsWeb.create(
            carname=fName,
            carbrand=fBrand,
            carmodel=fModel,
            carprice=fPrice,
            description=fDescription,
        )

        rows = TBCarsWeb.select()
        datas = []
        for row in rows:
            datas.append(
                {
                    "id": row.id,
                    "carname": row.carname,
                    "carbrand": row.carbrand,
                    "carmodel": row.carmodel,
                    "carprice": row.carprice,
                    "description": row.description,
                }
            )
        return jsonify(datas)

    def put(self):
        parserData = reqparse.RequestParser()
        parserData.add_argument("id", type=int, required=True)
        parserData.add_argument("carname", required=True)
        parserData.add_argument("carbrand", required=True)
        parserData.add_argument("carmodel", required=True)
        parserData.add_argument("carprice", required=True)
        parserData.add_argument("description")

        data = parserData.parse_args()

        car = TBCarsWeb.get_or_none(TBCarsWeb.id == data["id"])

        if car is None:
            return {"message": "Data mobil tidak ditemukan"}, 404

        car.carname = data["carname"]
        car.carbrand = data["carbrand"]
        car.carmodel = data["carmodel"]
        car.carprice = data["carprice"]

        if data["description"] is not None:
            car.description = data["description"]

        car.save()

        return {"message": "Data berhasil diperbarui"}, 200

    def delete(self):
        parserData = reqparse.RequestParser()
        parserData.add_argument("id", type=int, required=True)
        data = parserData.parse_args()

        car = TBCarsWeb.get_or_none(TBCarsWeb.id == data["id"])

        if car is None:
            return {"message": "Data mobil tidak ditemukan"}, 404

        car.delete_instance()

        return {"message": "Data berhasil dihapus"}, 200


api.add_resource(CAR, "/cars/", endpoint="cars/")


if __name__ == "__main__":
    create_tables()
    app.run(host="0.0.0.0", debug=False, port=5053)
