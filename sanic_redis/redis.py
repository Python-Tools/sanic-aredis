# @Author: Huang Sizhe
# @Date:   10-Apr-2017
# @Email:  hsz1273327@gmail.com
# @Last modified by:   Huang Sizhe
# @Last modified time: 10-Apr-2017
# @License: MIT



__all__=["Core"]
import aredis
from sanic_redis.base import Base
class Core(Base):
    def __init__(self,uri=None):
        super().__init__(uri)
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
        redis = aredis.StrictRedis.from_url(self.uri)
        self.redis = redis
        app.extensions['Aredis'] = redis
        return redis
