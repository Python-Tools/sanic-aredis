__all__=["Core"]
import aredis
from sanic_redis.base import Base
import asyncio
import time
import threading



class Core(Base):
    def __init__(self,uri=None):
        super().__init__(uri)
    def init_app(self, app):
        """绑定app
        """
        self.app = app
        if not self.uri:
            if app.config.REDIS_BROADCAST_URI:
                self.__uri = app.config.REDIS_BROADCAST_URI
            else:
                raise AssertionError("need a db uri")

        if "extensions" not in app.__dir__():
            app.extensions = {}
        redis = aredis.StrictRedis.from_url(self.uri)
        if app.config.get('REDIS_BROADCAST_IGNORE_SUBSCRIBE_MESSAGES'):
            broadcast = _Broadcast(redis, ignore_subscribe_messages=app.config.REDIS_BROADCAST_IGNORE_SUBSCRIBE_MESSAGES)
        else:
            broadcast = _Broadcast(redis)
        app.extensions['Broadcast'] = broadcast
        return broadcast
