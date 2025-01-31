from src.main import main


if __name__ == "__main__":
    import sys
    import cv2
    from src.adas.detectors.lane.params import YoloLaneDetecorParams
    from src.adas import LaneDepartureWarningSystem
    from src.components.drawer import DrawParams
    from pathlib import Path

    use_server = None
    url = None
    if use_server:
        url = "0.0.0.0:9999".split(":")
    video_file = sys.argv[1]
    assert Path(video_file).exists(), video_file
    video = cv2.VideoCapture(video_file)

    params = YoloLaneDetecorParams.default(
        LANE_THRESHOLD=150
    )
    systems = [
        LaneDepartureWarningSystem(params),
    ]
    main(
        url,
        video,
        systems,
        DrawParams.default()
    )
    video.release()
