from pathlib import Path
from urllib.parse import urlencode

import httpx
import uvicorn
from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
SERVICES = {
    "MS1": ("http://127.0.0.1:5051", "DB-A"),
    "MS2": ("http://127.0.0.1:5052", "DB-A"),
    "MS3": ("http://127.0.0.1:5053", "DB-B"),
}
app = FastAPI(title="PBL0902 Car Microservices", docs_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def service_info(ms: str) -> tuple[str, str]:
    try:
        return SERVICES[ms.upper()]
    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail="Microservice tidak ditemukan",
        ) from error


async def service_request(ms: str, method: str = "GET", **kwargs) -> httpx.Response:
    base_url, _ = service_info(ms)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=5.0) as client:
            response = await client.request(method, "/cars/", **kwargs)
            response.raise_for_status()
            return response
    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=error.response.status_code,
            detail=error.response.text,
        ) from error
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Microservice {ms.upper()} tidak dapat dijangkau",
        ) from error


def render(
    request: Request,
    template: str,
    **context,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name=template,
        context={"appType": "FastAPI", **context},
    )


@app.get("/", response_class=HTMLResponse)
async def masukkeindeks(
    request: Request,
    ms: str = "MS1",
    page: int = Query(default=1, ge=1),
    query: str = "",
):
    _, db_name = service_info(ms)
    ms = ms.upper()
    rows = (await service_request(ms)).json()
    if query:
        normalized_query = query.casefold()
        rows = [
            car
            for car in rows
            if any(
                normalized_query in str(car[field]).casefold()
                for field in ("carname", "carbrand", "carmodel", "carprice")
            )
        ]

    limit = 10
    total_pages = max(1, (len(rows) + limit - 1) // limit)
    page = min(page, total_pages)
    start_index = (page - 1) * limit
    page_urls = [
        (
            number,
            "/?"
            + urlencode(
                {
                    "ms": ms,
                    "page": number,
                    **({"query": query} if query else {}),
                }
            ),
        )
        for number in range(1, total_pages + 1)
    ]
    return render(
        request,
        "index.html",
        cars=rows[start_index : start_index + limit],
        page=page,
        total_pages=total_pages,
        page_urls=page_urls,
        previous_url=page_urls[max(0, page - 2)][1],
        next_url=page_urls[min(total_pages - 1, page)][1],
        start_index=start_index,
        query=query,
        active_ms=ms,
        db_name=db_name,
        services=SERVICES,
    )


@app.get("/ms1", response_class=HTMLResponse)
async def ms1(request: Request):
    return render(
        request,
        "indexms.html",
        rows=(await service_request("MS1")).json(),
        servermana="MS1",
        DB="DB-A",
    )


@app.get("/ms2", response_class=HTMLResponse)
async def ms2(request: Request):
    return render(
        request,
        "indexms.html",
        rows=(await service_request("MS2")).json(),
        servermana="MS2",
        DB="DB-A",
    )


@app.get("/ms3", response_class=HTMLResponse)
async def ms3(request: Request):
    return render(
        request,
        "indexms.html",
        rows=(await service_request("MS3")).json(),
        servermana="MS3",
        DB="DB-B",
    )


@app.get("/createcar/{ms}", response_class=HTMLResponse)
async def createcar(request: Request, ms: str):
    service_info(ms)
    return render(request, "createcar.html", servermana=ms.upper())


@app.post("/createcarsave_{ms}")
async def createcarsave(
    ms: str,
    carName: str = Form(...),
    carBrand: str = Form(...),
    carModel: str = Form(...),
    carPrice: str = Form(...),
):
    service_info(ms)
    await service_request(
        ms,
        "POST",
        json={
            "carname": carName,
            "carbrand": carBrand,
            "carmodel": carModel,
            "carprice": carPrice,
            "description": f"input from appx to {ms.upper()}",
        },
    )
    return RedirectResponse(url=f"/?ms={ms.upper()}", status_code=303)


@app.get("/readcar/{ms}", response_class=HTMLResponse)
async def readcar(request: Request, ms: str):
    _, db_name = service_info(ms)
    return render(
        request,
        "readcar.html",
        rows=(await service_request(ms)).json(),
        servermana=ms.upper(),
        DB=db_name,
    )


@app.get("/updatecar/{ms}", response_class=HTMLResponse)
async def updatecar(request: Request, ms: str, name: str = ""):
    service_info(ms)
    rows = (await service_request(ms)).json()
    if name.strip():
        rows = [row for row in rows if name.lower() in row["carname"].lower()]
    return render(
        request,
        "updatecar.html",
        rows=rows,
        car=None,
        search_name=name,
        servermana=ms.upper(),
    )


@app.api_route(
    "/updatecar/{ms}/{car_id}",
    methods=["GET", "POST"],
    response_class=HTMLResponse,
)
async def updatecar_by_id(request: Request, ms: str, car_id: int):
    rows = (await service_request(ms)).json()
    car = next((row for row in rows if row["id"] == car_id), None)
    if car is None:
        raise HTTPException(status_code=404, detail="Data mobil tidak ditemukan")

    if request.method == "POST":
        form = await request.form()
        values = {
            "carname": str(form.get("name", "")).strip(),
            "carbrand": str(form.get("brand", "")).strip(),
            "carmodel": str(form.get("model", "")).strip(),
            "carprice": str(form.get("price", "")).strip(),
        }
        if not all(values.values()):
            return render(
                request,
                "updatecar.html",
                car=car,
                rows=rows,
                search_name="",
                servermana=ms.upper(),
                error="Semua field harus diisi.",
            )
        await service_request(ms, "PUT", json={"id": car_id, **values})
        return RedirectResponse(url=f"/?ms={ms.upper()}", status_code=303)

    return render(
        request,
        "updatecar.html",
        car=car,
        rows=[],
        search_name="",
        servermana=ms.upper(),
    )


@app.get("/deletecar/{ms}", response_class=HTMLResponse)
async def deletecar(request: Request, ms: str):
    service_info(ms)
    return render(
        request,
        "deletecar.html",
        rows=(await service_request(ms)).json(),
        servermana=ms.upper(),
    )


@app.post("/deletecar/{ms}/{car_id}")
async def deletecar_by_id(ms: str, car_id: int):
    await service_request(ms, "DELETE", json={"id": car_id})
    return RedirectResponse(url=f"/?ms={ms.upper()}", status_code=303)


@app.get("/searchcar/{ms}", response_class=HTMLResponse)
async def searchcar(request: Request, ms: str, name: str = ""):
    service_info(ms)
    rows = (await service_request(ms)).json()
    if name.strip():
        rows = [row for row in rows if name.lower() in row["carname"].lower()]
    return render(
        request,
        "searchcar.html",
        rows=rows,
        search_name=name,
        servermana=ms.upper(),
    )


if __name__ == "__main__":
    uvicorn.run("APPX.appx:app", host="0.0.0.0", port=5000, reload=True)
