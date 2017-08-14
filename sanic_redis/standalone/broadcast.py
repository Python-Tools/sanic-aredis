import threading
import asyncio
import aredis
class Channel:
    ##todo
    ##
    def __init__(self,uri:str,name:str,ignore_subscribe_messages:bool=False,**kwargs):
        self.uri = uri
        self.name = name
        self.ignore_subscribe_messages=ignore_subscribe_messages
        self.__redis = aredis.StrictRedis.from_url(self.uri)
        self.__pubsub = self.__redis.pubsub(**kwargs)

    def pubsub_reset(self):
        self.__pubsub.close()


    async def publish(self,message):
        """
        Publish ``message`` on ``channel``.
        Returns the number of subscribers the message was delivered to.
        """
        return await self.__redis.publish(self.name, message)
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

    async def subscribe(self, handler=None):
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
        if handler is None:
            return await self.__pubsub.subscribe(self.name)
        else:
            return await self.__pubsub.subscribe(**{self.name:handler})

    async def unsubscribe(self):
        return await self.__pubsub.unsubscribe(self.name)

    async def wait_for_message(self, timeout=0.1):
        """定时等待一定时间来接收推送,一定时间过后如果没收到推送就自动返回None
        """
        now = time.time()
        timeout = now + timeout
        while now < timeout:
            message = await self.__pubsub.get_message(
                ignore_subscribe_messages=ignore_subscribe_messages
            )
            if message is not None:
                if message.get("type") == 'message':
                    return message.get('data')
            await asyncio.sleep(0.01)
            now = time.time()
        return None

    async def get_message(self):
        """
        Get the next message if one is available, otherwise None.
        If timeout is specified, the system will wait for `timeout` seconds
        before returning. Timeout should be specified as a floating point
        number.
        获取到的是None或者形如:

        {'type': 'message',
         'pattern': None,
         'channel': 'foo',
         'data': 'test message 2017-04-20 01:16:54'}

         的字典,如果ignore_subscribe_messages=False,那么还会有哟中type为subscribe的信息发送.
        """
        return await self.__pubsub.get_message(ignore_subscribe_messages=self.ignore_subscribe_messages)

    async def listen(self):
        """Listen for messages on channels this client has been subscribed to"""
        return await self.__pubsub.listen()

    def sub_in_thread(self,daemon=False):
        """另起一个线程来处理sub"""
        return self.__pubsub.run_in_thread(daemon=daemon)
    def pub_in_thread(self,callback,daemon=False):
        """单独线程起一个pub服务,可以用于有规律的推送一些数据"""
        thread = PubWorkerThread(self,callback, daemon=daemon)
        thread.start()
        return thread

class PubWorkerThread(threading.Thread):
    """单独线程起一个pub服务,可以用于有规律的推送一些数据
    """
    def __init__(self, client,callback, daemon=False):
        super().__init__()
        self.daemon = daemon
        self.callback = callback
        self.client = client
        self._running = False
        # Make sure we have the current thread loop before we
        # fork into the new thread. If not loop has been set on the connection
        # pool use the current default event loop.
        try:
            if client.connection_pool.loop:
                self.loop = client.connection_pool.loop
            else:
                self.loop = asyncio.get_event_loop()
        except AttributeError as ae:
            self.loop = asyncio.get_event_loop()
        except Exception as e:
            raise e

    async def _run(self):
        client = self.client
        await self.callback(client)
        self._running = False

    def run(self):
        if self._running:
            return
        self._running = True
        future = asyncio.run_coroutine_threadsafe(self._run(), self.loop)
        return future.result()

    def stop(self):
        # stopping simply unsubscribes from all channels and patterns.
        # the unsubscribe responses that are generated will short circuit
        # the loop in run(), calling pubsub.close() to clean up the connection
        if self.loop:
            # unsubscribed = asyncio.run_coroutine_threadsafe(self.pubsub.unsubscribe(), self.loop)
            # punsubscribed = asyncio.run_coroutine_threadsafe(self.pubsub.punsubscribe(), self.loop)
            # asyncio.wait(
            #     [unsubscribed, punsubscribed],
            #     loop=self.loop
            # )
            self.loop.close()
            print('here')
