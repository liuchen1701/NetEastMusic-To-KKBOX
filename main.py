"""
    Arguments:
    1. Exported playlist file in "TRACK - ARTIST" format, WITH file extension
    2. Name of the new KKBOX playlist
    3. Optional: Start index when loading original playlist, WITHOUT file extension
"""

from kkbox import *
from util import *
import sys
from colorama import init

def read_neteast_txt(filename):
    tracks = []

    with open(filename,"r", encoding='utf8') as file:
        for line in file:
            track = line.split(" - ")
            track[-1] = track[-1].strip('\n')
            tracks.append(track)

    file.close()
    return tracks

def get_track_info(title, artist, album):
    data = search_track(title, artist, album)

    if data is None:
        return None, None

    track_id = data["id"]
    pathname = get_song_pathname(track_id)

    album_url = data["album"]["images"][0]["url"]
    album_id = extract(extract(album_url, "album", ",", 6, 0), "/", None, 1, 0)
    
    return pathname, album_id

def load_tracks_info(tracks, start_index, playlist_name):
    info_dict = {}
    error_tracks = []
    index = 1
    for track in tracks[start_index:]:
        title = track[0].replace("(", "").replace(")", "")
        # if title.find(" - ") != -1:
        #     title = title[:title.find(" - ")]
        artist = track[-2].replace("/", " ")
        album = track[-1]

        print("#" + str(index) + " \tProcessing \t" + title + " - " + artist + " - " + album, end='')
        pathname, album_id = get_track_info(title, artist, album)
        if pathname is not None and album_id is not None:
            info_dict[pathname] = album_id
            print("\t\033[92mSuccess\033[0m")
            append_to_playlist(pathname, album_id, playlist_name)
        else:
            print(pathname)
            print(album_id)
            error_tracks.append("#" + str(index) + " - " + title + " - " + artist + " - " + album)
            print("\t\033[91mERROR\033[0m")

        index += 1

    return info_dict, error_tracks

def generate_error_file(error_tracks, playlist_name):
    if len(error_tracks) == 0:
        return
    print("\n========== FOLLOWING SONGS ARE NOT ADDED =========\n")
    with open(playlist_name + "_error.txt", "w", encoding='utf8') as file:
        for track in error_tracks:
            print(track)
            file.write(track + "\n")

init()

source_list = sys.argv[1]
kkbox_list = sys.argv[2]

init_kkbox_playlist(kkbox_list)

tracks = read_neteast_txt(source_list)
info_dict, error_tracks = load_tracks_info(tracks, 0, kkbox_list)

finish_kkbox_playlist(info_dict, kkbox_list)

generate_error_file(error_tracks, kkbox_list)