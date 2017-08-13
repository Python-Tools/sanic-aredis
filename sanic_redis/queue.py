__all__=["Core"]
import aredis

from sanic_redis.standalone import Queue


class Core(Base):

    @staticmethod
    def SetConfig(app, **confs):
        app.config.REDIS_QUEUE_SETTINGS = confs
        return app

    def __init__(self,app=None):
        self.queues = {}
        if app:
            self.init_app(app)
        else:
            pass


    def init_app(self, app):
        """绑定app
        """
        if app.config.REDIS_QUEUE_SETTINGS and isinstance(app.config.REDIS_QUEUE_SETTINGS, dict):
            self.REDIS_QUEUE_SETTINGS = app.config.REDIS_QUEUE_SETTINGS
            self.app = app
            for dbname, dburl in app.config.REDIS_QUEUE_SETTINGS.items():
                queue = Queue(dburl,dbname)
                self.queues[dbname] = queue
        else:
            raise ValueError(
                "nonstandard sanic config REDIS_QUEUE_SETTINGS,REDIS_QUEUE_SETTINGS must be a Dict[dbname,dburl]")

        if "extensions" not in app.__dir__():
            app.extensions = {}
        app.extensions['redis-queue'] = self
        app.queues = self.queues
        return queue
