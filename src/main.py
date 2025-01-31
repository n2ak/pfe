import cv2


def main(
    url=None,
    video=None,
    systems=None,
    draw_params=None
):
    from components.program import Program
    from components.visualizer import ServerVisualizer, WindowVisualizer
    from components.drawer import Drawer
    from components.warner import WarnerParams

    if systems is None:
        pass
        # systems = [
        #     ForwardCollisionWarningSystem(objects_params),
        #     LaneDepartureWarningSystem(yolo_lane_params),
        # ]
    drawer = Drawer(draw_params)
    # wav_file = wav_file or "./backend/assets/smartphone_vibrating_alarm_silent-7040 (mp3cut.net).wav"
    # wav_file = wav_file or "./backend/assets/Alarm-beeping-sound.wav"

    import os
    # assert os.path.exists(wav_file), print(os.getcwd())
    warnerParams = WarnerParams.default()
    warnerParams.USE_LOG.set_value(False)

    # warner = Warner(
    #     wav_file,
    #     warnerParams
    # )
    if url is not None:
        host, port = url
        visualizer = ServerVisualizer(host=host, port=port)
    else:
        visualizer = WindowVisualizer()
    program = Program(
        systems,
        drawer,
        None,
        visualizer,
        systems_on=True,
    )
    frame_count = 30
    program.run(frame_count, video)
    _exit()


def _exit():
    cv2.destroyAllWindows()
    print("Exited")
    import sys
    sys.exit(0)
