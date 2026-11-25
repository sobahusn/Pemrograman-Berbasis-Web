import os
from pathlib import Path
from urllib.parse import urlencode

import httpx
import uvicorn
from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
API_URL = os.environ.get("CARS_API_URL", "http://127.0.0.1:8001")

app = FastAPI(title="Car Management Client", docs_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


async def api_request(method: str, path: str, **kwargs) -> httpx.Response:
    async with httpx.AsyncClient(base_url=API_URL, timeout=5.0) as client:
        response = await client.request(method, path, **kwargs)
        response.raise_for_status()
        return response


@app.get("/", response_class=HTMLResponse)
async def list_cars(
    request: Request,
    page: int = Query(default=1, ge=1),
    query: str = "",
):
    response = await api_request(
        "GET", "/api/cars", params={"page": page, "query": query}
    )
    data = response.json()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "cars": data["cars"],
            "page": data["page"],
            "total_pages": data["total_pages"],
            "query": query,
        },
    )


@app.post("/cars/create")
async def create_car(
    carname: str = Form(...),
    carbrand: str = Form(...),
    carmodel: str = Form(...),
    carprice: str = Form(...),
):
    await api_request(
        "POST",
        "/api/cars",
        json={
            "carname": carname,
            "carbrand": carbrand,
            "carmodel": carmodel,
            "carprice": carprice,
        },
    )
    return RedirectResponse(url="/?created=true", status_code=303)


@app.post("/cars/update/{car_id}")
async def update_car(
    car_id: int,
    name: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    price: str = Form(...),
):
    await api_request(
        "PATCH",
        f"/api/cars/{car_id}",
        json={
            "carname": name,
            "carbrand": brand,
            "carmodel": model,
            "carprice": price,
        },
    )
    return RedirectResponse(url="/?updated=true", status_code=303)


@app.get("/cars/search")
async def search_cars(query: str = ""):
    if not query:
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url=f"/?{urlencode({'query': query})}", status_code=303)


@app.get("/cars/delete/{car_id}")
async def delete_car(car_id: int):
    await api_request("DELETE", f"/api/cars/{car_id}")
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    uvicorn.run(
        "client.main:app",
        app_dir=str(BASE_DIR.parent),
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
