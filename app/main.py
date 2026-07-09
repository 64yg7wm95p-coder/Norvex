from contextlib import asynccontextmanager

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import init_db
from .routes import router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Norvex API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)


templates = Jinja2Templates(directory="app/templates")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


app.include_router(router)