from contextlib import asynccontextmanager

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
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
    title="Xathes API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)


templates = Jinja2Templates(directory="app/templates")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/privacy", response_class=HTMLResponse, include_in_schema=False)
def privacy():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Xathes Privacy Policy</title>
        <style>
            body{
                font-family:Arial,Helvetica,sans-serif;
                max-width:900px;
                margin:40px auto;
                padding:20px;
                line-height:1.7;
                color:#333;
            }
            h1{color:#222;}
        </style>
    </head>
    <body>
        <h1>Xathes Privacy Policy</h1>

        <p>
            Xathes uses your marketplace account information only to provide
            AI-powered product optimization and marketplace integration services.
        </p>

        <p>
            We do not sell, rent or share your personal information with third
            parties except where required to operate the service or comply with law.
        </p>

        <p>
            OAuth access tokens are stored securely and are used only to perform
            actions that you explicitly authorize.
        </p>

        <p>
            Contact:
            <a href="mailto:info@nobleblood.co.uk">
                info@nobleblood.co.uk
            </a>
        </p>

    </body>
    </html>
    """


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

app.include_router(router)