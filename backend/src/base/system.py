import abc
from src.base.params import ParamsBase
import typing


class ADASystem(abc.ABC):
    def __init__(self) -> None:
        self.model = None

    @abc.abstractmethod
    def init(self, initial_frame):
        raise NotImplementedError("")

    @abc.abstractmethod
    def tick(self, frame):
        raise NotImplementedError("")

    @abc.abstractmethod
    def draw(self, frame):
        raise NotImplementedError("")

    @abc.abstractmethod
    def is_safe(self):
        raise NotImplementedError("")

    @abc.abstractmethod
    def update_state(self, data):
        raise NotImplementedError("")

    @abc.abstractmethod
    def report(self):
        raise NotImplementedError("")

    @abc.abstractmethod
    def get_param(self, ret_types=True) -> typing.Union[typing.Tuple[str, ParamsBase], ParamsBase]:
        raise NotImplementedError("")
