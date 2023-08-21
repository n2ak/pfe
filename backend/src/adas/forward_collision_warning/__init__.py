
from src.base.system import ADASystem
from src.detectors.objects import ObjectDetector


class ForwardCollisionWarningSystem(ADASystem):
    def __init__(self, objects_params) -> None:
        super().__init__("objects")
        self.model = ObjectDetector(
            params=objects_params
        )

    def init(self, initial_frame):
        self.model.init(initial_frame)

    def ready(self):
        return self.model._ready

    def _tick(self, frame):
        return self.model.detect(frame)

    def _draw(self, frame, draw_params):
        return self.model.draw(frame, draw_params)

    def _is_safe(self):
        return self.model.is_safe()

    def update_state(self, data):
        return self.model._update(data)

    def report(self):
        near_objects = self.model.close_objects
        if not len(near_objects):
            return ""
        data = [f"""
            {object.type}:
                distance: {object.distance}
"""
                for object in near_objects]
        data = '\n'.join(data)
        text = f"""
        Forward Collision Warning System:
            Objects in front:
            {
                data
            }        
        """

        return text
