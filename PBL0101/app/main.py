from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import time

app = FastAPI(title="Simple Project Hello World using FastAPI")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "message": "Hello World",
            "code": "#PBW3B1PBL0101",
            "identity": "251080200054 M. Sobahus Sururin Ni'am",
            "framework": "Python [3] - FastAPI",
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        },
    )


@app.get("/hello-world")
async def hello_world():
    return {
        "message": "Hello World",
        "code": "#PBW3B1PBL0101",
        "identity": "251080200054 M. Sobahus Sururin Ni'am",
        "framework": "Python [3] - FastAPI",
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
    }
