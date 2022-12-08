res_width = 1600
res_height = 850
playfield_width = res_width * 0.8
playfield_height = res_height * 0.8
playfield_start = (res_width * 0.1, res_height * 0.1)

maps = []

def pixelConv(pixels, dimension): # Converts osu! pixels (based on 80% of 640 * 480) to real screen pixels, found from here: 
    # https://www.reddit.com/r/osugame/comments/vvua1l/osupixels_to_normal_coordinates/
    if dimension == 'x':
        return pixels * (playfield_width / 512)
    return pixels * (playfield_height / 384)

# Map and object definitions taken from 
# https://osu.ppy.sh/wiki/en/Client/File_formats/Osu_%28file_format%29


class Map():
    def __init__(self, title, artist, creator, version, mapID, setID, HP, CS, OD, AR):
        # HP = HP drain rate, CS = circle size, OD = overall difficulty, AR = approach rate
        # Definitions of these difficulty setting terms can be found at 
        # https://osu.ppy.sh/wiki/en/Client/Beatmap_editor/Song_Setup#difficulty

        self.title = title
        self.artist = artist
        self.creator = creator
        self.version = version
        self.mapID = mapID
        self.setID = setID
        self.background = 'backgrounds/' + title + '.jpg'
        self.song = 'songs/' + title + '.mp3'
        
        self.HP = HP
        self.CS = CS
        self.OD = OD
        self.AR = AR
        self.diffMultiplier = HP + CS + OD + AR
        self.objects = []

        # self.r = 32 * (1 - ((0.7 * (CS - 5)) / 5)) 
        self.r = 109 - (9 * CS) # Found here: https://www.reddit.com/r/osugame/comments/5gd3dm/whats_the_cspixel_formula/
        self.hitWindow300 = 79 - (OD * 6) + 0.5
        self.hitWindow100 = 139 - (OD * 8) + 0.5
        self.hitWindow50 =  199 - (OD * 10) + 0.5
        if AR > 5:
            self.approachTiming = 1200 - ((AR - 5) * 150)
        else:
            self.approachTiming = 1800 - (AR * 120)
        # Most calculations for hit windows, approach rates, and circle radius found here: 
        # https://www.reddit.com/r/osugame/comments/6phntt/difficulty_settings_table_with_all_values/

        self.localScores = []

    def addObjects(self, objectList):
        for object in objectList:
            self.objects.append((object.drawTime, object)) 


class HitObject(Map):
    def __init__(self, map, x, y, time):
        self.map = map
        self.x = pixelConv(x, 'x') + playfield_start[0]
        self.y = pixelConv(y, 'y') + playfield_start[1]
        self.time = time
        self.drawTime = (time - map.approachTiming, time + map.hitWindow50)


class Circle():
    def __init__(self, HitObject):
        self.x = HitObject.x
        self.y = HitObject.y
        self.map = HitObject.map
        self.approachTiming = HitObject.map.approachTiming
        self.drawTime = HitObject.drawTime
        self.time = HitObject.time


class Slider():
    def __init__(self, HitObject, length, slideTime, repeats):
        self.x = HitObject.x
        self.y = HitObject.y
        self.map = HitObject.map
        self.approachTiming = HitObject.map.approachTiming
        self.length = length
        self.slideTime = slideTime
        self.repeats = repeats
        self.time = HitObject.time
        self.totalSlideTime = self.slideTime * (self.repeats + 1)
        self.drawTime = HitObject.drawTime

        self.possibleEnds = {(self.x + self.length, self.y, 'Right'), (self.x, self.y + self.length, 'Down'), 
        (self.x - self.length, self.y, 'Left'), (self.x, self.y - self.length, 'Up')}
        for end in self.possibleEnds:
            if ((end[0] > HitObject.map.r and end[0] < res_width - HitObject.map.r) 
            and (end[1] > HitObject.map.r and end[1] < res_height - HitObject.map.r)):
                self.endX, self.endY = end[0], end[1]
                self.direction = end[2]

