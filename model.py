import asyncio
import random
import queue
import multiprocessing
import time
from concurrent import futures

class consumer():
    def __init__(self, num):
        self.coro_num = num

    def run(self, q):
        loop = asyncio.get_event_loop()
        loop.create_task(self.run_helper(q))
        loop.run_forever()
        loop.close()

    async def run_helper(self, q):
        await asyncio.gather(*(self.real_work(i, q) for i in range(self.coro_num)))

    async def real_work(self, id, q):
        while True:
            try:
                #print('try get...')
                token = q.get_nowait()
            except:
                # Important...transfer owership to other coroutine
                await asyncio.sleep(0.5)
                continue
            await asyncio.get_event_loop().run_in_executor(None, self.simulate_io_bound_work)
            print(id, ':', token)



    def simulate_io_bound_work(self):
        #print('reach here1')
        time.sleep(10)
        #print('reach here2')

class model():
    def __init__(self):
        self.q = multiprocessing.Queue()
        self.consumer_num = 20
        self.producer = multiprocessing.Process(target=self.produce)
        self.consumer = consumer(self.consumer_num)

    def produce(self):
        i = 0
        while True:
            i += 1
            time.sleep(0.5)
            self.q.put(i)


    def consume(self):
        while True:
            if self.q.empty():
                continue
            token = self.q.get()
            print(token ** 2)

    def run(self):
        self.producer.start()
        self.consumer.run(self.q)


m = model()
m.run()
