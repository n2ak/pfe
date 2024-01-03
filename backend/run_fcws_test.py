from src.main import main


if __name__ == "__main__":
    import sys
    import cv2
    from src.utils import seek_video

    host, port = "0.0.0.0:9999".split(":")
    video = None
    video_file = "./backend/assets/tanj.mp4"
    import os
    assert os.path.exists(video_file)
    video = cv2.VideoCapture(video_file)
    seek_video(video, 2 * 60)

    wav_file = "./backend/assets/smartphone_vibrating_alarm_silent-7040 (mp3cut.net).wav"
    from src.detectors.objects import ObjectDetectorParams
    from src.adas import ForwardCollisionWarningSystem
    objectDetectorParams = ObjectDetectorParams()
    objectDetectorParams.F = 1500
    objectDetectorParams.CAR_MIN_DISTANCE = 20
    systems = [
        ForwardCollisionWarningSystem(objectDetectorParams),
    ]
    main(
        host,
        port,
        video=video,
        wav_file=wav_file,
        systems=systems
    )
    video.release()
