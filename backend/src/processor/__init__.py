from typing import List, Union
from src.adas import ADASystem
from src.warner import Warner
from src.drawer import Drawer
from src.workers import DetectionWorker
from .processor_params import ProcessorParams
from src.base.parameterizable import Parameterizable
from src.base.params import ParamsBase


class Processor(Parameterizable):
    def __init__(
        self,
        systems: List[ADASystem],
        warner: Warner,
        drawer: Drawer,
        systems_on=False
    ) -> None:
        super().__init__("processor")
        self.systems = systems
        self.warner = warner
        self.drawer = drawer
        self.params = ProcessorParams(systems, systems_on)
        self.params.print()

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
            params = [system.get_param(ret_type=False).PARAMS
                      for system in self.systems]
            ons = [self.params.get_porperty(system.name)
                   for system in self.systems]
            self.detectionWorker.q_in.put((frame, params, ons))
            self._worker_free = False
        if not self.detectionWorker.q_out.empty():
            datas = self.detectionWorker.q_out.get()

            assert len(datas) == len(self.systems)
            warning_source = None
            for data, system in zip(datas, self.systems):
                system.update_state(data)
                if (warning_source is None) and (not system.is_safe()):
                    warning_source = system
            if warning_source is not None:
                self.warner.warn(warning_source)
            else:
                self.warner.stop()
            self._worker_free = True

        frame = self.drawer.draw(
            frame,
            self.systems,
        )
        return frame

    def get_params(self, ret_types=True, include_drawer=False) -> Union[list[ParamsBase], dict[str, list[ParamsBase]]]:
        systems = self.systems
        drawer = self.drawer

        entities: List[Parameterizable] = [self, *systems, self.warner]

        if include_drawer:
            entities.append(drawer)
        params = [e.get_param(ret_type=ret_types) for e in entities]
        if ret_types:
            params = dict(params)
        return params

    # def _update(self):
