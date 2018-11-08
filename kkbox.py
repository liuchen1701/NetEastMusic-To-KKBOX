from kkbox_developer_sdk.auth_flow import KKBOXOAuth
from kkbox_developer_sdk.api import KKBOXAPI
import requests
from util import *
import datetime
import time
import opencc
import collections

CLIENT_ID = "1bbdaf0fedef363ed64fb500a1964f55"
CLIENT_SECRET = "711691aac37e0a7013b1a689bfa9f407"

PATHNAME_KEYWORD = "al:windows_universal:url"
PATHNAME_OFFSET = 53
ALBUM_URL_KEYWORD = "music:album"
ALBUM_URL_OFFSET = 22

KKBOX_VER = "10.5.32"
PACKAGE_VER = "1.1"

auth, token, kkboxapi = None, None, None
playlist = None
cc = opencc.OpenCC('s2t')

def init():
    global auth, token, kkboxapi
    auth = KKBOXOAuth(CLIENT_ID, CLIENT_SECRET)
    token = auth.fetch_access_token_by_client_credentials()
    kkboxapi = KKBOXAPI(token)

def search(query):
    try:
        results = kkboxapi.search_fetcher.search(query, ["track"], 'HK')
    except Exception as e:
        time.sleep(5)
        try:
            results = kkboxapi.search_fetcher.search(query, ["track"], 'HK')
        except Exception as ex:
            results = None
    return results

def match_score(str1, str2):
    map1 = collections.Counter(str1.upper())
    map2 = collections.Counter(str2.upper())
    count = 0
    for key in map1.keys():
        count += min(map1[key], map2.get(key, 0))
    return count

def get_best_track(results, title=None, artist=None, album=None):
    track = None
    highest_score = 0
    if title is None and artist is None and album is None:
        if results is not None and len(results["tracks"]["data"]) is not 0:
            for data in results["tracks"]["data"]:
                if len(data["available_territories"]) is not 0 and "HK" in data["available_territories"]:
                    track = results["tracks"]["data"][0]
                    break
    else:
        if results is not None:
            title_t, artist_t, album_t = None, None, None
            if title is not None:
                title_t = cc.convert(title)
            if artist is not None:
                artist_t = cc.convert(artist)
            if album is not None:
                album_t = cc.convert(album)

            for data in results["tracks"]["data"]:
                if len(data["available_territories"]) is not 0 and "HK" in data["available_territories"]:
                    score = 0
                    if title_t is not None:
                        score += match_score(title_t, data["name"])
                    if artist_t is not None:
                        score += match_score(artist_t, data["album"]["artist"]["name"])
                    if album_t is not None:
                        score += match_score(album_t, data["album"]["name"])
                    if score > highest_score:
                        highest_score = score
                        track = data
    return track, highest_score

def search_track(title, artist, album):
    global kkboxapi, cc
    if kkboxapi is None:
        init()
    
    results = None
    candidates = []

    # Full query search
    # print("Searching: " + title + " " + artist + " " + album)
    results = search(title + " " + artist + " " + album)
    candidates.append(get_best_track(results, title, artist, album))

    # For cases when artist is mis-labelled in either side
    # print("Searching: " + title + " " + album)
    results = search(title + " " + album)
    candidates.append(get_best_track(results, title, album))

    # Search for same song, same artist but different album version
    # print("Searching: " + title + " " + artist)
    results = search(title + " " + artist)
    candidates.append(get_best_track(results , title, artist))

    for index, candidate in enumerate(candidates):
        if candidate[0] is not None:
            candidate += (match_score(cc.convert(title), candidate[0]["name"]) / float(len(candidate[0]["name"])),)
        else:
            candidate += (0 ,)
        candidates[index] = candidate

    candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
    candidates = sorted(candidates, key=lambda x: x[2], reverse=True)
    
    # for candidate in candidates:
    #     print(str(candidate[1]) + " " + str(candidate[2]))

    if len(candidates) is not 0 and candidates[0][0] is not None:
        return candidates[0][0]
    else:
        return get_best_track(search(title), title)[0]

def get_song_pathname(id):
    url = "https://event.kkbox.com/content/song/" + id
    url = requests.get(url).url
    url = url.replace("tw/en", "hk/tc")

    response = requests.get(url).text

    return extract(response, PATHNAME_KEYWORD, "\"", PATHNAME_OFFSET, 0)

def init_kkbox_playlist(playlist_name):
    global playlist
    playlist = open(playlist_name + ".kbl", "w", encoding='utf8')
    prefix = "<utf-8_data><kkbox_package><kkbox_ver>" + \
            KKBOX_VER + \
            "</kkbox_ver><playlist><playlist_id>1</playlist_id><playlist_name>" + \
            playlist_name + \
            "</playlist_name><playlist_descr /><playlist_data>"
    
    playlist.write(prefix + "\n")
    playlist.close()

def append_to_playlist(pathname, album_id, playlist_name="new_playlist"):
    global playlist
    if playlist is None:
        init_kkbox_playlist(playlist_name)
    
    if playlist.closed:
        playlist = open(playlist_name + ".kbl", "a", encoding='utf8')

    info = "<song_data>\n<song_name></song_name>\n<song_artist></song_artist>\n<song_album></song_album>\n<song_genre></song_genre>\n<song_preference></song_preference>\n<song_playcnt></song_playcnt>\n<song_pathname>" + \
        pathname + \
        "</song_pathname>\n<song_type></song_type>\n<song_lyricsexist></song_lyricsexist>\n<song_artist_id></song_artist_id>\n<song_album_id>" + \
        album_id + \
        "</song_album_id>\n<song_song_idx></song_song_idx>\n</song_data>"
    playlist.write(info)
    playlist.flush()

def finish_kkbox_playlist(info_dict, playlist_name):
    global playlist
    if playlist is None:
        init_kkbox_playlist(playlist_name)
    
    if playlist.closed:
        playlist = open(playlist_name + ".kbl", "a", encoding='utf8')

    surfix = "</playlist_data></playlist><package><ver>" + \
            PACKAGE_VER + \
            "</ver><descr /><packdate>" + \
            datetime.datetime.now().strftime("%Y%m%d%H%M") + \
            "</packdate><playlistcnt>1</playlistcnt><songcnt>" + \
            str(len(info_dict)) + \
            "</songcnt></package></kkbox_package></utf-8_data>"
    
    playlist.write(surfix)
    playlist.close()

# print(search_track("红(Live)", "张国荣", "张国荣跨越97演唱会"))