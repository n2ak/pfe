
from utils_ import seek_video
from lane_detector import LaneDetector
from car import CarDetector
import cv2
import numpy as np
import time
from workers import *
from param import *
from main import Program


def main(use_async: bool):
    F = 2800
    FOCAL_LENGTH = 4.74
    config = {
        "polygon_height": 150,
        "lane_center1": 600,
        "lane_width1": 125*2,
        "lane_center2": 700,
        "lane_width2": 350*2,
    }
    print("height", 720 - 150)
    src = "../rsrc/tanj.mp4"
    video = cv2.VideoCapture(src)
    seek_video(video, 2 * 60)
    print("done waiting")
    on, initial_frame = video.read()
    assert on, ""
    ld = LaneDetector(
        initial_frame.shape[:2],
        use_bitwise=CheckBoxParam("Use Bitwise", PARAMS_WINDOW, val=True),
        draw_roi=CheckBoxParam("Draw ROI", PARAMS_WINDOW, val=False),
        show_perp_lines=False,
        color_threshold=TrackbarParam("Color trshd", PARAMS_WINDOW, 100, 255),
        window_size_ratio=2,
        use_canny=CheckBoxParam("Use canny", PARAMS_WINDOW),
        canny_thresholds=(
            TrackbarParam("Color trshd 1", PARAMS_WINDOW, 100, 255),
            TrackbarParam("Color trshd 2", PARAMS_WINDOW, 100, 255)
        )
    )
    car_d = CarDetector(F, FOCAL_LENGTH, initial_frame.shape[1]//2)
    ld.init_polygon(config)
    p = Program(
        ld,
        car_d,
        use_async=use_async,
        frame_ratio=2,
        draw=True,
    )
    p.run(video)
    time.sleep(1)
    print("Exited")
    import sys
    cv2.destroyAllWindows()
    sys.exit(0)


if __name__ == "__main__":
    import sys
    run_async = "async" in sys.argv
    main(run_async)
