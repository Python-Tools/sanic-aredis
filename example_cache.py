# @Author: Huang Sizhe
# @Date:   10-Apr-2017
# @Email:  hsz1273327@gmail.com
# @Last modified by:   Huang Sizhe
# @Last modified time: 10-Apr-2017
# @License: MIT



""" To run this example you need additional aioredis package
"""
from sanic import Sanic, response
from sanic.response import json
# import aioredis
from sanic_redis import Redis
import ujson
app = Sanic(__name__)
class CustomIdentityGenerator(IdentityGenerator):

    def generate(self, key, content):
        return key


def expensive_work(data):
    """some work that waits for io or occupy cpu"""
    return data

#redis_pool = aredis.ConnectionPool(host='localhost', port=6379, db=0)
redis = Redis("redis://localhost:6379/0")
cachedb = redis(app)
cache = cachedb.cache('example_cache',
                         identity_generator_class=CustomIdentityGenerator)
@app.get("/test-my-key/<key>")
async def handle(request,key):
    val = await cachedb.get(key)
    return response.text(val.decode('utf-8'))

@app.post("/test-my-key")
async def handle(request):
    doc = request.json
    for k,v in doc.items():
        await cachedb.set(k, v)
    return json({"result":True})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
