import cv2


def main(
    url,
    video,
    systems,
    draw_params
):
    from .components.program import Program
    from .components.visualizer import ServerVisualizer, WindowVisualizer
    from .components.drawer import Drawer
    from .components.warner import WarnerParams

    drawer = Drawer(draw_params)
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
