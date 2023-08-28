
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
        self.t = Thread(target=self._play, args=())
        self.e = Event()

    def _play(self):
        winsound.PlaySound(self.filepath, self.flags)

        while True:
            if self.e.is_set():
                winsound.PlaySound(None, winsound.SND_PURGE)
                break
            time.sleep(self.delai)

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


# class Sound2:
#     def __init__(self, filepath='../Alarm-beeping-sound.wav', flags=winsound.SND_LOOP + winsound.SND_ASYNC) -> None:
#         self.e = Event()
#         self.t = Thread(target=self._play, args=())
#         self.filepath = filepath
#         self.flags = flags

#     def _play(self):
#         from pydub import AudioSegment
#         from pydub.playback import play

#         song = AudioSegment.from_mp3("your_song.mp3")
#         louder_song = song + 6
#         quieter_song = song - 3
#         while True:
#             if self.e.is_set():
#                 break
#             play(louder_song)

#     def start(self):
#         self.t.start()

#     def stop(self):
#         self.e.set()
