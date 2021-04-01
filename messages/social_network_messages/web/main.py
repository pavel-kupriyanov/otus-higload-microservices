from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette_exporter import PrometheusMiddleware, handle_metrics

from social_network_messages.settings import settings
from social_network_messages.db.exceptions import RowsNotFoundError
from social_network_messages.db.connectors_storage import ConnectorsStorage

from .views import router as api_router

app = FastAPI()
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)


@app.exception_handler(RowsNotFoundError)
async def handle_404(request: Request, exc: RowsNotFoundError):
    return JSONResponse(status_code=404, content={'detail': 'Not found'})


app.include_router(api_router, prefix='/messages')


@app.on_event('startup')
async def startup():
    storage = ConnectorsStorage()
    await storage.create_connector(settings.DATABASE.MASTER)

    for conf in settings.DATABASE.SLAVES:
        await storage.create_connector(conf)
    app.state.storage = storage
