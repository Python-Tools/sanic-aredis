from sanic_redis.namespace import Namespace
import aredis
class Queue:
    def __init__(self,uri:str,queuename:str):
        self.uri = uri
        self.__redis = aredis.StrictRedis.from_url(self.uri)
        self.namespace = Namespace('queue-'+queuename+":")

    async def push(self,key,*value):
        result = await self.__redis.lpush(self.namespace(key),*value)
        return result

    async def pop(self,key,timeout=0):
        result = await self.__redis.brpop(self.namespace(key),timeout=timeout)
        return result
