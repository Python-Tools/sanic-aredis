from sanic_redis.core import Core
class Redis(Core):
    def __init__(self, uri=None):
        super().__init__(uri)
