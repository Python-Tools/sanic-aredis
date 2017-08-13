__all__=["Core"]
import aredis
import asyncio
import time
import threading



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
                redis = aredis.StrictRedis.from_url(dburl)
                if ignore_subscribe_messages:
                    broadcast = _Broadcast(redis, ignore_subscribe_messages=ignore_subscribe_messages)
                else:
                    broadcast = _Broadcast(redis)
                self.channels[dbname] = broadcast
        else:
            raise ValueError(
                "nonstandard sanic config REDIS_CHANNEL_SETTINGS,REDIS_CHANNEL_SETTINGS must be a Dict[dbname,Tuple[dburl,ignore_subscribe_messages]]")


        if "extensions" not in app.__dir__():
            app.extensions = {}
        app.extensions['redis-channel'] = self
        app.channels = self.channels
        return self.channels
