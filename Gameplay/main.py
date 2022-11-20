from cmu_112_graphics import *
from importing import *
import pygame



# Settings

res_width = 2560
res_height = 1440
effects_vol = 1
music_vol = 1
master_vol = 1


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


class HitObject(Map):
    def __init__(self, x, y, r, hitWindow300, hitWindow100, hitWindow50, hitTime, approachTiming, type, objectParams):
        super().init(r, hitWindow300, hitWindow100, hitWindow50, approachTiming)
        self.x = x
        self.y = y
        self.hitTime = hitTime
        self.hit300 = (hitTime - hitWindow300, hitTime + hitWindow300)
        self.hit100 = (hitTime - hitWindow100, hitTime + hitWindow100)
        self.hit50 = (hitTime - hitWindow50, hitTime + hitWindow50)
        self.appearTime = hitTime - approachTiming
        self.disappearTime = hitTime + approachTiming
        self.type = type
        self.objectParams = objectParams
        self.bounds = (x - r, y - r, x + r, y + r)

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

    # Loops = number of times to loop the sound.
    # If loops = 1 or 1, play it once.
    # If loops > 1, play it loops + 1 times.
    # If loops = -1, loop forever.
    def start(self, loops=1):
        self.loops = loops
        pygame.mixer.music.play(loops=loops)

    # Stops the current sound from playing
    def stop(self):
        pygame.mixer.music.stop()


def appStarted(app):
    # map = Map() from importing

    pygame.mixer.pre_init(44100, -16, 1, 512) 
    # Used to remove sound delay, especially with histounds, taken from https://stackoverflow.com/questions/18273722/pygame-sound-delay 
    pygame.mixer.init()
    app.sound = pygame.mixer.Sound("audio/hitsound.wav")
    app.music = Sound("audio/Tokyo's Starlight.mp3")
    app.music.start(1)

    app.cx = app.width / 2
    app.cy = app.height / 2
    app.timePassed = 0

def drawHitObject(app, canvas, hitObject):
    if object.type == 1:
        drawCircle(app, canvas, hitObject)
    elif object.type == 2:
        drawSlider(app, canvas, hitObject)
    else:
        drawSpinner(app, canvas, hitObject)

def drawApproachCircle(app, canvas, hitObject):
    canvas.create_oval(hitObject.bounds[0], hitObject.bounds[1], hitObject.bounds[2], hitObject.bounds[3])


def drawCircle(app, canvas, hitObject):
    canvas.create_oval(hitObject.bounds[0], hitObject.bounds[1], hitObject.bounds[2], hitObject.bounds[3])


def drawSlider(app, canvas, hitObject):
    return 42

def drawSpinner(app, canvas, hitObject):
    return 42

def drawCursor(app, canvas):
    return 42
    
def mousePos(app, event):
    return event.x, event.y

def appStopped(app):
    app.sound.stop()
    app.music.stop()

def keyPressed(app, event):
    if ((event.key in ('a', 's', 'A', 'S')) and 
    (mousePos(app, event) >= (250, 50) and mousePos(app, event) <= (350, 150))):
        pygame.mixer.Sound.play(app.sound)

def timerFired(app):
    app.timePassed += 1

def redrawAll(app, canvas):
    canvas.create_oval(250, 50, 350, 150, fill='blue')

runApp(width=res_width, height=res_height) 