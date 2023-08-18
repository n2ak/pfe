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
from src.warning import Warner


def init_params(initial_frame):
    objects_params = ObjectDetectorParams()
    yolo_lane_params = YoloLaneDetecorParams()
    draw_params = DrawParams()
    return objects_params, yolo_lane_params, draw_params


def main(
        video,
        host: str,
        port: str,
        warn=False,
        log=False,
        init_=init_params
):
    on, initial_frame = video.read()
    h, w = initial_frame.shape[:2]
    from src.server import Server
    server = Server()

    objects_params, yolo_lane_params, draw_params = init_(initial_frame)
    systems = [
        ForwardCollisionWarningSystem(objects_params),
        # LaneDepartureWarningSystem(
        #     yolo_lane_params
        # ),
    ]
    drawer = Drawer(draw_params)
    warner = Warner(use_sound=warn, log=log)
    program = Program(
        systems,
        drawer,
        server,
        warner,
    )
    frame_count = 30

    try:
        # p.run_as_thread(video, frame_count)
        # print("Running program", id(p))
        program.run_thread(program.run, (video, frame_count))
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
