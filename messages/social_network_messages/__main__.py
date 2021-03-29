import uvicorn

from social_network_messages.settings import BaseSettings, settings


def run(conf: BaseSettings):
    u_conf = conf.UVICORN
    uvicorn.run(u_conf.ASGI_PATH, host=u_conf.HOST, port=u_conf.PORT,
                workers=u_conf.WORKERS)


if __name__ == '__main__':
    run(settings)
