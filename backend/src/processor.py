import typing
from src.adas import ADASystem
from src.warning import Warner
from src.drawer import Drawer
from src.workers import DetectionWorker


class Processor:
    def __init__(
        self,
        systems: typing.List[ADASystem],
        warner: Warner,
        drawer: Drawer,
    ) -> None:
        self.systems = systems
        self.warner = warner
        self.drawer = drawer

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
            params = [system.get_param(ret_types=False).PARAMS
                      for system in self.systems]
            self.detectionWorker.q_in.put((frame, params))
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

    def get_params(self, ret_types=True, include_drawer=False):
        systems = self.systems
        drawer = self.drawer

        params = [system.get_param(ret_types=ret_types)
                  for system in systems]
        if include_drawer:
            params.append(drawer.get_param(ret_types=ret_types))
        if ret_types:
            params = dict(params)
        return params
