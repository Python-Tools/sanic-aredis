import aredis
import asyncio
import concurrent.futures
import time

async def publish(client):
    # sleep to wait for subscriber to listen
    while True:
        await asyncio.sleep(2)
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(now)
        await client.publish('foo', 'test message {time}'.format(time = now))

if __name__ == '__main__':
    client = aredis.StrictRedis()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(publish(client))
