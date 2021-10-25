from pytube import YouTube
from pytube import Playlist
import os
import sys
import shutil

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

from cmanager import Cmanager



def dl_audio(video_url, location):
    yt = YouTube(video_url)
    y_audio = yt.streams.get_audio_only()

    minutes = int(yt.length/60)
    seconds = int(yt.length%60)

    filename = y_audio.default_filename
    file_path = location + "/" + filename

    if os.path.isfile(file_path):
        print("# " + filename + " [found]")
        return ("found", filename, minutes, seconds)
    else:
        print("# " + filename + " [downloaded]")
        y_audio.download(location)
        return ("downloaded", filename, minutes, seconds)


def dl_audio_list(pl, video_url_list, folder):

    to_del = pl.remove_deleted(video_url_list)
    for filename in to_del:
        print(filename)
        try:
            os.remove(folder + "/" + filename)
        except OSError as error:
            print("file to delete not found")

    for url in video_url_list:
        if pl.has_song(url):
            pass
        else:
            status, filename, minutes, seconds = dl_audio(url, folder)
            pl.add_song(url, filename, minutes, seconds)


def add_playlist(playlist_url):

    if cmanager.get_pl(playlist_url) == None:
        if True: #yt
            playlist = Playlist(playlist_url)

            if not playlist or not playlist.title:
                print("Url not valid")
                return None

            p_name = playlist.title
            yt_url_list = playlist.video_urls
        else: #sp
            pass

        aa = cmanager.add_pl(playlist_url, p_name)

        folder = DUMP_LOCATION + p_name

        if not os.path.isdir(folder):
            os.mkdir(folder)

        print("\n# '" + p_name)
        dl_audio_list(aa, yt_url_list, folder)
        aa.print_synch_info()

    else:
        print("Playlist already added")


def remove_playlist(playlist_id):

    pl = cmanager.remove_pl(playlist_id)

    if os.path.isfile(DUMP_LOCATION + pl.title):
        shutil.rmtree(DUMP_LOCATION + pl.title)

    print(pl.title + " removed")


def print_help():
    print("Commands:")
    print("\tsync \tsync all the stuff")
    print("\tadd_pl \tadd Playlist")
    print("\--status \tadd Show all")
    print("\--list \tadd List the playlists addded")



DUMP_LOCATION = ""

param = sys.argv[1:]
cmanager = Cmanager("config")

if not os.path.isfile("" + 'config'):
    config = open("" + 'config', 'w+')
    config.close()

if param == [] or param == None or param == ["--help"] or param == ["-h"]:
    print_help()

elif param[0] == "add_pl":
    if len(param) == 2:
        add_playlist(param[1])
    else:
        print("wrong parameters number")

elif param[0] == "--list":
    print(cmanager.playlists_list())

elif param[0] == "--status":
    print(cmanager)

elif param[0] == "rm_pl":
    if len(param) == 2:
        remove_playlist(int(param[1]) -1)
    else:
        print("wrong parameters number")

elif param[0] == "add_spotify_pl":
    if len(param) == 2:
        add_spotify_playlist(param[1])
    else:
        print("wrong parameters number")

else:
    print("Parameters not catched")


cmanager.write_back()
