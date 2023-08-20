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
        i = 0
        q_out.put("Started")
        while True:
            i += 1
            in_ = q_in.get()
            if in_ is None:
                break
            frame, params, ons = in_
            for param, system, on in zip(params, self.systems, ons):
                system.set_on(on)
                system.get_param(False).update(param)
            datas = [system.tick(frame) for system in self.systems]
            q_out.put(datas)

            time.sleep(.05)
            if (i % 100) == 0:
                print(f"{i} elements were processed")

    def start(self):
        self.p.start()

    def stop(self):
        self.q_in.put(None)
        self.p.kill()
