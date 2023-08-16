import abc


class ADASystem(abc.ABC):
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def tick(self, frame):
        raise "Unimplemented"

    @abc.abstractmethod
    def draw(self, frame):
        raise "Unimplemented"

    @abc.abstractmethod
    def is_safe():
        raise "Unimplemented"

    @abc.abstractmethod
    def update_state():
        raise "Unimplemented"

    @abc.abstractmethod
    def report():
        raise "Unimplemented"
