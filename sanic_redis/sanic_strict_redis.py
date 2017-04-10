# @Author: Huang Sizhe
# @Date:   10-Apr-2017
# @Email:  hsz1273327@gmail.com
# @Last modified by:   Huang Sizhe
# @Last modified time: 10-Apr-2017
# @License: MIT

import aredis
from sanic_redis.mixin import SessionMixin
class SaincStrictRedis(aredis.StrictRedis,SessionMixin):
    def __init__(self, host='localhost', port=6379,
                 db=0, password=None, stream_timeout=None,
                 connect_timeout=None, connection_pool=None,
                 unix_socket_path=None,
                 ssl=False, ssl_keyfile=None, ssl_certfile=None,
                 ssl_cert_reqs=None, ssl_ca_certs=None,
                 max_connections=None, retry_on_timeout=False):
        super().__init__(host=host, port=port,
                 db= db, password=password, stream_timeout=stream_timeout,
                 connect_timeout=connect_timeout, connection_pool=connection_pool,
                 unix_socket_path=unix_socket_path,
                 ssl=ssl, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile,
                 ssl_cert_reqs=ssl_cert_reqs, ssl_ca_certs=ssl_ca_certs,
                 max_connections=max_connections, retry_on_timeout=retry_on_timeout)
