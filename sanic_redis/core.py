__all__=["Core"]

import aredis

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
        if not self.uri:
            if app.config.REDIS_URI:
                self.__uri = app.config.REDIS_URI
            else:
                raise AssertionError("need a db uri")

        if "extensions" not in app.__dir__():
            app.extensions = {}
        redis = aredis.StrictRedis.from_url(self.uri)
        self.redis = redis
        app.extensions['SanicRedis'] = self
        return redis
