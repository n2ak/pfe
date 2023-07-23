import cv2
import time
from param import *
from main import Program
from utils_ import seek_video
from lane import MlLaneDetector, YoloLaneDetecor
from car import CarDetector


def init_ml_lane_detector(frame_shape):
    use_bitwise = CheckBoxParam("Use Bitwise", PARAMS_WINDOW, val=True)
    draw_roi = CheckBoxParam("Draw ROI", PARAMS_WINDOW, val=False)
    color_threshold = TrackbarParam("Color trshd", PARAMS_WINDOW, 100, 255)
    use_canny = CheckBoxParam("Use canny", PARAMS_WINDOW, val=True)
    canny_thresholds = (
        TrackbarParam("Canny trshd 1", PARAMS_WINDOW, 100, 255),
        TrackbarParam("Canny trshd 2", PARAMS_WINDOW, 100, 255)
    )
    return MlLaneDetector(
        frame_shape,
        use_bitwise=use_bitwise,
        draw_roi=draw_roi,
        show_perp_lines=False,
        color_threshold=color_threshold,
        window_size_ratio=2,
        use_canny=use_canny,
        canny_thresholds=canny_thresholds
    )


def main(host: str, port: str, use_async: bool = False):
    F = 2800
    FOCAL_LENGTH = 4.74
    config = {
        "polygon_height": 150,
        "lane_center1": 600,
        "lane_width1": 125*2,
        "lane_center2": 700,
        "lane_width2": 350*2,
    }
    src = "../rsrc/tanj.mp4"
    video = cv2.VideoCapture(src)
    seek_video(video, 2 * 60)

    on, initial_frame = video.read()
    assert on, ""

    # ld = init_ml_lane_detector(initial_frame.shape[:2])
    # ld.init_polygon(config)
    ld = YoloLaneDetecor()
    car_d = CarDetector(F, FOCAL_LENGTH, initial_frame.shape[1]//2)

    # car_d = None
    p = Program(
        ld,
        car_d,
        use_async=use_async,
        frame_ratio=2,
        draw=True,
        draw_lines=False,
        show_windows=False,
    )
    try:
        p.run_as_thread(video)
        p.run_server(host, port)
        time.sleep(5)
    except KeyboardInterrupt:
        print("daoda")
    except Exception as e:
        print("="*10, "Exception", e)
    _exit()


def _exit():
    cv2.destroyAllWindows()
    print("Exited")
    import sys
    sys.exit(0)


if __name__ == "__main__":
    import sys
    run_async = "async" in sys.argv
    host, port = "0.0.0.0:9999".split(":")
    main(host, port, use_async=run_async)
