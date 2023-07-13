import abc


class LaneDetectorBase(abc.ABC):
    def __init__(
        self,
        # img_shape,
    ) -> None:
        pass

    @abc.abstractmethod
    def draw(self, frame):
        raise "Unimplemented"

    @abc.abstractmethod
    def pipeline(self, frame):
        raise "Unimplemented"

    @abc.abstractmethod
    def is_in_lane(self):
        raise "Unimplemented"
