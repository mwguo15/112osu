from cmu_112_graphics import *
from importing import *
import math
import pygame




# Settings

res_width = 1920
res_height = 1080
effects_vol = 1
music_vol = 1
master_vol = 1
cursor_size = 1
skin = 0
universal_offset = 10
maps = []


# Map and object definitions taken from 
# https://osu.ppy.sh/wiki/en/Client/File_formats/Osu_%28file_format%29


class Map():
    def __init__(self, title, artist, song, creator, mapID, setID, background, HP, CS, OD, AR, starRating):
        # HP = HP drain rate, CS = circle size, OD = overall difficulty, AR = approach rate
        # Definitions of these difficulty setting terms can be found at 
        # https://osu.ppy.sh/wiki/en/Client/Beatmap_editor/Song_Setup#difficulty

        self.title = title
        self.artist = artist
        self.song = song
        self.creator = creator
        self.mapID = mapID
        self.setID = setID
        self.background = background
        self.HP = HP
        self.CS = CS
        self.OD = OD
        self.AR = AR
        self.starRating = starRating
        self.objects = dict()

        self.r = 32 * (1 - ((0.7 * (CS - 5)) / 5)) 
        self.hitWindow300 = 79 - (OD * 6) + 0.5
        self.hitWindow100 = 139 - (OD * 8) + 0.5
        self.hitWindow50 =  199 - (OD * 10) + 0.5
        if AR > 5:
            self.approachTiming = 1200 - ((AR - 5) * 150)
        else:
            self.approachTiming = 1800 - (AR * 120)
        # All calculations for hit windows, approach rates, and circle radius found here 
        # https://www.reddit.com/r/osugame/comments/6phntt/difficulty_settings_table_with_all_values/

    def addObject(self, object):
        self.objects[object.drawTime] = object

class HitObject(Map):
    def __init__(self, map, x, y, hitTime, type, objectParams):
        self.map = map
        self.x = x
        self.y = y
        self.hitTime = hitTime
        self.hit300 = (hitTime - map.hitWindow300, hitTime + map.hitWindow300)
        self.hit100 = (hitTime - map.hitWindow100, hitTime + map.hitWindow100)
        self.hit50 = (hitTime - map.hitWindow50, hitTime + map.hitWindow50)
        self.drawTime = (hitTime - map.approachTiming, hitTime + map.approachTiming)
        self.type = type
        self.objectParams = objectParams
        # self.bounds = (x - map.r, y - map.r, x + map.r, y + map.r)
        # self.approachBounds = (x - 1.5*map.r, y - 1.5*map.r, x + 1.5*map.r, y + 1.5*map.r)

class Circle(HitObject):
    def __init__(self, x, y, hitTime, skin):
        super().init(x, y, hitTime)
        self.skin = skin

class Slider(HitObject):
    def __init__(self, x, y, objectParams, hitTime, skin):
        super().init(x, y, hitTime, objectParams)
        self.skin = skin

class Sound(object): # Taken from Animations Part 4 on the CS-112 website
    def __init__(self, path):
        self.path = path
        self.loops = 1
        pygame.mixer.music.load(path)

    # Loops = number of times to loop the sound.        app.currentObjects.pop[0]

    # If loops = 1 or 1, play it once.
    # If loops > 1, play it loops + 1 times.
    # If loops = -1, loop forever.
    def start(self, loops=1):
        self.loops = loops
        pygame.mixer.music.play(loops=loops)

    # Stops the current sound from playing
    def stop(self):
        pygame.mixer.music.stop()


def imgScale(img, base):
    width = img.size[0]
    scale = base / width
    return scale

def appStarted(app):
    # map = Map() from importing
    pygame.mixer.pre_init(44100, -16, 1, 512) 
    # Used to remove sound delay, especially with histounds, taken from https://stackoverflow.com/questions/18273722/pygame-sound-delay 
    pygame.mixer.init()
    app.sound = pygame.mixer.Sound("audio/drum-hitnormal.wav")
    app.music = Sound("audio/audio.mp3")
    app.music.start(1)

    app.map1 = Map('pizza', 'pizza', 'pizza', 'pizza', 1, 1, 'pizza', 10, 4, 10, 10, 5)
    app.circle1 = HitObject(app.map1, app.width / 2, app.height / 2, 1500, 1, None)
    app.map1.addObject(app.circle1)

    app.currentObjects = []
    app.currentApproach = []

    app.cx = app.width / 2
    app.cy = app.height / 2
    app.cursorX = 0
    app.cursorY = 0
    app.timePassed = 0
    app.timerDelay = 1

    # For approach circle drawing
    appearTime = app.map1.approachTiming * 2
    sizeChange = 2 * app.map1.r
    sizeDecrements = (sizeChange / appearTime) * app.timerDelay

    app.circleRaw = app.loadImage("skins/current/hitcircleoverlay.png")
    app.approachRaw = app.loadImage("skins/current/approachcircle.png")
    app.cursorRaw = app.loadImage("skins/current/cursor.png")
    app.bgRaw = app.loadImage("meikaruza.jpg")

    app.circle = app.scaleImage(app.circleRaw, imgScale(app.circleRaw, 3 * app.map1.r))
    app.approach = app.scaleImage(app.approachRaw, 3 * imgScale(app.circleRaw, 3 * app.map1.r))
    app.cursor = app.scaleImage(app.cursorRaw, cursor_size)
    app.bg = app.scaleImage(app.bgRaw, imgScale(app.bgRaw, res_width))
    

def drawHitObject(app, canvas):
    if len(app.currentObjects) > 0: # Prevents out of index error for when there are no objects yet
        for hitObject in app.currentObjects:
            if hitObject.type == 1:
                drawCircle(app, canvas)
            elif hitObject.type == 2:
                drawSlider(app, canvas)
            else:
                drawSpinner(app, canvas)
            

# def drawApproach(app, canvas, hitObject):
#     appearTime = hitObject.approachTiming * 2
#     sizeChange = 2 * hitObject.r
#     sizeDecrements = (sizeChange / appearTime) * app.timerDelay
#     canvas.create_image(hitObject.x, hitObject.y, image = ImageTk.PhotoImage(app.approach))


def drawCircle(app, canvas):
    current = app.currentObjects[0]
    canvas.create_image(current.x, current.y, image = ImageTk.PhotoImage(app.circle))

def drawSlider(app, canvas, hitObject):
    return 42

def drawSpinner(app, canvas, hitObject):
    return 42

def drawCursor(app, canvas):
    canvas.create_image(app.cursorX, app.cursorY, image = ImageTk.PhotoImage(app.cursor))

def drawBackground(app, canvas):
    canvas.create_image(app.width / 2, app.height / 2, image = ImageTk.PhotoImage(app.bg))

    
def mouseMoved(app, event):
    app.cursorX, app.cursorY = event.x, event.y

def appStopped(app):
    app.sound.stop()
    app.music.stop()

def keyPressed(app, event):
    [objcx, objcy] = [app.currentObjects[0].x, app.currentObjects[0].y]
    dist = math.dist([objcx, objcy], [app.cursorX, app.cursorY])
    
    if ((event.key in ('a', 's', 'A', 'S')) and dist < app.map1.r):
        pygame.mixer.Sound.play(app.sound)
        app.currentObjects.pop[0]
        app.currentApproach.pop[0]

def timerFired(app):
    app.timePassed += 1
    if (app.timePassed + universal_offset) in app.map1.objects:
        app.currentObjects.append(app.map1.objects[app.timePassed + universal_offset])
        app.currentApproach.append(app.map1.objects[app.timePassed + universal_offset])
    if (app.timePassed - 2 * app.map1.approachTiming + universal_offset) in app.map1.objects:
        app.currentObjects.pop[0]
        app.currentApproach.pop[0]

def redrawAll(app, canvas):
    drawBackground(app, canvas)
    drawCursor(app, canvas)


runApp(width=res_width, height=res_height) 