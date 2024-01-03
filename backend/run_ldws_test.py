from src.main import main


if __name__ == "__main__":
    import sys
    import cv2
    from src.utils import seek_video

    run_async = "async" in sys.argv
    warn = "warn" in sys.argv
    log = "log" in sys.argv
    use_webcam = "webcam" in sys.argv

    host, port = "0.0.0.0:9999".split(":")
    video = None
    if not use_webcam:
        video_file = None  # video path
        video = cv2.VideoCapture(video_file)
    wav_file = "./backend/assets/smartphone_vibrating_alarm_silent-7040 (mp3cut.net).wav"

    from src.detectors.lane import YoloLaneDetecorParams
    from src.adas import LaneDepartureWarningSystem

    params = YoloLaneDetecorParams()
    params.LANE_THRESHOLD = 150
    systems = [
        LaneDepartureWarningSystem(params),
    ]
    main(
        host,
        port,
        warn=warn,
        log=log,
        video=video,
        wav_file=wav_file,
        systems=systems
    )
    video.release()
