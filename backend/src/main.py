import cv2
import time
# from param import *
from src.utils import seek_video
from src.program import Program
from src.adas import LaneDepartureWarningSystem, ForwardCollisionWarningSystem
from src.drawer import Drawer
from src.detectors.lane import YoloLaneDetecorParams
from src.detectors.objects import ObjectDetectorParams
from src.drawer import DrawParams
from src.warner import Warner, WarnerParams


def init_params():
    objects_params = ObjectDetectorParams()
    yolo_lane_params = YoloLaneDetecorParams()
    draw_params = DrawParams()
    return objects_params, yolo_lane_params, draw_params


def main(
        host: str,
        port: str,
        warn=False,
        log=False,
        init_=init_params,
        video=None,
        wav_file=None,
        systems=None
):
    from src.server import Server

    objects_params, yolo_lane_params, draw_params = init_()
    if systems is None:
        systems = [
            ForwardCollisionWarningSystem(objects_params),
            LaneDepartureWarningSystem(
                yolo_lane_params
            ),
        ]
    drawer = Drawer(draw_params)
    # wav_file = wav_file or "./backend/assets/smartphone_vibrating_alarm_silent-7040 (mp3cut.net).wav"
    wav_file = wav_file or "./backend/assets/Alarm-beeping-sound.wav"

    import os
    import sys
    assert os.path.exists(wav_file), print(os.getcwd())
    warnerParams = WarnerParams()
    warnerParams.USE_LOG = False

    warner = Warner(
        wav_file,
        warnerParams
    )
    program = Program(
        systems,
        drawer,
        warner,
        systems_on=True
    )
    frame_count = 30

    try:
        # p.run_as_thread(video, frame_count)
        # print("Running program", id(p))
        program.run_thread(program.run, (frame_count, video))
        program.run_server(host, port, False)
        time.sleep(5)
    except KeyboardInterrupt:
        print("Ending")
    except Exception as e:
        print("="*10, "Exception", e)
    _exit()


def _exit():
    cv2.destroyAllWindows()
    print("Exited")
    import sys
    sys.exit(0)
