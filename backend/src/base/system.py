import abc


class ADASystem(abc.ABC):
    def __init__(self) -> None:
        self.model = None

    @abc.abstractmethod
    def tick(self, frame):
        raise "Unimplemented"

    @abc.abstractmethod
    def draw(self, frame):
        raise "Unimplemented"

    @abc.abstractmethod
    def is_safe(self):
        raise "Unimplemented"

    @abc.abstractmethod
    def update_state(self, data):
        raise "Unimplemented"

    @abc.abstractmethod
    def report(self):
        raise "Unimplemented"

    @abc.abstractmethod
    def get_param(self):
        raise "Unimplemented"
