#!/usr/bin/env python3
# requires `mplayer` to be installed
# v1.0

# https://raspberrytips.nl/internet-radio-luisteren-raspberry-pi/

from time import sleep
import os
import sys
import signal
import shlex
import math

PY3 = sys.version_info[0] >= 3
if not PY3:
    print("Radio only works with python3")
    sys.exit(1)

import subprocess
from subprocess import Popen, PIPE, STDOUT

UPDATE_INTERVAL = 1

STATIONS = [

    {'name': "Retro Radio",
     'source': 'http://stream1.retroradio.hu/mid.mp3.m3u',
     'info': "Retro Radio"},

    {'name': "Petofi Radio",
     'source': 'http://stream001.radio.hu:8080/mr2.mp3.m3u',
     'info': 'Petofi Radio'},

    {'name': "Balaton Radio",
     'source': 'http://wssgd.gdsinfo.com:8200/listen.pls',
     'info': 'Balaton Radio'},

    {'name': "Radio Most \nKaposvar",
     'source': 'http://stream.radiomost.hu:8200/live.mp3',
     'info': 'Radio Most'},

    {'name': "Slager FM",
     'source': 'http://92.61.114.159:7812/slagerfm64.mp3',
     'info': 'Slager FM'}

]

class Radio(object):
    def __init__(self, lcd, start_station=0):
        self.current_station_index = start_station
        self.playing_process = None
        
        self.lcd = lcd

    @property
    def current_station(self):
        """Returns the current station dict."""
        return STATIONS[self.current_station_index]

    @property
    def playing(self):
        return self._is_playing

    @playing.setter
    def playing(self, should_play):
        if should_play:
            self.play()
        else:
            self.stop()

    @property
    def text_status(self):
        """Returns a text represenation of the playing status."""
        if self.playing:
            return "Now Playing"
        else:
            return "Stopped"

    def play(self):
        """Plays the current radio station."""
        print("Playing {}.".format(self.current_station['name']))
        if self.current_station['source'].split("?")[0][-3:] in ['m3u', 'pls']:
            play_command = "mplayer -quiet -playlist {stationsource}".format(
		        stationsource=self.current_station['source'])
        else:
            play_command = "mplayer -quiet {stationsource}".format(
                stationsource=self.current_station['source'])
        self.playing_process = subprocess.Popen(
            play_command,
            shell=True,
            preexec_fn=os.setsid)
        self._is_playing = True
        self.update_display()

    def stop(self):
        """Stops the current radio station."""
        print("Stopping radio.")
        os.killpg(self.playing_process.pid, signal.SIGTERM)
        self._is_playing = False

    def change_station(self, new_station_index):
        """Change the station index."""
        was_playing = self.playing
        if was_playing:
            self.stop()
        self.current_station_index = new_station_index % len(STATIONS)
        if was_playing:
            self.play()

    def next_station(self, event=None):
        self.change_station(self.current_station_index + 1)

    def previous_station(self, event=None):
        self.change_station(self.current_station_index - 1)

    def update_display(self):
        self.update_station()

    def update_station(self):
        """Updates the station status."""
        message = self.current_station['name']
        self.lcd.clear()
        self.lcd.message = message

    def toggle_playing(self, event=None):
        if self.playing:
            self.stop()
            self.lcd.clear()
            self.lcd.message = "Pauze"
        else:
            self.play()

    def close(self):
        self.stop()
        self.lcd.clear()

if __name__ == "__main__":
    try:
        subprocess.call(["mplayer"], stdout=open('/dev/null'))
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print(
                "MPlayer was not found, install with "
                "`sudo apt-get install mplayer`")
            sys.exit(1)
        else:
            raise
