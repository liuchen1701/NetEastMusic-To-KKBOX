from kkbox_developer_sdk.auth_flow import KKBOXOAuth
from kkbox_developer_sdk.api import KKBOXAPI
import requests
from util import *
import datetime

CLIENT_ID = ""
CLIENT_SECRET = ""

PATHNAME_KEYWORD = "al:windows_universal:url"
PATHNAME_OFFSET = 53
ALBUM_URL_KEYWORD = "music:album"
ALBUM_URL_OFFSET = 22

KKBOX_VER = "10.5.32"
PACKAGE_VER = "1.1"

auth, token, kkboxapi = None, None, None

def init():
    global auth, token, kkboxapi
    auth = KKBOXOAuth(CLIENT_ID, CLIENT_SECRET)
    token = auth.fetch_access_token_by_client_credentials()
    kkboxapi = KKBOXAPI(token)

def search_track(name):
    global kkboxapi
    if kkboxapi is None:
        init()
    
    return kkboxapi.search_fetcher.search(name, ["track"], 'HK')

def get_song_pathname(id):
    url = "https://event.kkbox.com/content/song/" + id
    url = requests.get(url).url
    url = url.replace("tw/en", "hk/tc")

    response = requests.get(url).text

    return extract(response, PATHNAME_KEYWORD, "\"", PATHNAME_OFFSET, 0)

def generate_kkbox_playlist(info_dict, name):
    with open(name + ".kbl", "w", encoding='utf8') as file:
        prefix = "<utf-8_data><kkbox_package><kkbox_ver>" + \
                 KKBOX_VER + \
                 "</kkbox_ver><playlist><playlist_id>3</playlist_id><playlist_name>" + \
                 name + \
                 "</playlist_name><playlist_descr /><playlist_data>"
        
        surfix = "</playlist_data></playlist><package><ver>" + \
                 PACKAGE_VER + \
                 "</ver><descr /><packdate>" + \
                 datetime.datetime.now().strftime("%Y%m%d%H%M") + \
                 "</packdate><playlistcnt>1</playlistcnt><songcnt>" + \
                 str(len(info_dict)) + \
                 "</songcnt></package></kkbox_package></utf-8_data>"

        file.write(prefix + "\n")

        for pathname, album_id in info_dict.items():
            info = "<song_data>\n<song_name></song_name>\n<song_artist></song_artist>\n<song_album></song_album>\n<song_genre></song_genre>\n<song_preference></song_preference>\n<song_playcnt></song_playcnt>\n<song_pathname>" + \
                   pathname + \
                   "</song_pathname>\n<song_type></song_type>\n<song_lyricsexist></song_lyricsexist>\n<song_artist_id></song_artist_id>\n<song_album_id>" + \
                   album_id + \
                   "</song_album_id>\n<song_song_idx></song_song_idx>\n</song_data>"
            file.write(info)

        file.write(surfix)