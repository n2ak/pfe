# TODO : draw nothing when no lanes are detected for to many frames
import time
from src.utils import read_video, bytes_to_image
from src.server import Server
from src.processor import Processor


MAX = 9_000_000


class Program:
    fps_ = [0]

    def __init__(
        self,
        systems,
        drawer,
        warner,
        show_window=False,
        systems_on=False,
    ) -> None:
        self.show_window = show_window

        self.processor = Processor(
            systems,
            warner,
            drawer,
            systems_on=systems_on
        )
        self._frame = None

    def stop(self):
        self.processor.stop()

    def show_main_window(self, frame, name="Main"):
        from src.utils import show_window
        return show_window(name, frame, ratio=1)

    def _run(self,  frame_count, video=None):
        self.processor.start()

        def get_frame():
            if video is not None:
                on, frame = read_video(video)
            else:
                on, frame = True, self._frame.copy()
            return on, frame
        try:
            i = 0
            while True:
                i += 1
                if i > MAX:
                    print("="*10, f"${MAX} iters was reached.")
                    import sys
                    sys.exit()
                    break
                self.on, frame = get_frame()  # size=(640, 384))
                if not self.on:
                    break
                self.processor.set_frame(frame)
                result_frame = self.processor.tick(frame)
                # frame = self.tick(frame)
                if self.show_window and self.show_main_window(result_frame):
                    break

                Server.set_frame(result_frame)
                time.sleep(1/frame_count)
        except KeyboardInterrupt:
            pass
        self.stop()

    def init(self, frame):
        self.processor.init(frame)

    def run(self,  frame_count, video=None):
        if video is not None:
            while not Server.has_started():
                print("Waiting for server to start..")
                time.sleep(.5)
            on, frame = read_video(video)
            assert on is True
        else:
            while self._frame is None:
                print("Waiting for first frame..")
                time.sleep(.2)
            frame = self._frame
        self.init(frame)
        self._run(frame_count, video=video)

    def run_thread(self, func, args):
        import threading
        t = threading.Thread(target=func, args=args)
        t.daemon = True
        t.start()

    def run_server(self, host, port, debug=True):
        Server.run_server(host, port, self, debug=debug,)

    def get_params(self, ret_types=True, include_drawer=False):
        return self.processor.get_params(ret_types=ret_types, include_drawer=include_drawer)

    def set_frame_from_bytes(self, bytes):
        self._frame = bytes_to_image(bytes)
