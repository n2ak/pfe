# TODO : draw nothing when no lanes are detected for to many frames


from server import Server
from multiprocessing import Queue, Process
from utils_ import read_video
import cv2
import numpy as np
import time
from param import *
from drawer import Drawer
from typing import List
from base import ADASystem


def simple_on_danger(*x):
    print("Danger")


MAX = 9_000_000


class Program:
    fps_ = [0]

    def __init__(
        self,
        systems: List[ADASystem],
        drawer: Drawer,
        server: Server,
        use_async=False,
        frame_ratio=2,
        on_danger=simple_on_danger,
        draw=True,
        draw_lines=True,
        show_windows=False,
    ) -> None:
        self.systems = systems
        self.use_async = use_async
        self.frame_ratio = frame_ratio
        self.on_danger = on_danger
        self.drawer = drawer
        self.draw = draw
        self.draw_lines = draw_lines
        self.show_windows = show_windows
        self.window_names = ["Main"]
        self.server = server

        if use_async:
            self.init_workers()

        if not use_async:
            self.runner_func = self.run_sync

    def start(self):
        self.lane_worker.start()
        self.car_worker.start()

    def stop(self):
        if self.use_async:
            print("Stopping all workers")
            self.lane_worker.stop()
            self.car_worker.stop()
            self.network.stop()
            if self.draw:
                self.draw_worker.stop()
        # self.detectionWorker.p.close()
        cv2.destroyAllWindows()

    def run_sync(self, frame):
        if self._worker_free is True:
            self.detectionWorker.q_in.put(frame)
            self._worker_free = False
        if not self.detectionWorker.q_out.empty():
            datas = self.detectionWorker.q_out.get()
            assert len(datas) == len(self.systems)
            for data, system in zip(datas, self.systems):
                system.update_state(data)
            self._worker_free = True
        if self.draw:
            frame = self.drawer.draw(
                frame,
                self.systems,
            )
        return frame

    def run(self, video, frame_count):

        if self.use_async:
            self.start()
        else:
            self.detectionWorker = DetectionWorker(
                self.systems
            )
            self.detectionWorker.start()
            assert self.detectionWorker.q_out.get() == "Started"
            self._worker_free = True
        try:
            i = 0
            while True:
                i += 1
                if i > MAX:
                    print("="*10, f"${MAX} iters was reached.")
                    import sys
                    sys.exit()
                    break

                self.on, frame = read_video(video, )  # size=(640, 384))
                if not self.on:
                    break
                frame = self.runner_func(frame)
                # if off:
                #     break
                cv2.imshow("sss", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                Server.set_frame(frame)
                time.sleep(1/frame_count)

            time.sleep(.1)
        except KeyboardInterrupt:
            pass
        self.detectionWorker.stop()
        self.stop()

    def run_as_thread(self, video, fps):
        import threading
        t = threading.Thread(target=self.run, args=(video, fps,))
        t.daemon = True
        t.start()

    def run_server(self, host, port):
        Server.run_server(host, port)


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
            frame = in_

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
