from typing import Callable
import base64
import asyncio
import websockets
from utils_ import show_window, put_text, scale, timed_function
from multiprocessing import Queue, Process

from lane.ml_lane_detector import LaneDetector
from car import CarDetector
import time
import cv2
import numpy as np
from param import spawn_params_window


class Worker:
    def __init__(self, target, args=()) -> None:
        self.q = Queue()
        args = (self.q, *args)
        self.target = target
        self.p = Process(target=self.main, args=args)
        self.p.daemon = True

    def main(self, *args):
        print("**** Started", self.__class__.__name__)
        try:
            import signal
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            self.target(*args)
        except Exception as e:
            print(e)
            raise e
            pass
        print("**** Stopped", self.__class__.__name__)

    def start(self):
        self.p.start()

    def stop(self):
        self.q.put(None)
        pass


class LaneWorker(Worker):
    def __init__(self, lane_d: LaneDetector) -> None:
        self.q2 = Queue()
        self.detector = lane_d
        self.w = super().__init__(self.tick, args=(self.q2,))

    def tick(self, q: Queue, q2: Queue):
        spawn_params_window()
        # print("Mains up")
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return
            # s = time.time()
            got = q.get()
            if got is None:
                break
            action, frame = got
            # print("LaneWorker", "Got action:", action)
            if action == "detect":
                frame = self.detect(self.detector, frame)
            elif action == "draw":
                frame = self.draw(self.detector, frame)
                q2.put((frame, self.detector.lines))
            else:
                raise str(action) + " not recognized"
            # print("lane Done in:", s, time.time()-s)
        cv2.destroyAllWindows()

    def detect(self, d, frame):
        return lane_detect_one_frame(d, frame)

    def draw(self, d: LaneDetector, frame):
        if d.detected_lines:
            frame = d.draw(frame)
        return frame


class DrawWorker(Worker):
    def __init__(self, frame_ratio, window_names, stack=True) -> None:
        self.q2 = Queue()
        self.window_names = window_names
        self.prev_time = time.time()-1
        self.frame_ratio = frame_ratio
        super().__init__(target=self.draw, args=(self.q2,))
        self.stack = stack
        # for wn in window_names:
        #     print("showing window", wn)

        #     cv2.namedWindow(wn)

    def draw(self, q: Queue, q2: Queue):
        # got = q.get()
        while True:
            # if not q.empty():
            #     got = q.get()
            got = q.get()
            s = time.time()
            if got is None:
                break
            self.frames = got
            # print("Drawing")
            self.update_fps()
            for i in range(len(self.frames)):
                frame = self.frames[i]
                name = self.window_names[i]
                self.draw_fps(frame)
                show_window(name, frame, self.frame_ratio)
            # else:
            #     frame = np.hstack(self.frames)
            #     self.draw_fps(frame)
            #     show_window(name, frame, self.frame_ratio)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                q2.put(None)
            q2.put("")
            # print("Car Done in:", s, time.time()-s)

    fps_ = []

    def draw_fps(self, frame):
        fps = np.mean(self.fps_)
        text = f"FPS: {int(fps)}"
        put_text(frame, text, (7, 90), thickness=2)

    def update_fps(self):
        new = time.time()
        self.fps_.append(1//(new-self.prev_time))
        self.fps_ = self.fps_[-10:]
        # print(self.fps_)
        self.prev_time = new


class CarWorker(Worker):
    def __init__(self, car_d: CarDetector) -> None:
        self.detector = car_d
        self.q2 = Queue()
        self.w = super().__init__(self.tick, args=(self.q2,))

    def tick(self, q: Queue, q2: Queue):
        while True:
            got = q.get()
            if got is None:
                break
            action, frame = got
            # print("CarWorker", "Got action:", action)
            if action == "detect":
                frame = self.detect(self.detector, frame)
                q2.put(self.detector.safe)
            elif action == "draw":
                frame = self.draw(self.detector, frame)
                q2.put(frame)

    def detect(self, d, frame):
        return car_detect_one_frame(d, frame)

    def draw(self, d: CarDetector, frame):
        return d.draw(frame)


def draw_main_window(frame, fr):
    show_window("Main window", frame, fr)


# @timed_function
def lane_detect_one_frame(detector: LaneDetector, frame):
    detector.pipeline(frame)
    if detector.detected_lines:
        is_in_lane = detector.is_in_lane()
        detector.put_text(
            frame, f"In lane: {bool(is_in_lane)}", (7, 50), thickness=2)
    return frame


# @timed_function
def car_detect_one_frame(detector: CarDetector, frame):
    detector.detect(frame)
    return frame


class WebsocketWorker(Worker):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.url = f"ws://{host}:{port}"
        super().__init__(self.serve, args=())
        self.frame = None
        self.clients = []

    def stop(self):
        super().stop()

    def start(self):
        super().start()
        self.running = True

    def encode(self, frame):
        print(frame.shape)
        # frame = scale(frame, 2)
        print(frame.shape)
        encoded = cv2.imencode('.jpg', frame)[1]
        frame = str(base64.b64encode(encoded))
        frame = frame[2:len(frame)-1]
        return frame

    def serve(self, q: Queue):
        self.event_loop = None

        async def send(client):
            try:
                while True:
                    got = self.q.get()
                    if got is None:
                        break
                    frame = got
                    frame = self.encode(frame)
                    await client.send(frame)
                    print("Frame sent to client:")
            except Exception as e:
                print(e)
        start_server = websockets.serve(
            send,
            self.host,
            port=self.port
        )
        print("dir", dir(start_server))
        print("Started server on port : ", self.url)
        # print(str(start_server.ws_server))

        asyncio.get_event_loop().run_until_complete(start_server)
        self.event_loop = asyncio.get_event_loop()
        self.event_loop.run_forever()
        self.end()

    def end(self):
        self.event_loop.stop()
        print("Stopped serving")
        # del start_server
        print("Yep")
        import sys
        sys.exit(0)
