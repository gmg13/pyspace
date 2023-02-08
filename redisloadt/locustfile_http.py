from random import randint

from locust import HttpUser, task, between

multiplier = 2

class RedisUser(HttpUser):
    wait_time = between(0.01, 0.02)

    # @task
    def run_aggregations(self):
        # do some random gets first
        freads = randint(multiplier * 5,multiplier * 15)
        lreads = randint(multiplier * 5,multiplier * 15)
        writes = randint(multiplier, multiplier * 3)
        deletes = randint(0, multiplier)

        # do some random reads first
        for _ in range(freads):
            self.client.get(f'/get/key_{randint(0,99):0>3}')

        # do some random writes in the middle
        for _ in range(writes):
            n = f'{randint(0,99):0>3}'
            self.client.get(f'/set/key_{n}/val_{n}')

        # do some random reads at the end
        for _ in range(lreads):
            self.client.get(f'/get/key_{randint(0,99):0>3}')

        # delete some random keys too
        for _ in range(deletes):
            self.client.get(f'/del/key_{randint(0,99):0>3}')

    @task
    def run_get(self):
        self.client.get("/get/myk")

    @task
    def run_set(self):
        self.client.get("/set/myk/myv")

    @task
    def run_del(self):
        self.client.get("/del/myk")
