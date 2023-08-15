
from base import ADASystem
from detectors.car import CarDetector


class ForwardCollisionWarningSystem(ADASystem):
    def __init__(self, car_params) -> None:
        super().__init__()
        self.model = CarDetector(
            params=car_params
        )

    def tick(self, frame):
        return self.model.detect(frame)

    def draw(self, frame):
        return self.model.draw(frame)

    def is_safe(self):
        return self.model.safe

    def update_state(self, data):
        return self.model._update(data)
