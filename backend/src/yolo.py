
class Yolo:
    def __init__(self, version: str, hub=True) -> None:
        if hub is True:
            version = version.lower()
            self.model = load_yolo(version, "../")
        else:
            from ultralytics import YOLO
            self.model = YOLO(version,)

    def detect(self, frame, **kwargs):
        return self.model(frame, **kwargs)

    def predict(self, frame, verbose=False, **kwargs):
        if isinstance(frame, str):
            from src.utils_ import read_rgb
            frame = read_rgb(frame)
        result = self.model.predict(frame, verbose=verbose)
        return result[0]


def load_yolo(version: str, base=None):
    import torch
    if base is not None:
        torch.hub.set_dir(base)
    return torch.hub.load(f'ultralytics/{version}', f'{version}s')
