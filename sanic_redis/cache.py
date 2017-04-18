__all__=["Core"]
import aredis
from sanic_redis.base import Base
from types import MethodType

async def get_by_key(self, key):
    res = await self.client.get(key)
    if res:
        res = self._unpack(res)
    return res

class Core(Base):

    def __init__(self,uri=None):
        super().__init__(uri)

    def init_app(self, app):
        """绑定app
        """
        self.app = app
        if not self.uri:
            if app.config.REDIS_CACHE_URI:
                self.__uri = app.config.REDIS_CACHE_URI
            else:
                raise AssertionError("need a db uri")

        if "extensions" not in app.__dir__():
            app.extensions = {}
        redis = aredis.StrictRedis.from_url(self.uri)
        cache = redis.cache(app.name+'-cache:')
        cache.get_by_key = MethodType(get_by_key, cache)
        self.cache = cache
        app.extensions['CACHE'] = cache
        return cache
