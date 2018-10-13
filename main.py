"""
    Arguments:
    1. Exported playlist file in "TRACK - ARTIST" format, WITH file extension
    2. Name of the new KKBOX playlist
    3. Optional: Start index when loading original playlist, WITHOUT file extension
"""

from kkbox import *
from util import *
import json
import sys

def read_neteast_txt(filename):
    dict = {}

    with open(filename,"r", encoding='utf8') as file:
        for line in file:
            list = line.split(" - ")
            dict[list[0]] = list[-1].strip('\n')

    file.close()
    return dict

def get_track_info(query):
    data = search_track(query)

    if len(data["tracks"]["data"]) is 0:
        return None, None

    track_id = data["tracks"]["data"][0]["id"]
    pathname = get_song_pathname(track_id)

    album_url = data["tracks"]["data"][0]["album"]["images"][0]["url"]
    album_id = extract(extract(album_url, "album", ",", 6, 0), "/", None, 1, 0)
    
    return pathname, album_id

def load_tracks_info(tracks_dict, start_index):
    info_dict = {}
    error_tracks = {}
    for key, value in list(tracks_dict.items())[start_index:]:
        print("Processing song \t" + key + " \tby \t" + value + " . . . ", end='')
        pathname, album_id = get_track_info(key + " " + value)
        if pathname is not None and album_id is not None:
            info_dict[pathname] = album_id
            print("\tSuccess!")
        else:
            error_tracks[key] = value
            print("\ERROR!!!!")

    return info_dict, error_tracks

def generate_error_file(error_tracks, playlist_name):
    print("\n========== FOLLOWING SONGS ARE NOT ADDED =========\n")
    with open(playlist_name + "_error.txt", "w", encoding='utf8') as file:
        for key, value in error_tracks.items():
            print(key + " - " + value)
            file.write(key + " - " + value + "\n")

source_list = sys.argv[1]
kkbox_list = sys.argv[2]

tracks_dict = read_neteast_txt(source_list)
info_dict, error_tracks = load_tracks_info(tracks_dict, 0)
generate_kkbox_playlist(info_dict, kkbox_list)
generate_error_file(error_tracks, kkbox_list)