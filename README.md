# sanic-redis

aredis的sanic扩展,具体包括如下几个模块:

+ Redis 直接操作redis,与aredis接口基本一致
+ Session 专门处理session,由于sanic一般都会用多个worker运行,因此基于内存的session基本是行不通的.redis刚好可以用来存session
+ Cache 用来缓存比较重的任务的结果,如果我们有的任务比较重,那么我们可以让它自己运算,然后存在redis中,
+ Broadcast 这个模块是用来做简易多对多消息队列的,负责将消息广播给注册的频道或者从频道接收广播
+ Queue 使用list构建队列系统，使用sorted set甚至可以构建有优先级的队列系统。
