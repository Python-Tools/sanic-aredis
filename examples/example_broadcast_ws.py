from sanic import Sanic
from sanic.response import file
from sanic_redis import Broadcast
import asyncio
import time
app = Sanic("test_ws_channel")
Broadcast.SetConfig(app,test_channels=("redis://localhost:6379/1",True))
Broadcast(app)
thread = None

@app.listener("before_server_start")
async def pub(app, loop):
    async def publish(client):
        import time
        import asyncio
        while True:
            await asyncio.sleep(2)
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            await client.publish('test message {time}'.format(time = now))
    global thread
    thread = app.channels["test_channels"].pub_in_thread(publish,daemon=True)

@app.listener("after_server_stop")
async def pub_close(app, loop):
    global thread
    thread.stop()
    print("after")

@app.route('/')
async def index(request):
    return await file('websocket.html')


@app.websocket('/feed')
async def feed(request, ws):
    assert app.channels["test_channels"].subscribed is False
    await app.channels["test_channels"].subscribe()

    while app.channels["test_channels"].subscribed:
        data = await app.channels["test_channels"].get_message()
        if data is not None:
            await ws.send(data.get("data"))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7000)
