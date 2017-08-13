__all__=["Core"]
import aredis
from types import MethodType

async def get_by_key(self, key):
    res = await self.client.get(key)
    if res:
        res = self._unpack(res)
    return res

class Core:

    @staticmethod
    def SetConfig(app, **confs):
        app.config.REDIS_CACHE_SETTINGS = confs
        return app

    def __init__(self,app=None):
        self.caches = {}
        if app:
            self.init_app(app)
        else:
            pass

    def init_app(self, app):
        """绑定app
        """

        if app.config.REDIS_CACHE_SETTINGS and isinstance(app.config.REDIS_CACHE_SETTINGS, dict):
            self.REDIS_CACHE_SETTINGS = app.config.REDIS_CACHE_SETTINGS
            self.app = app
            for dbname, dburl in app.config.REDIS_CACHE_SETTINGS.items():
                redis = aredis.StrictRedis.from_url(dburl)
                cache = redis.cache(app.name+"-"+dbname+'-cache:')
                cache.get_by_key = MethodType(get_by_key, cache)
                self.caches[dbname] = cache
        else:
            raise ValueError(
                "nonstandard sanic config REDIS_CACHE_SETTINGS,REDIS_CACHE_SETTINGS must be a Dict[dbname,dburl]")

        if "extensions" not in app.__dir__():
            app.extensions = {}
        app.extensions['redis-cache'] = cache
        app.caches = self.caches
        return self.caches
