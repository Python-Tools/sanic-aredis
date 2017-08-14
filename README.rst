
sanic-redis
===============================

version: 0.0.5

author: hsz

email: hsz1273327@gmail.com

Feature
----------------------
* 使用python的原生协程
* 使用aredis访问redis,与aredis接口基本一致
* 支持多db多uri,一个应用往往使用不止一个数据库
* 支持session,sanic一般都会用多个worker运行,因此基于内存的session基本是行不通的.redis刚好可以用来存session
* 支持cache,用来缓存比较重的任务的结果,如果我们有的任务比较重,那么我们可以让它自己运算,然后存在redis中,
* 支持channel,redis自带发布订阅模式


Install
--------------------------------

- ``python -m pip install sanic-redis``


Usage
---------------------------------

不同的功能是用不同类,但用法接近

* redis,app中需要有配置`REDIS_SETTINGS`,它必须是一个由名字,uri组成的字典,也可以使用`SetConfig(app, **confs)`类方法来设置该参数
* session,app中需要有配置`REDIS_SESSION_URI`,它必须是一个uri字符串,也可以使用`SetConfig(app, uri)`类方法来设置该参数
* cache,app中需要有配置`REDIS_CACHE_SETTINGS`,它必须是一个由名字,uri组成的字典,也可以使用`SetConfig(app, **confs)`类方法来设置该参数
* channel,app中需要有配置`REDIS_CHANNEL_SETTINGS`,它必须是一个由名字,(uri,ignore_subscribe_messages:bool)组成的字典,也可以使用`SetConfig(app, **confs)`类方法来设置该参数

初始化完成后就可在app的对应的元素中访问到他们了

* reids:app.redis[name]
* session:app.session,也可以使用request['session']来获取
* cache:app.caches[name]
* channels:app.channels[name]


Example
-------------------------------

1. redis

.. code:: python

    from sanic import Sanic, response
    from sanic.response import json
    # import aioredis
    from sanic_redis import Redis,Namespace
    import ujson
    app = Sanic('redis_test')
    #redis_pool = aredis.ConnectionPool(host='localhost', port=6379, db=0)
    Redis.SetConfig(app,test="redis://localhost:6379/1")
    Redis(app)
    appspace = Namespace(app.name)

    @app.get("/test-my-key/<key>")
    async def handle(request,key):
        val = await request.app.redis["test"].get(appspace(key))
        return response.text(val.decode('utf-8'))

    @app.post("/test-my-key")
    async def handle(request):
        doc = request.json
        for k,v in doc.items():
            await request.app.redis["test"].set(appspace(k), v)
        return json({"result":True})

    if __name__ == '__main__':
        app.run(host="0.0.0.0", port=8000)


2. session

.. code:: python

    from sanic import Sanic, response
    from sanic.response import json,text
    # import aioredis
    from sanic_redis import Session
    import ujson
    app = Sanic('redis_session_test')

    Session.SetConfig(app,"redis://localhost:6379/1")
    Session(app)

    @app.route("/")
    async def test(request):
        # interact with the session like a normal dict
        if not request['session'].get('foo'):
            request['session']['foo'] = 0

        request['session']['foo'] += 1
        response = text(request['session']['foo'])
        return response

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8000, debug=True)

3. cache

.. code:: python

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


4. channel

.. code:: python

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

5. 使用channel配合websocket

服务端:

.. code:: python

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


客户端:

.. code:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>WebSocket demo</title>
        </head>
        <body>
            <script>
                var ws = new WebSocket('ws://localhost:7000/feed'),
                    messages = document.createElement('ul');
                ws.onmessage = function (event) {
                    var messages = document.getElementsByTagName('ul')[0],
                        message = document.createElement('li'),
                        content = document.createTextNode('Received: ' + event.data);
                    message.appendChild(content);
                    messages.appendChild(message);
                };
                document.body.appendChild(messages);
            </script>
        </body>
    </html>



TODO
-------------------------------

* Queue 使用list构建队列系统，使用sorted set甚至可以构建有优先级的队列系统。
