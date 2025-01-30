import cv2
import time
# from param import *
from .utils import seek_video
from .program import Program
from .adas import LaneDepartureWarningSystem, ForwardCollisionWarningSystem
from .drawer import Drawer
from .detectors.lane import YoloLaneDetecorParams
from .detectors.objects import ObjectDetectorParams
from .drawer import DrawParams
from .warner import Warner, WarnerParams


def init_params():
    objects_params = ObjectDetectorParams()
    yolo_lane_params = YoloLaneDetecorParams()
    draw_params = DrawParams()
    return objects_params, yolo_lane_params, draw_params


def main(
        url=None,
        warn=False,
        log=False,
        init_=init_params,
        video=None,
        wav_file=None,
        systems=None
):

    objects_params, yolo_lane_params, draw_params = init_()
    if systems is None:
        systems = [
            ForwardCollisionWarningSystem(objects_params),
            LaneDepartureWarningSystem(yolo_lane_params),
        ]
    drawer = Drawer(draw_params)
    # wav_file = wav_file or "./backend/assets/smartphone_vibrating_alarm_silent-7040 (mp3cut.net).wav"
    wav_file = wav_file or "./backend/assets/Alarm-beeping-sound.wav"

    import os
    # assert os.path.exists(wav_file), print(os.getcwd())
    warnerParams = WarnerParams()
    warnerParams.USE_LOG = False

    # warner = Warner(
    #     wav_file,
    #     warnerParams
    # )
    if url is not None:
        host, port = url
        from .visualizer import ServerVisualizer
        visualizer = ServerVisualizer(host=host, port=port)
    else:
        from .visualizer import WindowVisualizer
        visualizer = WindowVisualizer()
    program = Program(
        systems,
        drawer,
        None,
        visualizer,
        systems_on=True,
    )
    frame_count = 30
    # p.run_as_thread(video, frame_count)
    # print("Running program", id(p))
    program.run(frame_count, video)
    # program.run_server(host, port, False)
    _exit()


def _exit():
    cv2.destroyAllWindows()
    print("Exited")
    import sys
    sys.exit(0)
