from src.adas import ADASystem
from .warner import Warner
from .drawer import Drawer
from .workers import DetectionWorker
from src.base.parameterizable import Parameterizable
from src.base.params import ParamsBase, BooleanParam


class ProcessorParams(ParamsBase):
    def __init__(self, systems: list[ADASystem]) -> None:
        params = [
            BooleanParam(s.name, f"{s.name}", True)
            for s in systems
        ]
        super().__init__(params)


class Processor(Parameterizable):
    def __init__(
        self,
        systems: list[ADASystem],
        warner: Warner,
        drawer: Drawer,
    ) -> None:
        super().__init__(
            "processor",
            ProcessorParams(systems),
        )
        self.systems = systems
        self.warner = warner
        self.drawer = drawer
        # self.params.print()

    def init(self, initial_frame):
        for system in self.systems:
            system.init(initial_frame)

    def start(self):
        self.detectionWorker = DetectionWorker(
            self.systems
        )
        self.detectionWorker.start()
        assert self.detectionWorker.q_out.get() == "Started"
        self._worker_free = True

    def stop(self):
        self.detectionWorker.stop()

    def set_frame(self, frame):
        self._current_frame = frame

    def tick(self, frame):
        if self._worker_free is True:
            params = [system.get_params() for system in self.systems]
            ons = [self.params.get(system.name).value()
                   for system in self.systems]
            self.detectionWorker.q_in.put((frame, params, ons))
            self._worker_free = False
        if not self.detectionWorker.q_out.empty():
            datas = self.detectionWorker.q_out.get()

            assert len(datas) == len(self.systems)
            for data, system in zip(datas, self.systems):
                system.update_state(data)
            self._worker_free = True

        frame = self.drawer.draw(
            frame,
            self.systems,
        )
        return frame

    def warn_if_needed(self):
        if self.warner is not None:
            in_danger = False
            for s in self.systems:
                in_danger = s.in_danger()
                if in_danger:
                    self.warner.warn(s)
                    break
            if not in_danger:
                self.warner.stop()

    def all_parameterizables(self, asdict=False):
        l = [self.params, self.drawer.params] + \
            [s.params for s in self.systems]
        if not asdict:
            return l
        return {p.__class__.__name__: p for p in l}
