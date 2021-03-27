import os.path
from functools import lru_cache

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api_gateway.settings import ROOT_DIR

from .api import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(ROOT_DIR, 'web/app/frontend/static')
INDEX = os.path.join(ROOT_DIR, 'web/app/frontend/index.html')

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


app.include_router(router, prefix='/api')


@app.get('{full_path:path}', response_class=HTMLResponse)
def get_frontend(full_path: str):
    return load_frontend()


@lru_cache(1)
def load_frontend() -> str:
    with open(INDEX) as fp:
        return fp.read()
