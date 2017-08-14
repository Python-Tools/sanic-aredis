__all__=["Core"]
import aredis
import asyncio
import time
import threading
from sanic_redis.standalone import Channel


class Core:

    @staticmethod
    def SetConfig(app, **confs):
        app.config.REDIS_CHANNEL_SETTINGS = confs
        return app

    def __init__(self,app=None):
        self.channels = {}
        if app:
            self.init_app(app)
        else:
            pass

    def init_app(self, app):
        """绑定app
        """
        if app.config.REDIS_CHANNEL_SETTINGS and isinstance(app.config.REDIS_CHANNEL_SETTINGS, dict):
            self.REDIS_CHANNEL_SETTINGS = app.config.REDIS_CHANNEL_SETTINGS
            self.app = app
            for dbname, (dburl,ignore_subscribe_messages) in app.config.REDIS_CHANNEL_SETTINGS.items():
                broadcast = Channel(dburl,dbname, ignore_subscribe_messages=ignore_subscribe_messages)

                self.channels[dbname] = broadcast
        else:
            raise ValueError(
                "nonstandard sanic config REDIS_CHANNEL_SETTINGS,REDIS_CHANNEL_SETTINGS must be a Dict[dbname,Tuple[dburl,ignore_subscribe_messages]]")

        @app.listener("before_server_stop")
        async def sub_close(app, loop):

            for name,channel in self.channels.items():
                channel.pubsub_reset()

            print("after channels closed")


        if "extensions" not in app.__dir__():
            app.extensions = {}
        app.extensions['redis-channel'] = self
        app.channels = self.channels
        return self.channels
