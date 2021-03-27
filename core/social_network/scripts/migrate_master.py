from social_network.db.migrations import migrate
from social_network.settings import settings

if __name__ == '__main__':
    migrate(settings.DATABASE.MASTER)
