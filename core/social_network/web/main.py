from asyncio import create_task

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse

from social_network.settings import settings
from social_network.db.exceptions import RowsNotFoundError
from social_network.db.managers import NewsManager
from social_network.services import DependencyInjector

from .utils import warmup_news

from .auth import router as auth_router
from .users import router as users_router
from .friendships import router as friend_requests_manager
from .hobbies import router as hobbies_router
from .messages import router as messages_router
from .news import router as news_router

app = FastAPI()


@app.exception_handler(RowsNotFoundError)
async def handle_404(request: Request, exc: RowsNotFoundError):
    return JSONResponse(status_code=404, content={'detail': 'Not found'})


app.include_router(auth_router, prefix='/auth')
app.include_router(users_router, prefix='/users')
app.include_router(friend_requests_manager, prefix='/friendships')
app.include_router(hobbies_router, prefix='/hobbies')
app.include_router(messages_router, prefix='/messages')
app.include_router(news_router, prefix='/news')


@app.on_event('startup')
async def startup():
    injector = DependencyInjector(settings)
    await injector.start()
    coro = warmup_news(
        settings.NEWS_CACHE,
        NewsManager(injector.connectors_storage),
        injector.kafka_producer
    )
    create_task(coro)
    app.state.dependency_injector = injector


@app.on_event('shutdown')
async def shutdown():
    await app.state.dependency_injector.close()
