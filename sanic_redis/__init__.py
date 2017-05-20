
__all__=["Redis","Session", "Namespace","Cache","Broadcast"]

from sanic_redis.redis import Core as RedisCore
from sanic_redis.session import Core as SessionCore
from sanic_redis.cache import Core as CacheCore
from sanic_redis.broadcast import Core as BroadcastCore
from sanic_redis.queue import Core as QueueCore

from sanic_redis.namespace import Namespace

class Redis(RedisCore):
    def __init__(self, uri=None):
        super().__init__(uri)
class Session(SessionCore):
    def __init__(self, uri=None):
        super().__init__(uri)

class Cache(CacheCore):
    def __init__(self, uri=None):
        super().__init__(uri)

class Broadcast(BroadcastCore):
    def __init__(self, uri=None):
        super().__init__(uri)


class Queue(QueueCore):
    def __init__(self, uri=None):
        super().__init__(uri)
