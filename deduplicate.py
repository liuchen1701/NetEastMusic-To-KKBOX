import xml.etree.ElementTree as ET
tree = ET.parse('Liked.kbl')
root = tree.getroot()
playlist = root[0][1][3]
song_set = set()
to_remove = []

print("Number of songs: " + str(len(playlist)))
for song in playlist:
    if song[6].text not in song_set:
        song_set.add(song[6].text)
    else:
        to_remove.append(song)

for item in to_remove:
    playlist.remove(item)

root[0][1][3] = playlist
tree._setroot(root)
tree.write('Liked.kbl')
