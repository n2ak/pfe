
from src.base.system import ADASystem
from src.detectors.objects import ObjectDetector


class ForwardCollisionWarningSystem(ADASystem):
    def __init__(self, objects_params) -> None:
        super().__init__()
        self.model = ObjectDetector(
            params=objects_params
        )

    def tick(self, frame):
        return self.model.detect(frame)

    def draw(self, frame):
        return self.model.draw(frame)

    def is_safe(self):
        return self.model.is_safe()

    def update_state(self, data):
        return self.model._update(data)

    def get_param(self, ret_types=True):
        params = self.model.params
        if ret_types:
            params = "objects", params
        return params

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
