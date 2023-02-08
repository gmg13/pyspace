# main.py : This is the place which hosts the redis proxy API. We
# would host a fast API server which redirects to redis tcp calls
# using py redis client

from fastapi import FastAPI
import redis

global rconn

def init():
    global rconn
    pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
    rconn = redis.Redis(connection_pool=pool)

# initialise the redis connection
init()

# initiate the app
app = FastAPI()

@app.get("/get/{key}")
async def get(key: str):
    global rconn
    return rconn.get(key)

@app.get("/set/{key}/{value}")
async def set(key: str, value: str):
    global rconn
    return rconn.set(key, value)
    
@app.get("/del/{key}")
async def delete(key: str):
    global rconn
    return rconn.delete(key)

