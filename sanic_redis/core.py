# @Author: Huang Sizhe
# @Date:   10-Apr-2017
# @Email:  hsz1273327@gmail.com
# @Last modified by:   Huang Sizhe
# @Last modified time: 10-Apr-2017
# @License: MIT



__all__=["Core"]

from sanic_redis.sanic_strict_redis import SaincStrictRedis

class Core:

    @property
    def uri(self):
        return self.__uri
    def __call__(self,app):
        if app:
            return self.init_app(app)
        else:
            raise AttributeError("need a sanic app to init the extension")

    def __init__(self,uri=None):
        self.__uri = uri

    def init_app(self, app):
        """绑定app
        """
        self.app = app
        if not self.uri:
            if app.config.REDIS_URI:
                self.__uri = app.config.REDIS_URI
            else:
                raise AssertionError("need a db uri")

        if "extensions" not in app.__dir__():
            app.extensions = {}
        redis = SaincStrictRedis.from_url(self.uri)
        self.redis = redis
        app.extensions['SanicRedis'] = self
        return redis

    def init_session(self,db):
        pass
