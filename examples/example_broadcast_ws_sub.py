from sanic import Sanic
from sanic.response import file
from sanic_redis import Broadcast
app = Sanic(__name__)

broadcastdb = Broadcast("redis://localhost:6379/0")
broadcast = broadcastdb(app)

@app.route('/')
async def index(request):
    return await file('websocket.html')


@app.websocket('/feed')
async def feed(request, ws):
    broadcast.subscribe('foo')
    while True:
        data = await broadcast.get_message(
            ignore_subscribe_messages=ignore_subscribe_messages
        )
        if data is not None:
            print('Sending: ' + data)
            await ws.send(data)
            data = await ws.recv()
            print('Received: ' + data)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7000)
