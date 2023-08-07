
import time
from threading import Thread, Event
import winsound

class Sound:
    def __init__(self, filepath='../Alarm-beeping-sound.wav', flags=winsound.SND_LOOP + winsound.SND_ASYNC) -> None:
        self.e = Event()
        self.t = Thread(target=self._play, args=())
        self.filepath = filepath
        self.flags = flags

    def _play(self):
        winsound.PlaySound(self.filepath,self.flags)
        while True:
            if self.e.is_set():
                winsound.PlaySound(None, winsound.SND_PURGE)
                break
            time.sleep(.5)

    def start(self):
        self.t.start()
        # self.t.daemon()

    def stop(self):
        self.e.set()
class Sound2:
    def __init__(self, filepath='../Alarm-beeping-sound.wav', flags=winsound.SND_LOOP + winsound.SND_ASYNC) -> None:
        self.e = Event()
        self.t = Thread(target=self._play, args=())
        self.filepath = filepath
        self.flags = flags

    def _play(self):
        from pydub import AudioSegment
        from pydub.playback import play

        song = AudioSegment.from_mp3("your_song.mp3")
        louder_song = song + 6
        quieter_song = song - 3
        while True:
            if self.e.is_set():
                break
            play(louder_song)

    def start(self):
        self.t.start()

    def stop(self):
        self.e.set()
