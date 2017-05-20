from sanic import Sanic
from sanic.response import file
from sanic_redis import Broadcast
import asyncio
import time
app = Sanic(__name__)

broadcastdb = Broadcast("redis://localhost:6379/0")
broadcast = broadcastdb(app)

thread = None

@app.listener("before_server_start")
async def pub(app, loop):
    async def publish(client):
        import time
        import asyncio
        while True:
            await asyncio.sleep(2)
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            await client.publish('foo', 'test message {time}'.format(time = now))
    global thread
    thread = broadcast.pub_in_thread(publish,daemon=True)
@app.listener("before_server_stop")
async def pub_close(app, loop):
    global thread
    thread.stop()
    print("after")

@app.route('/')
async def index(request):
    return await file('websocket.html')


@app.websocket('/feed')
async def feed(request, ws):

    assert broadcast.subscribed is False
    await broadcast.subscribe('foo')
    #while True:
        #data = await broadcast.wait_for_message()
        #await ws.send(data.get("data"))

    while broadcast.subscribed:
        data = await broadcast.get_message(ignore_subscribe_messages=True)
        if data is not None:
            await ws.send(data.get("data"))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7000)
