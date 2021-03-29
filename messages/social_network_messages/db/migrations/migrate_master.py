from social_network_messages.settings import settings

from .main import migrate

if __name__ == '__main__':
    migrate(settings.DATABASE.MASTER)
