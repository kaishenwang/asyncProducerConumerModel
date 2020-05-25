import asyncio
import multiprocessing
import time
from concurrent import futures

class consumer(multiprocessing.Process):
    def __init__(self, num, queue, flag):
        multiprocessing.Process.__init__(self)
        self.coro_num = num
        self.q = queue
        self.run_flag = flag

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.create_task(self.run_helper())
            loop.run_forever()
        except KeyboardInterrupt:
            loop.close()

    async def run_helper(self):
        await asyncio.gather(*(self.real_work(i) for i in range(self.coro_num)))

    async def real_work(self, id):
        while self.run_flag:
            try:
                token = self.q.get_nowait()
            except:
                # Important...transfer owership to other coroutine
                await asyncio.sleep(0.001)
                continue
            await asyncio.get_event_loop().run_in_executor(None, self.simulate_io_bound_work)
            print(id, ' get ', token)

    def simulate_io_bound_work(self):
        time.sleep(5)

class model():
    def __init__(self):
        self.q = multiprocessing.Queue(1000)
        self.consumer_num = 10
        self.run_flag = multiprocessing.Value('B', 1)
        self.consumer = consumer(self.consumer_num, self.q, self.run_flag)

    def run(self):
        i = 0
        self.consumer.start()
        while self.run_flag:
            try:
                i += 1
                time.sleep(1)
                self.q.put(i)
                print('Put ', i)
            except KeyboardInterrupt:
                print('KeyboardInterrupt caught. Exiting...')
                quit()
                self.consumer.join()
        
    def quit():
        self.run_flag = 0


m = model()
m.run()
