# TODO : draw nothing when no lanes are detected for to many frames
import time
from src.utils_ import read_video
from src.server import Server
from src.processor import Processor


MAX = 9_000_000


class Program:
    fps_ = [0]

    def __init__(
        self,
        systems,
        drawer,
        server: Server,
        warner,
        show_window=False,
    ) -> None:
        self.systems = systems
        self.drawer = drawer
        self.window_names = ["Main"]
        self.server = server
        self.show_window = show_window

        self.processor = Processor(
            systems,
            warner,
            drawer,
        )

    def stop(self):
        self.processor.stop()

    def show_main_window(self, frame, name="Main"):
        from src.utils_ import show_window
        return show_window(name, frame, ratio=1)

    def run(self, video, frame_count):
        self.processor.start()
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

    def run_thread(self, func, args):
        import threading
        t = threading.Thread(target=func, args=args)
        t.daemon = True
        t.start()

    def run_server(self, host, port, debug=True):
        Server.run_server(host, port, self, debug=debug,)

    def get_params(self, ret_types=True, include_drawer=False):
        return self.processor.get_params(ret_types=ret_types, include_drawer=include_drawer)
