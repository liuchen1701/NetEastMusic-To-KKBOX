import json
import sys

with open(sys.argv[1],"r", encoding='utf8') as source:
    with open(sys.argv[2],"a", encoding='utf8') as target:
        for line in source:
            line = line[1:].replace("\"\"", "\"")
            if line[-1] == "\n":
                line = line[:-1]
            while line[-1] == "\"":
                line = line[:-1]
            dict = json.loads(line)

            album = dict["album"]["name"]

            artists = dict["artists"]
            artist = ""
            for info in artists:
                artist += info["name"] + " "
            artist = artist.strip().replace(";", " ")

            title = dict["name"]

            target.write(title + " - " + artist + " - " + album + "\n")