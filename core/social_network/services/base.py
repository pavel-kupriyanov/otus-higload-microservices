from typing import List


class BaseService:

    async def start(self):
        raise NotImplemented

    async def close(self):
        raise NotImplemented


class BaseController(BaseService):

    @property
    def services(self) -> List[BaseService]:
        raise NotImplemented

    async def start(self):
        for service in self.services:
            await service.start()

    async def close(self):
        for service in self.services:
            await service.close()
