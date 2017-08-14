__all__=["Core"]
import aredis
class Core:

    @staticmethod
    def SetConfig(app, **confs):
        app.config.REDIS_SETTINGS = confs
        return app

    def __init__(self,app=None):
        self.redises = {}
        if app:
            self.init_app(app)
        else:
            pass

    def init_app(self, app):
        """绑定app
        """
        if app.config.REDIS_SETTINGS and isinstance(app.config.REDIS_SETTINGS, dict):
            self.REDIS_SETTINGS = app.config.REDIS_SETTINGS
            self.app = app
            for dbname, dburl in app.config.REDIS_SETTINGS.items():
                redis = aredis.StrictRedis.from_url(dburl)
                self.redises[dbname] = redis
        else:
            raise ValueError(
                "nonstandard sanic config REDIS_SETTINGS,REDIS_SETTINGS must be a Dict[dbname,dburl]")


        if "extensions" not in app.__dir__():
            app.extensions = {}
        app.extensions['Aredis'] = self

        app.redis = self.redises
        return self.redises
