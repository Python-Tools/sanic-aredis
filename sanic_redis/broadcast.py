__all__=["Core"]
import aredis
from sanic_redis.base import Base

class _Broadcast:
    def __init__(self,redis,**kwargs):
        self.__redis = redis
        self.__pubsub = redis.pubsub(**kwargs)

    def pubsub_reset(self):
        self.__pubsub.close()

    async def publish(self,channel, message):
        """
        Publish ``message`` on ``channel``.
        Returns the number of subscribers the message was delivered to.
        """
        return await self.__redis.publish(channel, message)
    async def channels(self, pattern='*'):
        """
        Return a list of channels that have at least one subscriber
        """
        return await self.__redis.pubsub_channels(pattern=pattern)
    async def numpat(self):
        """
        Returns the number of subscriptions to patterns
        """
        return await self.__redis.pubsub_numpat()
    async def numsub(self, *args):
        """
        Return a list of (channel, number of subscribers) tuples
        for each channel given in ``*args``
        """
        return await self.__redis.pubsub_numsub(*args)

    @property
    def subscribed(self):
        return self.__pubsub.subscribed

    async def psubscribe(self, *args, **kwargs):
        return await self.__pubsub.psubscribe(*args, **kwargs)

    async def punsubscribe(self, *args):
        return await self.__pubsub.punsubscribe(*args)

    async def subscribe(self, *args, **kwargs):
        """
        Subscribe to channels. Channels supplied as keyword arguments expect
        a channel name as the key and a callable as the value. A channel's
        callable will be invoked automatically when a message is received on
        that channel rather than producing a message via ``listen()`` or
        ``get_message()``.
        也就是说,参数可以是字符串也可以是一个键为字符串值为callable的字典,
        如果是字符串,那么就是注册下关注的channel,如果是字典,则相当于回调函数,
        key对应的channel有消息来了就会触发
        """
        return await self.__pubsub.subscribe(*args, **kwargs)

    async def unsubscribe(self,*args):
        return await self.__pubsub.unsubscribe(*args)

    async def get_message(self, ignore_subscribe_messages=False):
        """
        Get the next message if one is available, otherwise None.
        If timeout is specified, the system will wait for `timeout` seconds
        before returning. Timeout should be specified as a floating point
        number.
        """
        return await self.__pubsub.get_message(ignore_subscribe_messages=ignore_subscribe_messages)
    async def listen(self):
        """Listen for messages on channels this client has been subscribed to"""
        return await self.__pubsub.listen()

    def run_in_thread(self,daemon=False):
        """令起一个线程来处理sub"""
        return self.__pubsub.run_in_thread(daemon=daemon)

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
