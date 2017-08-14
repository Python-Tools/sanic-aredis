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
from sanic_redis import Cache
import time

app = Sanic('redis_test')

def expensive_work(data):
    """some work that waits for io or occupy cpu"""
    time.sleep(2)
    return data

Cache.SetConfig(app,test_cache="redis://localhost:6379/1")
Cache(app)


@app.post("/test-my-key")
async def handle(request):
    data = request.json
    result = await request.app.caches["test_cache"].set('example_key', expensive_work(data), data)
    return json({"result":request.app.caches["test_cache"]._gen_identity('example_key', data)})

@app.get("/test-my-key/<key>")
async def handle(request,key):
    res = await request.app.caches["test_cache"].get_by_key(key)
    return json(res)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
