
__all__=["Redis","Session", "Namespace","Cache","Broadcast"]

from sanic_redis.redis import Core as RedisCore
from sanic_redis.session import Core as SessionCore
from sanic_redis.cache import Core as CacheCore
from sanic_redis.broadcast import Core as BroadcastCore
from sanic_redis.queue import Core as QueueCore

from sanic_redis.namespace import Namespace

class Redis(RedisCore):
    pass
class Session(SessionCore):
    pass
class Cache(CacheCore):
    pass

class Broadcast(BroadcastCore):
    pass
 
class Queue(QueueCore):
    pass
