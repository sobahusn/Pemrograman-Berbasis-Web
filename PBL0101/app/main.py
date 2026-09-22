from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Simple Project Hello World using FastAPI")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Tugas PBL 0101 - 054",
            "message": "Hello World",
            "description": "Simple Project Hello World using FastAPI",
        },
    )


@app.get("/hello-world")
async def hello_world():
    return {"message": "Hello World"}
