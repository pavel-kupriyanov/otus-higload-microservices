import uvicorn

from social_network_auth.settings import settings, Settings


def run(conf: Settings):
    u_conf = conf.UVICORN
    uvicorn.run(u_conf.ASGI_PATH, host=u_conf.HOST, port=u_conf.PORT,
                workers=u_conf.WORKERS)


if __name__ == '__main__':
    run(settings)
