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


class myPL:

    def __init__(self, string):
        tmp = string.split(" ")
        self.url = tmp[0]
        self.songs = tmp[1]
        self.title = (' '.join(tmp[2:])).strip()

    def __str__(self):
        return self.title + " " + self.songs

class SongPlaceholder:

    def __init__(self, string):
        tmp = string.split(" ")
        self.url = tmp[0]
        self.title = (' '.join(tmp[1:])).strip()

    def __str__(self):
        return self.url + " " + self.title

def read_list(list_file_path):

    file = open(list_file_path, "r")
    lines = file.readlines()
    items = []

    for string in lines:
        string = string.strip()
        if string != "" and string != " ":
            items.append( SongPlaceholder(string) )

    return items

def write_playlist_list(list_file_path, playlist_list): #url title/folder_name

    file = open(list_file_path, "w")
    for pl in playlist_list:
        file.write(pl.url + " " + pl.title + "\n")
    file.close()

def in_items(items, url=None, title=None):

    if url != None:
        for item in items:
            if url == item.url:
                return True
        return False

    elif title!=None:
        for item in items:
            if title == item.title:
                return True
        return False

def dl_audio(video_url, location):
    yt = YouTube(video_url)
    y_audio = yt.streams.get_audio_only()

    filename = y_audio.default_filename
    file_path = location + "/" + filename

    if os.path.isfile(file_path):
        print(filename + " found")
        return ("found", filename)
    else:
        print(filename + " downloaded")
        y_audio.download(location)
        return ("downloaded", filename)

def download_playlist(playlist_url, dump_location=""):

    playlist = Playlist(playlist_url)

    if not playlist or not playlist.title:
        print("Url not valid")
        return None

    p_name = playlist.title
    location = dump_location + p_name

    try:
        os.mkdir(location)
    except OSError as error:
        pass
        # print("directory already exists")

    if not os.path.isfile(location + '/config'):
        config = open(location + '/config', 'w+')
        config.close()

    config = open(location + '/config', 'r')
    old_songs_strings = config.readlines()
    old_songs = []
    for string in old_songs_strings:
        string = string.strip()
        if string != "" and string != " ":
            old_songs.append( SongPlaceholder(string) )


    config.close()
    new_songs_url = []

    songs = {
        "already_synchronized":0,
        "found":0,
        "downloaded":0,
        "deleted": 0
    }


    #check videos removed from playlist
    for song in list(old_songs):
        if not song.url in playlist.video_urls:
            #print("deleting " + str(song))
            songs["deleted"] += 1
            old_songs.remove(song)
            try:
                os.remove(location + "/" + song.title)
            except OSError as error:
                print("file to delete not found")


    for url in playlist.video_urls:

        found = False
        for oldsong in old_songs:
            if url == oldsong.url:
                found = True

        if found: #already synchronized
            songs["already_synchronized"] += 1
        else:
            status, filename = dl_audio(url, location)
            songs[status] += 1
            new_songs_url.append( SongPlaceholder(url + " " + filename))

    config = open(location + '/config', 'w')
    for song in old_songs:
        config.write(str(song) + "\n")
    for song in new_songs_url:
        config.write(str(song) + "\n")
    config.close()

    print("\n# '" + p_name + "' synchronized")
    print(" - already synchronized \t" + str(songs["already_synchronized"]))
    print(" - found \t\t\t" + str(songs["found"]))
    print(" - downloaded \t\t\t" + str(songs["downloaded"]))
    print(" - deleted \t\t\t" + str(songs["deleted"]))
    return p_name


def add_playlist(playlist_url, dump_location=""):

    if not os.path.isfile(dump_location + 'config'):
        config = open(dump_location + 'config', 'w+')
        config.close()

    playlists = read_list(dump_location + 'config')

    if not in_items(playlists, playlist_url):
        config = open(dump_location + 'config', 'a')
        playlist_name = download_playlist(playlist_url)
        if playlist_name:
            config.write(playlist_url + " " + playlist_name + "\n")
            print("Playlist added")
        else:
            print("Playlist not added")
    else:
        print("Playlist already added")


# def get_url_from_yt(query):
#
#     query_url = "https://www.youtube.com/results?search_query=" + query
#
#     driver = webdriver.Firefox()
#     driver.get(query_url)
#     html = driver.page_source
#     soup  = BeautifulSoup(html, features="lxml")
#     driver.quit()
#
#     item = soup.find(id="primary").find_all("ytd-video-renderer", class_="ytd-item-section-renderer")[0]
#     video_url = "https://www.youtube.com/" + item.find("ytd-thumbnail").find("a", id="thumbnail")["href"]
#     return video_url
#
# def add_spotify_playlist(spotify_id, dump_location=""):
#     sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="fe5cb70c31984c1c9b859e79a3a721ce",
#                                                            client_secret="735c5faab0db4b39a43f395487dd8ff5"))
#     #playlist_id = 'spotify:user:spotifycharts:playlist:5qwmXZBJMZAKT0PsxQ5RTD'
#     results = sp.playlist(spotify_id)["tracks"]["items"]
#
#     song = {}
#
#     for r in results:
#         song["title"] = r["track"]["name"]
#         song["main_author"] = r["track"]["album"]["artists"][0]["name"]
#         song["spotify_id"] = r["track"]["id"]
#
#         query = song["title"] + " " + song["main_author"]
#         song["yt_url"] = get_url_from_yt(query)


def remove_playlist(playlist_id, dump_location=""):
    playlists = read_list(dump_location + 'config')
    pl = playlists.pop(playlist_id)

    if os.path.isfile(dump_location + pl.title + "/config"):
        shutil.rmtree(dump_location + pl.title)
        write_playlist_list(dump_location + "config", playlists)
        print("Playlist deleted succesfully at " + dump_location + pl.title + "/")
    else:
        print("config file not found :(")


def sync(dump_location=""):

    playlists = []
    with open(dump_location + 'config', 'r') as config:
        lines = config.readlines()
        playlists = [SongPlaceholder(line.rstrip()) for line in lines]

    print("### " + str(len(playlists)) + " Playlists found ###")

    for playlist in playlists:
        download_playlist(playlist.url)


def about(dump_location=""):
    playlists = read_list(dump_location + 'config')

    print("### " + str(len(playlists)) + " Playlists found ###\n")

    i=1
    for pl in playlists:
        print("# " + '{0:03}'.format(i) + " " + pl.title)
        i+=1

    print("")


def print_help():
    print("Commands:")
    print("\tsync \tsync all the stuff")
    print("\tadd_pl \tadd Playlist")

param = sys.argv[1:]

if param == [] or param == None or param == ["--help"] or param == ["-h"]:
    print_help()

elif param[0] == "sync":
    sync()

elif param[0] == "add_pl":
    if len(param) == 2:
        add_playlist(param[1])
    else:
        print("wrong parameters number")

elif param[0] == "about":
    about()

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
