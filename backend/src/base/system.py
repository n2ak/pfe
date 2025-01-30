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

    def init(self, initial_frame):
        name = self.name
        self._init(initial_frame)
        print(f"{name} has been initialized.")

    def stop(self):
        name = self.name
        self._stop()
        print(f"{name} has stopped.")

    @abc.abstractmethod
    def _init(self, frame):
        raise NotImplementedError(self)

    @abc.abstractmethod
    def _tick(self, frame):
        raise NotImplementedError(self)

    @abc.abstractmethod
    def _stop(self, frame, draw_params):
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

    @abc.abstractmethod
    def _warmup(self):
        raise NotImplementedError(self)

    def warmup(self):
        name = self.name
        print(f"{name} is warming up...")
        self._warmup()

    def tick(self, frame):
        if not self._on:
            return None
        name = self.name
        import time
        s = time.monotonic()
        res = self._tick(frame)
        e = time.monotonic()
        print(f"{name} took {e-s:.4f} secs")
        return res

    def draw(self, frame, draw_params):
        if not self._on:
            return frame
        return self._draw(frame, draw_params)

    def is_safe(self):
        if not self._on:  # or not self.ready():
            return True
        return self._is_safe()

    def in_danger(self):
        return not self.is_safe()
