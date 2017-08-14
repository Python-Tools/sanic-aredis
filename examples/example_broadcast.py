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

app = Sanic('redis_channel_test')


Broadcast.SetConfig(app,test_channels=("redis://localhost:6379/1",True))
Broadcast(app)

thread = None


def my_handler(x):
    print("my_handler")
    print(x)


@app.listener("before_server_start")
async def sub(app, loop):
    await app.channels["test_channels"].subscribe(my_handler)
    global thread
    print("befor")
    thread = app.channels["test_channels"].sub_in_thread(daemon=True)
@app.listener("before_server_stop")
async def sub_close(app, loop):
    global thread
    thread.stop()
    print("after")

@app.post("/test-my-key")
async def handle(request):
    data = request.json
    result = await app.channels["test_channels"].publish(data["msg"])
    return json({"result":'ok'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
