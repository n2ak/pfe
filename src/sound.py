
import time
from threading import Thread, Event
import winsound


class Sound:
    def __init__(self, filepath='../Alarm-beeping-sound.wav', flags=winsound.SND_LOOP + winsound.SND_ASYNC, delai=.01) -> None:
        self.filepath = filepath
        self.flags = flags
        self.is_on = False
        self.delai = delai
        self.refresh()

    def refresh(self):
        self.t = Thread(target=self._play, args=(), daemon=True)
        self.e = Event()

    def _play(self):
        winsound.PlaySound(self.filepath, self.flags)

        while True:
            if self.e.is_set():
                winsound.PlaySound(None, winsound.SND_PURGE)
                break
            time.sleep(self.delai)
        print("Stopping sound")

    def start(self):
        if (self.is_on is False) and (self.t.is_alive() is False):
            self.refresh()
            self.t.start()
            self.is_on = True

        # self.t.daemon()

    def stop(self):
        if self.is_on is True:
            self.e.set()
            self.is_on = False
