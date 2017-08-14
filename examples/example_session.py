# @Author: Huang Sizhe
# @Date:   10-Apr-2017
# @Email:  hsz1273327@gmail.com
# @Last modified by:   Huang Sizhe
# @Last modified time: 10-Apr-2017
# @License: MIT



""" To run this example you need additional aioredis package
"""
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
