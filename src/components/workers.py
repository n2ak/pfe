from typing import List
import time
from src.adas import ADASystem
from multiprocessing import Queue, Process


class DetectionWorker:
    def __init__(self, systems: List[ADASystem], args=()) -> None:
        self.q_in = Queue()
        self.q_out = Queue()
        args = (self.q_in, self.q_out, *args)
        self.p = Process(target=self.main, args=args)
        self.p.daemon = True
        self.systems = systems

    def main(self, q_in: Queue, q_out: Queue):
        try:
            for s in self.systems:
                s.warmup()
            q_out.put("Started")
            import itertools
            for i in itertools.count():
                in_ = q_in.get()
                if in_ is None:
                    break
                frame, params, ons = in_
                for param, system, on in zip(params, self.systems, ons):
                    system.set_on(on)
                    # system.get_params().update(param)
                datas = [system.tick(frame) for system in self.systems]
                q_out.put(datas, block=False)

                time.sleep(.03)
                if (i % 100) == 0:
                    print(f"{i} elements were processed")
        except Exception as e:
            raise e
        # for s in self.systems:
        #     s.stop()

    def start(self):
        print("Starting detection worker")
        self.p.start()

    def stop(self):
        self.q_in.put(None)
        self.p.kill()
        for s in self.systems:
            s.stop()
