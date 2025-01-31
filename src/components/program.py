# TODO : draw nothing when no lanes are detected for to many frames
import time
from src.utils import read_video
from .processor import Processor
from .visualizer import Visualizer

MAX = 9_000_000


class Program:
    fps_ = [0]

    def __init__(
        self,
        systems,
        drawer,
        warner,
        visualizer: Visualizer,
        show_window=False,
        systems_on=False,
    ) -> None:
        self.show_window = show_window

        self.processor = Processor(
            systems,
            warner,
            drawer,
        )
        self._frame = None
        self.visualizer = visualizer
        self.visualizer.update_kwargs(program=self)

    def stop(self):
        self.processor.stop()
        self.visualizer.stop()

    def _run(self,  fps, video=None):
        def get_frame():
            if video is not None:
                on, frame = read_video(video)
            else:
                on, frame = True, self._frame.copy()
            return on, frame
        import itertools
        for i in itertools.count():
            start = time.monotonic()
            if i > MAX:
                print("="*10, f"${MAX} iters was reached.")
                import sys
                sys.exit()
                break
            # get frame
            self.on, frame = get_frame()  # size=(640, 384))
            # if not self.on:
            #     break
            # process frame ?
            # run systems
            self.processor.set_frame(frame)
            result_frame = self.processor.tick(frame)
            # warn if needed
            self.processor.warn_if_needed()
            # show frame
            self.visualizer.show(result_frame)

            end = time.monotonic()
            delta = end - start
            if delta < (1/fps):
                time.sleep(1/fps - delta)
            stop = self.visualizer.should_stop()
            if stop:
                break

    def init(self, frame):
        self.processor.init(frame)
        self.processor.start()

    def run(self, fps, video=None):
        self.visualizer.start()
        print(f"{video=}")
        if video is not None:
            while not self.visualizer.is_ready():
                print("Waiting for visualizer to start..")
                time.sleep(.5)
            on, frame = read_video(video)
            assert on is True
        else:
            while self._frame is None:
                print("Waiting for first frame..")
                time.sleep(.2)
            frame = self._frame
        try:
            self.init(frame)
            self._run(fps, video=video)
        except KeyboardInterrupt:
            pass
        self.stop()

    def get_params(self, ret_types=True, include_drawer=False):
        return self.processor.get_params(ret_types=ret_types, include_drawer=include_drawer)
