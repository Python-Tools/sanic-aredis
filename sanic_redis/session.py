# @Author: Huang Sizhe
# @Date:   10-Apr-2017
# @Email:  hsz1273327@gmail.com
# @Last modified by:   Huang Sizhe
# @Last modified time: 10-Apr-2017
# @License: MIT

import uuid
try:
    import ujson
except:
    import json as ujson
import aredis
from sanic_session.base import BaseSessionInterface, SessionDict

class AredisSessionInterface(BaseSessionInterface):
    def __init__(
            self,redis_db,
            domain: str=None, expiry: int = 2592000,
            httponly: bool=True, cookie_name: str='session',
            prefix: str='session:'):
        """Initializes a session interface backed by Redis.
        Args:
            redis_getter (Callable):
                Coroutine which should return an asyncio_redis connection pool
                (suggested) or an asyncio_redis Redis connection.
            domain (str, optional):
                Optional domain which will be attached to the cookie.
            expiry (int, optional):
                Seconds until the session should expire.
            httponly (bool, optional):
                Adds the `httponly` flag to the session cookie.
            cookie_name (str, optional):
                Name used for the client cookie.
            prefix (str, optional):
                Memcache keys will take the format of `prefix+session_id`;
                specify the prefix here.
        """
        self.redis_db = redis_db
        self.expiry = expiry
        self.prefix = prefix
        self.cookie_name = cookie_name
        self.domain = domain
        self.httponly = httponly

    async def open(self, request):
        """Opens a session onto the request. Restores the client's session
        from Redis if one exists.The session data will be available on
        `request.session`.
        Args:
            request (sanic.request.Request):
                The request, which a sessionwill be opened onto.
        Returns:
            dict:
                the client's session data,
                attached as well to `request.session`.
        """
        sid = request.cookies.get(self.cookie_name)

        if not sid:
            sid = uuid.uuid4().hex
            session_dict = SessionDict(sid=sid)
        else:
            redis_connection = self.redis_db
            val = await redis_connection.get(self.prefix + sid)

            if val is not None:
                data = ujson.loads(val)
                session_dict = SessionDict(data, sid=sid)
            else:
                session_dict = SessionDict(sid=sid)

        request['session'] = session_dict
        return session_dict

    async def save(self, request, response) -> None:
        """Saves the session into Redis and returns appropriate cookies.
        Args:
            request (sanic.request.Request):
                The sanic request which has an attached session.
            response (sanic.response.Response):
                The Sanic response. Cookies with the appropriate expiration
                will be added onto this response.
        Returns:
            None
        """
        if 'session' not in request:
            return
        redis_connection = self.redis_db
        #redis_connection = await self.redis_getter()
        key = self.prefix + request['session'].sid
        if not request['session']:
            await redis_connection.delete([key])

            if request['session'].modified:
                self._delete_cookie(request, response)

            return

        val = ujson.dumps(dict(request['session']))

        await redis_connection.setex(key, self.expiry, val)

        self._set_cookie_expiration(request, response)



class Core:
    """session与其他不太一样,session不提供多数据库支持
    """
    @staticmethod
    def SetConfig(app, uri):
        app.config.REDIS_SESSION_URI = uri
        return app

    def __init__(self,app=None):
        self.session = None
        if app:
            self.init_app(app)
        else:
            pass



    def init_app(self, app):
        """绑定app,如果config有REDIS_SESSION_URI,那么可以不用初始化redis_uri
        """
        if app.config.REDIS_SESSION_URI and isinstance(app.config.REDIS_SESSION_URI, str):
            self.REDIS_SESSION_URI = app.config.REDIS_SESSION_URI
            self.app = app
            redis = aredis.StrictRedis.from_url(app.config.REDIS_SESSION_URI)
            session = AredisSessionInterface(redis,prefix=app.name+'-session:')
            self.session = session

        else:
            raise ValueError(
                "nonstandard sanic config REDIS_SESSION_URI,REDIS_SESSION_URI must be a string")

        if "extensions" not in app.__dir__():
            app.extensions = {}
        app.extensions['Session'] = self

        @app.middleware('request')
        async def add_session_to_request(request):
            # before each request initialize a session
            # using the client's request
            await session.open(request)


        @app.middleware('response')
        async def save_session(request, response):
            # after each request save the session,
            # pass the response to set client cookies
            await session.save(request, response)
        app.session = self.session
        return app
