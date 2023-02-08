from random import randint
from locust import User, between, TaskSet, task, events
import redis
import time


# Create the static connection pool definitions
pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
rconn = redis.Redis(connection_pool=pool)

def execute_query(name, *args):
    return getattr(rconn, name)(*args)

def fire_event(name,
               environment,
               start_time,
               start_perf_counter,
               context,
               exception=None):
    environment.events.request.fire(
        request_type=f"REDIS",
        name=name,
        start_time=start_time,
        response_time=(time.perf_counter() - start_perf_counter) * 1000,
        response_length=1,
        context=context,
        exception=exception,
    )


class RedisClient:
    "The Redis client that wraps the queries"

    def __init__(self, *, environment):
        self.environment = environment

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            start_perf_counter = time.perf_counter()
            start_time = time.time()

            try:
                execute_query(name, *args, **kwargs)

                # fire on success
                fire_event(
                    name,
                    self.environment,
                    start_time,
                    start_perf_counter,
                    {}
                )
            except Exception as e:
                fire_event(
                    name,
                    self.environment,
                    start_time,
                    start_perf_counter,
                    {},
                    exception=e
                )

        return wrapper


class CustomTaskSet(TaskSet):
    def randstr(self):
        return f'key_{randint(0,99):0>3}'

    @task(20)
    def get(self):
        self.client.get(self.randstr())

    @task(4)
    def set(self):
        self.client.set(self.randstr(), "1")

    @task(1)
    def delete(self):
        self.client.delete(self.randstr())


# This class will be executed when you fire up locust
class RedisUser(User):
    min_wait = 0.001
    max_wait = 0.005

    tasks = [CustomTaskSet]
    wait_time = between(min_wait, max_wait)

    def __init__(self, environment):
        super().__init__(environment)
        self.client = RedisClient(environment=environment)
