# @Author: Huang Sizhe
# @Date:   10-Apr-2017
# @Email:  hsz1273327@gmail.com
# @Last modified by:   Huang Sizhe
# @Last modified time: 10-Apr-2017
# @License: MIT



""" To run this example you need additional aioredis package
"""
from sanic import Sanic, response
from sanic.response import json, text
# import aioredis
from sanic_redis import Broadcast
import time

app = Sanic(__name__)


broadcastdb = Broadcast("redis://localhost:6379/0")
broadcast = broadcastdb(app)
thread = None


def my_handler(x):
    print("my_handler")
    print(x)


@app.listener("before_server_start")
async def sub(app, loop):
    await broadcast.subscribe(**{'example_channel1': my_handler})
    global thread
    print("befor")
    thread = broadcast.run_in_thread(daemon=True)
@app.listener("before_server_stop")
async def sub_close(app, loop):
    global thread
    thread.stop()
    print("after")

@app.post("/test-my-key")
async def handle(request):
    data = request.json
    result = await broadcast.publish('example_channel1', data["msg"])
    return json({"result":'ok'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
