import abc
from src.base.params import ParamsBase
from .parameterizable import Parameterizable
import typing


class ADASystem(abc.ABC, Parameterizable):
    def __init__(self, path, name=None, is_on=True) -> None:
        super().__init__(path, name)
        self.model = None
        self._on = is_on

    def set_on(self, val):
        self._on = val

    @abc.abstractmethod
    def init(self, initial_frame):
        raise NotImplementedError(self)

    @abc.abstractmethod
    def _tick(self, frame):
        raise NotImplementedError(self)

    @abc.abstractmethod
    def _draw(self, frame, draw_params):
        raise NotImplementedError(self)

    @abc.abstractmethod
    def _is_safe(self):
        raise NotImplementedError(self)

    @abc.abstractmethod
    def update_state(self, data):
        raise NotImplementedError(self)

    @abc.abstractmethod
    def report(self):
        raise NotImplementedError(self)

    @abc.abstractmethod
    def ready(self):
        raise NotImplementedError(self)

    def tick(self, frame):
        if not self._on:
            return None
        return self._tick(frame)

    def draw(self, frame, draw_params):
        if not self._on:
            return frame
        return self._draw(frame, draw_params)

    def is_safe(self):
        if not self._on:  # or not self.ready():
            return True
        return self._is_safe()
