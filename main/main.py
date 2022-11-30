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
skin = dict()
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
        self.diffMultiplier = HP + CS + OD + AR
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

        self.localScores = []

    def addObject(self, object):
        self.objects[object.drawTime] = object

class HitObject(Map):
    def __init__(self, map, x, y, time, type, objectParams):
        self.map = map
        self.x = x
        self.y = y
        self.time = time
        self.drawTime = (time - map.approachTiming, time + map.approachTiming)
        self.type = type
        self.objectParams = objectParams


class Slider(HitObject):
    def __init__(self, x, y, length, repeats, hitTime):
        super().init(x, y, hitTime)
        self.repeats = repeats
        self.possibleEnds = {(x + length, y), (x, y + length), (x - length, y), (x, y - length)}
        for end in self.possibleEnds:
            if ((end[0] > HitObject.map.r and end[0] < res_width - HitObject.map.r) 
            and (end[1] > HitObject.map.r and end[1] < res_height - HitObject.map.r)):
                self.end = end

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


def imgScale(img, base):
    width = img.size[0]
    scale = base / width
    return scale

def kthDigit(num, k):
    return (num // 10**(k-1)) % 10


def appStarted(app):
    # map = Map() from importing

    app.waitingForFirstKeyPress = True # Taken from 15-112 Animations Part 3

    pygame.mixer.pre_init(44100, -16, 1, 1024) 
    # Used to remove sound delay, especially with histounds. Taken from https://stackoverflow.com/questions/18273722/pygame-sound-delay 
    pygame.mixer.init()
    app.hitsound = pygame.mixer.Sound("audio/drum-hitnormal.wav")
    app.misssound = pygame.mixer.Sound("audio/combobreak.wav")
    app.music = Sound("audio/audio.mp3")

    app.map1 = Map('pizza', 'pizza', 'pizza', 'pizza', 1, 1, 'pizza', 10, 0, 0, 10, 5)
    app.circle1 = HitObject(app.map1, app.width / 2, app.height / 2, 500, 'Circle', None)
    app.circle2 = HitObject(app.map1, app.width / 3, app.height / 3, 600, 'Circle', None)
    app.circle3 = HitObject(app.map1, app.width / 4, app.height / 4, 700, 'Circle', None)
    app.circle4 = HitObject(app.map1, app.width / 5, app.height / 5, 800, 'Circle', None)
    app.circle5 = HitObject(app.map1, app.width / 6, app.height / 6, 900, 'Circle', None)
    app.circle6 = HitObject(app.map1, app.width / 7, app.height / 7, 1000, 'Circle', None)
    app.slider1 = HitObject(app.map1, app.width / 7, app.height / 7, 1000, 'Slider', None)
    app.map1.addObject(app.circle1)
    app.map1.addObject(app.circle2)
    app.map1.addObject(app.circle3)
    app.map1.addObject(app.circle4)
    app.map1.addObject(app.circle5)
    app.map1.addObject(app.circle6)
    

    app.currMap = app.map1

    app.currObjects = [] # Holds the current drawn objects 
    app.currObjectsEnd = [] # Holds the current drawn objects' ending draw time
    app.currDrawAcc = [] # Holds the accuracy symbols that are currently being drawn

    app.cx = app.width / 2
    app.cy = app.height / 2
    app.cursorX = 0
    app.cursorY = 0
    app.timePassed = 0 + universal_offset
    app.timerDelay = 1
    app.timeAfterDrawAcc = 0

    app.modMultiplier = 1
    app.currAcc = None
    app.totalAcc = 100.00
    app.objCount = 0
    app.score = 0
    app.rawScore = 0
    app.currCombo = 0
    app.highestCombo = 0

    app.circleRaw = app.loadImage("skins/current/hitcircleoverlay.png")
    app.approachRaw = app.loadImage("skins/current/approachcircle.png")
    app.sliderFollowRaw = app.loadImage("skins/current/sliderfollowcircle.png")
    app.sliderCircleRaw = app.loadImage("skins/current/sliderb.png")
    # app.sliderFollowRaw = app.loadImage("skins/current/sliderfollowcircle.png")
    app.hit300Raw = app.loadImage("skins/current/hit300.png")        
    app.hit100Raw = app.loadImage("skins/current/hit100.png")
    app.hit50Raw = app.loadImage("skins/current/hit50.png")
    app.hit0Raw = app.loadImage("skins/current/hit0.png")
    app.cursorRaw = app.loadImage("skins/current/cursor.png")
    app.bgRaw = app.loadImage("meikaruza.jpg")

    app.combo0 = app.loadImage("skins/current/combo-0.png")
    app.combo1 = app.loadImage("skins/current/combo-1.png")
    app.combo2 = app.loadImage("skins/current/combo-2.png")
    app.combo3 = app.loadImage("skins/current/combo-3.png")
    app.combo4 = app.loadImage("skins/current/combo-4.png")
    app.combo5 = app.loadImage("skins/current/combo-5.png")
    app.combo6 = app.loadImage("skins/current/combo-6.png")
    app.combo7 = app.loadImage("skins/current/combo-7.png")
    app.combo8 = app.loadImage("skins/current/combo-8.png")
    app.combo9 = app.loadImage("skins/current/combo-9.png")
    app.comboXRaw = app.loadImage("skins/current/combo-x@2x.png")
    app.score0 = app.loadImage("skins/current/score-0.png")
    app.score1 = app.loadImage("skins/current/score-1.png")
    app.score2 = app.loadImage("skins/current/score-2.png")
    app.score3 = app.loadImage("skins/current/score-3.png")
    app.score4 = app.loadImage("skins/current/score-4.png")
    app.score5 = app.loadImage("skins/current/score-5.png")
    app.score6 = app.loadImage("skins/current/score-6.png")
    app.score7 = app.loadImage("skins/current/score-7.png")
    app.score8 = app.loadImage("skins/current/score-8.png")
    app.score9 = app.loadImage("skins/current/score-9.png")
    app.percent = app.loadImage("skins/current/score-percent.png")
    app.dot = app.loadImage("skins/current/score-dot.png")

    app.comboNums = {0: app.combo0, 1: app.combo1, 2: app.combo2, 3: app.combo3, 4: app.combo4, 
    5: app.combo5, 6: app.combo6, 7: app.combo7, 8: app.combo8, 9: app.combo9}
    app.scoreNums = {0: app.score0, 1: app.score1, 2: app.score2, 3: app.score3, 4: app.score4, 
    5: app.score5, 6: app.score6, 7: app.score7, 8: app.score8, 9: app.score9}

    app.circle = app.scaleImage(app.circleRaw, imgScale(app.circleRaw, 3 * app.map1.r))
    app.approach = app.scaleImage(app.approachRaw, 3 * imgScale(app.circleRaw, 3 * app.map1.r))
    app.hit300 = app.scaleImage(app.hit300Raw, imgScale(app.circleRaw, 3 * app.map1.r))
    app.hit100 = app.scaleImage(app.hit100Raw, imgScale(app.circleRaw, 3 * app.map1.r))
    app.hit50 = app.scaleImage(app.hit50Raw, imgScale(app.circleRaw, 3 * app.map1.r))
    app.hit0 = app.scaleImage(app.hit0Raw, imgScale(app.circleRaw, 3 * app.map1.r))
    app.cursor = app.scaleImage(app.cursorRaw, cursor_size)
    app.bg = app.scaleImage(app.bgRaw, imgScale(app.bgRaw, res_width))
    app.comboX = app.scaleImage(app.comboXRaw, 0.5)

    app.circleR = app.circle.size[0] / 2


def drawHitObject(app, canvas):
    if len(app.currObjects) > 0: # Prevents out of index error for when there are no objects yet
        for hitObject in app.currObjects:
            if hitObject.type == 'Circle':
                drawCircle(app, canvas, hitObject)
                drawApproach(app, canvas, hitObject)
            elif hitObject.type == 'Slider':
                drawSlider(app, canvas)
                drawApproach(app, canvas)
            else:
                drawSpinner(app, canvas)
   

def drawApproach(app, canvas, hitObject):
    elapsed = app.timePassed - hitObject.drawTime[0] 
    scale = 1 + 2 * (elapsed / hitObject.map.approachTiming) 
    if scale >= 3:
        scale = 3 
    canvas.create_image(hitObject.x, hitObject.y, image = ImageTk.PhotoImage(
        app.scaleImage(app.approach, 1 / scale)))


def drawCircle(app, canvas, hitObject):
    canvas.create_image(hitObject.x, hitObject.y, image = ImageTk.PhotoImage(app.circle))


def drawSlider(app, canvas, hitObject):
    r = app.circleR
    slider = Slider(hitObject)
    canvas.create_image(slider.x, slider.y, image = ImageTk.PhotoImage(app.circle))
    # canvas.create_line(slider.x, slider.y - r, )



def drawSpinner(app, canvas, hitObject):
    return 42


def drawCursor(app, canvas):
    canvas.create_image(app.cursorX, app.cursorY, image = ImageTk.PhotoImage(app.cursor))


def drawBackground(app, canvas):
    canvas.create_image(app.cx, app.cy, image = ImageTk.PhotoImage(app.bg))


def drawAcc(app, canvas):
    if len(app.currDrawAcc) > 0: 
        for acc in app.currDrawAcc:
            x, y, accuracy = acc[0], acc[1], acc[2]
            if accuracy == 300:
                canvas.create_image(x, y, image = ImageTk.PhotoImage(app.hit300))
            elif accuracy == 100:
                canvas.create_image(x, y, image = ImageTk.PhotoImage(app.hit100))
            elif accuracy == 50:
                canvas.create_image(x, y, image = ImageTk.PhotoImage(app.hit50))
            elif accuracy == 0:
                canvas.create_image(x, y, image = ImageTk.PhotoImage(app.hit0))


def drawGameUI(app, canvas):
    drawCombo(app, canvas)
    drawTotalAcc(app, canvas)
    drawTimeRemaining(app, canvas)
    drawKeyPresses(app, canvas)
    drawScore(app, canvas)
    drawHitError(app, canvas)
    drawHP(app, canvas)
    drawDrainTime(app, canvas)
    drawLocalScores(app, canvas)


def drawCombo(app, canvas):
    ones = kthDigit(app.currCombo, 1)
    tens = kthDigit(app.currCombo, 2)
    hundreds = kthDigit(app.currCombo, 3)
    thousands = kthDigit(app.currCombo, 4)

    if app.currCombo < 10:
        canvas.create_image(app.width / 100, 49 * app.height / 50, image = ImageTk.PhotoImage(app.comboNums[ones]))
        canvas.create_image(2.5 * app.width / 100, 49 * app.height / 50, image = ImageTk.PhotoImage(app.comboX))
    elif app.currCombo < 100:
        canvas.create_image(app.width / 100, 49 * app.height / 50, image = ImageTk.PhotoImage(app.comboNums[tens]))
        canvas.create_image(2.5 * app.width / 100, 49 * app.height / 50, image = ImageTk.PhotoImage(app.comboNums[ones])) 
        canvas.create_image(4 * app.width / 100, 49 * app.height / 50, image = ImageTk.PhotoImage(app.comboX))
    elif app.currCombo < 1000:
        canvas.create_image(app.width / 100, 49 * app.height / 50, image = ImageTk.PhotoImage(app.comboNums[hundreds]))
        canvas.create_image(2.5 * app.width / 100, 49 * app.height / 50, image = ImageTk.PhotoImage(app.comboNums[tens]))
        canvas.create_image(4 * app.width / 100, 49 * app.height / 50, image = ImageTk.PhotoImage(app.comboNums[ones]))
        canvas.create_image(5.5 * app.width / 100, 49 * app.height / 50, image = ImageTk.PhotoImage(app.comboX))
    elif app.currCombo < 10000:
        canvas.create_image(app.width / 100, 49 * app.height / 50, image = ImageTk.PhotoImage(app.comboNums[thousands]))
        canvas.create_image(2.5 * app.width / 100, 49 * app.height / 50, image = ImageTk.PhotoImage(app.comboNums[hundreds]))
        canvas.create_image(4 * app.width / 100, 49 * app.height / 50, image = ImageTk.PhotoImage(app.comboNums[tens]))
        canvas.create_image(5.5 * app.width / 100, 49 * app.height / 50, image = ImageTk.PhotoImage(app.comboNums[ones]))
        canvas.create_image(7 * app.width / 100, 49 * app.height / 50, image = ImageTk.PhotoImage(app.comboX))


def drawScore(app, canvas):
    ones = kthDigit(app.score, 1)
    tens = kthDigit(app.score, 2)
    hundreds = kthDigit(app.score, 3)
    thousands = kthDigit(app.score, 4)
    tenthousands = kthDigit(app.score, 5)
    hunthousands = kthDigit(app.score, 6)
    millions = kthDigit(app.score, 7)
    tenmillions = kthDigit(app.score, 8)
    
    canvas.create_image(99 * app.width / 100, app.height / 50, image = ImageTk.PhotoImage(app.scoreNums[ones]))
    canvas.create_image(97.5 * app.width / 100, app.height / 50, image = ImageTk.PhotoImage(app.scoreNums[tens]))
    canvas.create_image(96 * app.width / 100, app.height / 50, image = ImageTk.PhotoImage(app.scoreNums[hundreds]))
    canvas.create_image(94.5 * app.width / 100, app.height / 50, image = ImageTk.PhotoImage(app.scoreNums[thousands]))
    canvas.create_image(93 * app.width / 100, app.height / 50, image = ImageTk.PhotoImage(app.scoreNums[tenthousands]))
    canvas.create_image(91.5 * app.width / 100, app.height / 50, image = ImageTk.PhotoImage(app.scoreNums[hunthousands]))
    canvas.create_image(90 * app.width / 100, app.height / 50, image = ImageTk.PhotoImage(app.scoreNums[millions]))
    canvas.create_image(88.5 * app.width / 100, app.height / 50, image = ImageTk.PhotoImage(app.scoreNums[tenmillions]))


def drawTotalAcc(app, canvas):
    hundreths = kthDigit(app.totalAcc * 100, 1)
    tenths = kthDigit(app.totalAcc * 100, 2)
    ones = kthDigit(app.totalAcc * 100, 3)
    tens = kthDigit(app.totalAcc * 100, 4)
    
    canvas.create_image(99 * app.width / 100, 2.5 * app.height / 50, image = ImageTk.PhotoImage(app.scaleImage(app.percent, 0.65)))
    canvas.create_image(98 * app.width / 100, 2.5 * app.height / 50, image = ImageTk.PhotoImage(app.scaleImage(app.scoreNums[hundreths], 0.65)))
    canvas.create_image(97 * app.width / 100, 2.5 * app.height / 50, image = ImageTk.PhotoImage(app.scaleImage(app.scoreNums[tenths], 0.65)))
    canvas.create_image(96 * app.width / 100, 2.25 * app.height / 50, image = ImageTk.PhotoImage(app.dot))
    canvas.create_image(95 * app.width / 100, 2.5 * app.height / 50, image = ImageTk.PhotoImage(app.scaleImage(app.scoreNums[ones], 0.65)))
    if app.totalAcc >= 10:
        canvas.create_image(94 * app.width / 100, 2.5 * app.height / 50, image = ImageTk.PhotoImage(app.scaleImage(app.scoreNums[tens], 0.65)))
    if str(app.totalAcc) == "100.0":
        canvas.create_image(93 * app.width / 100, 2.5 * app.height / 50, image = ImageTk.PhotoImage(app.scaleImage(app.scoreNums[1], 0.65)))


def drawTimeRemaining(app, canvas):
    return 42


def drawKeyPresses(app, canvas):
    return 42


def drawHP(app, canvas):
    return 42


def drawLocalScores(app, canvas):
    return 42


def drawHitError(app, canvas):
    return 42


def drawDrainTime(app, canvas): # Post MVP
    return 42

def keyPressed(app, event):
    if app.waitingForFirstKeyPress:
        app.waitingForFirstKeyPress = False
        app.music.start(1)
    if len(app.currObjects) > 0 and event.key in ('a', 's', 'A', 'S'):
        hitObject = app.currObjects[0]
        dist = math.dist([hitObject.x, hitObject.y], [app.cursorX, app.cursorY])
        if hitObject.type == 'Circle':
            if dist < app.circleR:
                hitError = abs(app.timePassed - hitObject.time)
                if hitError < hitObject.map.hitWindow300:
                    pygame.mixer.Sound.play(app.hitsound)
                    app.currAcc = 300
                elif hitError < hitObject.map.hitWindow100:
                    pygame.mixer.Sound.play(app.hitsound)
                    app.currAcc = 100
                elif hitError < hitObject.map.hitWindow50:
                    pygame.mixer.Sound.play(app.hitsound)
                    app.currAcc = 50
                else:
                    if app.currCombo >= 0:
                        pygame.mixer.Sound.play(app.misssound)
                    app.currAcc = 0

        # elif hitObject.type == 'Slider':
        #     if dist < app.circleR:
        #         hitError = abs(app.timePassed - hitObject.time)
        #         if hitError > hitObject.map.hitWindow50:
                    # app.currAcc = 0
                app.currDrawAcc.append((hitObject.x, hitObject.y, app.currAcc))
                updateRun(app)


def timerFired(app):
    if app.waitingForFirstKeyPress:
        return

    app.timePassed += 20 # this is so sad 
    if (app.timePassed, app.timePassed + 2 * app.map1.approachTiming) in app.map1.objects:
        app.currObjects.append(app.map1.objects[app.timePassed, app.timePassed + 2 * app.map1.approachTiming])
        app.currObjectsEnd.append(app.timePassed + 2 * app.map1.approachTiming)
    if app.timePassed in app.currObjectsEnd:
        app.currAcc = 0
        hitObject = app.currObjects[0]
        app.currDrawAcc.append((hitObject.x, hitObject.y, app.currAcc))
        if app.currCombo >= 0:
            pygame.mixer.Sound.play(app.misssound)
        updateRun(app)
    if len(app.currDrawAcc) > 0:
        app.timeAfterDrawAcc += 10
        if app.timeAfterDrawAcc > 25:
            app.currDrawAcc.pop(0)
            app.timeAfterDrawAcc = 0


def mouseMoved(app, event):
    app.cursorX, app.cursorY = event.x, event.y


def appStopped(app):
    app.music.stop()


def updateRun(app):
    if app.currCombo > app.highestCombo:
        app.highestCombo = app.currCombo
    if app.currAcc == 0:
        app.currCombo = 0
    else:
        app.currCombo += 1
    app.currObjects.pop(0)
    app.currObjectsEnd.pop(0)
    app.objCount += 1
    app.rawScore += app.currAcc
    app.score += app.currAcc * (1 + (max(app.currCombo - 1, 0) * app.modMultiplier * app.map1.diffMultiplier) / 25)
    # Score scaling calculations taken from the osu! wiki: https://osu.ppy.sh/wiki/en/Gameplay/Score/ScoreV1/osu%21 
    app.totalAcc = (app.rawScore / 3) / app.objCount


def redrawAll(app, canvas):
    drawBackground(app, canvas)
    drawCursor(app, canvas)
    drawGameUI(app, canvas)
    drawHitObject(app, canvas)        
    drawAcc(app, canvas)


runApp(width=res_width, height=res_height) 