__all__=["Core"]
import aredis
from sanic_redis.base import Base
from sanic_redis.standalone import Queue


class Core(Base):
    def __init__(self,uri=None):
        super().__init__(uri)
    def init_app(self, app):
        """绑定app
        """
        self.app = app
        if not self.__uri:
            if app.config.REDIS_QUEUE_URI:
                self.__uri = app.config.REDIS_QUEUE_URI
            else:
                raise AssertionError("need a db uri")
        queue = Queue(self.__uri,app.name)
        if "extensions" not in app.__dir__():
            app.extensions = {}

        app.extensions['Queue'] = queue
        return queue
