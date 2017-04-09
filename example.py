""" To run this example you need additional aioredis package
"""
from sanic import Sanic, response
from sanic.response import json
# import aioredis
from sanic_redis import Redis
import ujson
app = Sanic(__name__)
#redis_pool = aredis.ConnectionPool(host='localhost', port=6379, db=0)
redis = Redis("redis://localhost:6379/0")
db = redis(app)

@app.get("/test-my-key/<key>")
async def handle(request,key):
    val = await db.get(key)
    return response.text(val.decode('utf-8'))

@app.post("/test-my-key")
async def handle(request):
    doc = request.json
    for k,v in doc.items():
        await db.set(k, v)
    return json({"result":True})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
