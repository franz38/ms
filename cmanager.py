from datetime import time, datetime

class Duration:

    def __init__(self, hh=0, mm=0, ss=0):
        self.hh = hh
        self.mm = mm
        self.ss = ss

    def add(self, o):
        self.ss += o.ss
        self.mm += o.mm
        self.hh += o.hh

        while(self.ss >= 60):
            self.ss -= 60

        while(self.mm >= 60):
            self.mm -= 60

    def __str__(self):
        return str(self.mm) + ":" + "{:02d}".format(self.ss)


class Song:

    def __init__(self, url, title, minutes, seconds):
        self.url = url
        self.title = title
        self.duration = Duration(0, int(minutes), int(seconds))

    def get_config_string(self):
        return self.url + " " + str(self.duration) + " " + self.title + "\n"

    def __str__(self):
        return "- " + str(self.duration) + " min\t" + self.title + " " + "\n"


class Pl:

    songs = {}
    prev_amount = 0
    added = 0
    removed = 0


    def __init__(self, url, title):
        self.url = url
        self.title = title
        self.songs = {}

    def add_song(self, url, title, minutes, seconds, from_file=False):
        if not from_file:
            self.added += 1
        else:
            self.prev_amount += 1
        self.songs[url] = Song(url, title, minutes, seconds)

    def get_config_string(self):
        tmp = "#& " + self.url + " " + self.title + "\n"

        for key in self.songs:
            tmp += self.songs[key].get_config_string()
        return tmp

    def has_song(self, song_url):
        return song_url in self.songs

    def __get_duration(self):
        tmp = Duration(0,0,0)
        for key in self.songs:
            tmp.add(self.songs[key].duration)
        return tmp

    def delete_song_list(self, url_list):
        for url in url_list:
            del self.songs[url]
        removed += len(url_list)

    def remove_deleted(self, new_url_list):
        to_delete = []
        filenames_to_del = []
        for key in self.songs:
            found = False
            for url in new_url_list:
                if key == url:
                    found = True
            if not found:
                to_delete.append(self.songs[key])


        for song in to_delete:
            filenames_to_del.append(song.title)
            del song

        return filenames_to_del

    def print_synch_info(self):
        print(" - previus amount \t\t\t" + str( self.prev_amount ))
        print(" - added \t\t\t" + str( self.added ))
        print(" - deleted \t\t\t" + str( self.removed ))
        print(" - amount \t\t\t" + str( len(self.songs) ))

    def __str__(self):
        tmp = "\n"
        tmp += "# " + self.title + "\n"
        tmp += "# " + str(len(self.songs)) + " songs for a total of " + str(self.__get_duration()) + " minutes" + "\n"
        for key in self.songs:
            tmp += self.songs[key].__str__()
        return tmp

    def get_info(self):
        return self.title + " " + str(len(self.songs)) + " songs for a total of " + str(self.__get_duration()) + " minutes"



class Cmanager:

    cfile_path = None
    playlists = []

    def __init__(self, cfile_path):
        self.cfile_path = cfile_path
        cfile = open(cfile_path, "r")
        lines = cfile.readlines()

        pl = None
        for string in lines:
            string = string.strip()
            if string != "" and string != " ":

                tmp = string.split(" ")
                if tmp[0] == "#&":
                    url = tmp[1]
                    title = ' '.join(tmp[2:])
                    pl = self.add_pl(url, title)

                else:
                    url = tmp[0]
                    title = ' '.join(tmp[2:])
                    duration = tmp[1]
                    min = tmp[1].split(":")[0]
                    sec = tmp[1].split(":")[1]
                    pl.add_song( url, title, min, sec, True )

        cfile.close()
        #self.p()

    def get_pl(self, pl_url):
        for pl in self.playlists:
            if pl.url == pl_url:
                return pl
        return None

    def add_pl(self, url, title):
        pl = Pl(url, title)
        self.playlists.append(pl)
        return pl

    def remove_pl(self, id):
        return self.playlists.pop(id)

    def write_back(self):
        cfile = open(self.cfile_path, "w")
        for key in self.playlists:
            cfile.write( key.get_config_string() )
        cfile.close()

    def __str__(self):
        tmp = ""
        for key in self.playlists:
            tmp += str(key)
        return tmp

    def playlists_list(self):
        tmp = ""
        i = 0
        for key in self.playlists:
            i +=1
            tmp += "[" + str(i) + "] " + key.get_info() + "\n"
        return tmp

    def p(self):
        print(str(len(self.playlists)) + " playlist")
        for key in self.playlists:
            print(key)
