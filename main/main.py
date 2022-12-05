from cmu_112_graphics import *
# from importing import *
import math
import pygame
import time




# Settings

res_width = 1920
res_height = 1080
effects_vol = 1
music_vol = 1
master_vol = 1
cursor_size = 1
skin = dict()
universal_offset = 0
background_dim = 50
maps = []


# From skin.ini files, need to read later on
SliderBackground = 'black'
SliderBorder = 'gray'

# Map and object definitions taken from 
# https://osu.ppy.sh/wiki/en/Client/File_formats/Osu_%28file_format%29


class Map():
    def __init__(self, title, artist, creator, version, mapID, setID, background, HP, CS, OD, AR, starRating, sliderMultiplier):
        # HP = HP drain rate, CS = circle size, OD = overall difficulty, AR = approach rate
        # Definitions of these difficulty setting terms can be found at 
        # https://osu.ppy.sh/wiki/en/Client/Beatmap_editor/Song_Setup#difficulty

        self.title = title
        self.artist = artist
        self.creator = creator
        self.version = version
        self.mapID = mapID
        self.setID = setID
        self.background = background
        
        self.HP = HP
        self.CS = CS
        self.OD = OD
        self.AR = AR
        self.starRating = starRating
        self.sliderMultiplier = sliderMultiplier
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

    def addObjects(self, objectList):
        for object in objectList:
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


class Slider():
    def __init__(self, HitObject):
        self.x = HitObject.x
        self.y = HitObject.y
        self.approachTiming = HitObject.map.approachTiming
        self.length = HitObject.objectParams[0]
        self.slideTime = HitObject.objectParams[1]
        self.repeats = HitObject.objectParams[2]
        self.time = HitObject.time
        self.totalSlideTime = self.slideTime * (self.repeats + 1)
        self.velocity = self.length / self.slideTime

        self.possibleEnds = {(self.x + self.length, self.y, 'Right'), (self.x, self.y + self.length, 'Down'), 
        (self.x - self.length, self.y, 'Left'), (self.x, self.y - self.length, 'Up')}
        for end in self.possibleEnds:
            if ((end[0] > HitObject.map.r and end[0] < res_width - HitObject.map.r) 
            and (end[1] > HitObject.map.r and end[1] < res_height - HitObject.map.r)):
                self.endX, self.endY = end[0], end[1]
                self.direction = end[2]
 

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

def osuPixelsToReal(pixels):
    return pixels * (res_width / 640)


def imgScale(img, base):
    width = img.size[0]
    scale = base / width
    return scale

def kthDigit(num, k):
    return (num // 10**(k-1)) % 10

def almostEqual(d1, d2): # Taken from CS-112 notes (Data Types and Operators)
    epsilon = 10**-2
    return (abs(d2 - d1) < epsilon)

def appStarted(app):
    # map = Map() from importing

    pygame.init()

    pygame.mouse.set_visible(False)

    app.waitingForFirstKeyPress = True # Taken from 15-112 Animations Part 3

    pygame.mixer.pre_init(44100, -16, 1, 1024) 
    # Used to remove sound delay, especially with histounds. Taken from https://stackoverflow.com/questions/18273722/pygame-sound-delay 
    pygame.mixer.init()
    app.hitsound = pygame.mixer.Sound("audio/drum-hitnormal.wav")
    app.misssound = pygame.mixer.Sound("audio/combobreak.wav")
    app.music = Sound("audio/meikaruza.mp3")

    # app.map1 = Map('Today is Gonna be a Great Day (TV Size)', 'Bowling For Soup', 'Smoke', 'Turtle Unicorn', 2518847, 1209835, 'phineas and ferb.jpg', 10, 4, 4, 10, 6.3, 1.8)
    app.map1 = Map('MAKE A LOSER (inst)', 'Nanahoshi Kangengakudan', 'Keqing', "Yudragen's Expert", 3359370, 1504828, 'meikaruza.jpg', 5.4, 4, 4, 10, 6.3, 1.44)    
    app.circle1 = HitObject(app.map1, app.width / 2, app.height / 2, 500, 'Circle', None)
    app.circle2 = HitObject(app.map1, app.width / 3, app.height / 3, 700, 'Circle', None)
    app.circle3 = HitObject(app.map1, app.width / 4, app.height / 4, 900, 'Circle', None)
    app.circle4 = HitObject(app.map1, app.width / 5, app.height / 5, 1100, 'Circle', None)
    app.circle5 = HitObject(app.map1, app.width / 6, app.height / 6, 1300, 'Circle', None)
    app.circle6 = HitObject(app.map1, app.width / 2, app.height / 2, 1400, 'Circle', None)
    app.slider1 = HitObject(app.map1, 1000, 500, 1300, 'Slider', (300, 300, 1))

    # app.circle1 = HitObject(app.map1, 70 * 3, 94 * 3, 12889 // 15, 'Circle', None)
    # app.circle2 = HitObject(app.map1, 123 * 3, 357 * 3, 13211 // 15, 'Circle', None)
    # app.circle3 = HitObject(app.map1, 192 * 3, 153, 13377 // 15, 'Circle', None)
    # app.circle4 = HitObject(app.map1, 31 * 3, 295 * 3, 13543 // 15, 'Circle', None)
    # app.circle5 = HitObject(app.map1, 238 * 3, 260 * 3, 13691 // 15, 'Circle', None)
    # app.circle6 = HitObject(app.map1, 192 * 3, 153 * 3, 14031 // 15, 'Circle', None)
    # ^ Trying to take actual map values to map it correctly 

    # app.map1.addObjects([app.circle1, app.circle2, app.circle3, app.circle4, app.circle5, app.circle6])
    app.map1.addObjects([app.slider1])  # Slider testing

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
    app.mouseMovedDelay = 1

    app.modMultiplier = 1
    app.currAcc = None
    app.totalAcc = 100.00
    app.objCount = 0
    app.score = 0
    app.rawScore = 0
    app.currCombo = 0
    app.highestCombo = 0
    app.keyHeld = False

    app.circleRaw = app.loadImage("skins/current/hitcircleoverlay.png")
    app.approachRaw = app.loadImage("skins/current/approachcircle.png")
    app.sliderFollowRaw = app.loadImage("skins/current/sliderfollowcircle.png")
    app.sliderCircleRaw = app.loadImage("skins/current/sliderb.png")
    app.sliderReverseArrowRaw = app.loadImage("skins/current/reversearrow@2x.png")
    app.hit300Raw = app.loadImage("skins/current/hit300.png")      
    app.hit100Raw = app.loadImage("skins/current/hit100.png")
    app.hit50Raw = app.loadImage("skins/current/hit50.png")
    app.hit0Raw = app.loadImage("skins/current/hit0.png")
    app.cursorRaw = app.loadImage("skins/current/cursor.png")
    app.bgRaw = app.loadImage(app.map1.background)
    app.bgDim = app.loadImage("bgdim.jpg")
    app.bgDim.putalpha(round((background_dim / 100) * 255))
    app.comboXRaw = app.loadImage("skins/current/combo-x@2x.png")
    app.percentRaw = app.loadImage("skins/current/score-percent.png")
    app.score0Raw = app.loadImage("skins/current/score-0.png")
    app.score1Raw = app.loadImage("skins/current/score-1.png")
    app.score2Raw = app.loadImage("skins/current/score-2.png")
    app.score3Raw = app.loadImage("skins/current/score-3.png")
    app.score4Raw = app.loadImage("skins/current/score-4.png")
    app.score5Raw = app.loadImage("skins/current/score-5.png")
    app.score6Raw = app.loadImage("skins/current/score-6.png")
    app.score7Raw = app.loadImage("skins/current/score-7.png")
    app.score8Raw = app.loadImage("skins/current/score-8.png")
    app.score9Raw = app.loadImage("skins/current/score-9.png")


    app.combo0 = ImageTk.PhotoImage(app.loadImage("skins/current/combo-0.png"))
    app.combo1 = ImageTk.PhotoImage(app.loadImage("skins/current/combo-1.png"))
    app.combo2 = ImageTk.PhotoImage(app.loadImage("skins/current/combo-2.png"))
    app.combo3 = ImageTk.PhotoImage(app.loadImage("skins/current/combo-3.png"))
    app.combo4 = ImageTk.PhotoImage(app.loadImage("skins/current/combo-4.png"))
    app.combo5 = ImageTk.PhotoImage(app.loadImage("skins/current/combo-5.png"))
    app.combo6 = ImageTk.PhotoImage(app.loadImage("skins/current/combo-6.png"))
    app.combo7 = ImageTk.PhotoImage(app.loadImage("skins/current/combo-7.png"))
    app.combo8 = ImageTk.PhotoImage(app.loadImage("skins/current/combo-8.png"))
    app.combo9 = ImageTk.PhotoImage(app.loadImage("skins/current/combo-9.png"))
    app.acc0 = ImageTk.PhotoImage(app.scaleImage(app.score0Raw, 0.65))
    app.acc1 = ImageTk.PhotoImage(app.scaleImage(app.score1Raw, 0.65))
    app.acc2 = ImageTk.PhotoImage(app.scaleImage(app.score2Raw, 0.65))
    app.acc3 = ImageTk.PhotoImage(app.scaleImage(app.score3Raw, 0.65))
    app.acc4 = ImageTk.PhotoImage(app.scaleImage(app.score4Raw, 0.65))
    app.acc5 = ImageTk.PhotoImage(app.scaleImage(app.score5Raw, 0.65))
    app.acc6 = ImageTk.PhotoImage(app.scaleImage(app.score6Raw, 0.65))
    app.acc7 = ImageTk.PhotoImage(app.scaleImage(app.score7Raw, 0.65))
    app.acc8 = ImageTk.PhotoImage(app.scaleImage(app.score8Raw, 0.65))
    app.acc9 = ImageTk.PhotoImage(app.scaleImage(app.score9Raw, 0.65))
    app.score0 = ImageTk.PhotoImage(app.score0Raw)
    app.score1 = ImageTk.PhotoImage(app.score1Raw)
    app.score2 = ImageTk.PhotoImage(app.score2Raw)
    app.score3 = ImageTk.PhotoImage(app.score3Raw)
    app.score4 = ImageTk.PhotoImage(app.score4Raw)
    app.score5 = ImageTk.PhotoImage(app.score5Raw)
    app.score6 = ImageTk.PhotoImage(app.score6Raw)
    app.score7 = ImageTk.PhotoImage(app.score7Raw)
    app.score8 = ImageTk.PhotoImage(app.score8Raw)
    app.score9 = ImageTk.PhotoImage(app.score9Raw)


    app.comboX = ImageTk.PhotoImage(app.scaleImage(app.comboXRaw, 0.5))
    app.scorepercent = ImageTk.PhotoImage(app.percentRaw)
    app.accpercent = ImageTk.PhotoImage(app.scaleImage(app.percentRaw, 0.65))
    app.dot = ImageTk.PhotoImage(app.loadImage("skins/current/score-dot.png"))

    app.comboNums = {0: app.combo0, 1: app.combo1, 2: app.combo2, 3: app.combo3, 4: app.combo4, 
    5: app.combo5, 6: app.combo6, 7: app.combo7, 8: app.combo8, 9: app.combo9}
    app.accNums = {0: app.acc0, 1: app.acc1, 2: app.acc2, 3: app.acc3, 4: app.acc4, 
    5: app.acc5, 6: app.acc6, 7: app.acc7, 8: app.acc8, 9: app.acc9}
    app.scoreNums = {0: app.score0, 1: app.score1, 2: app.score2, 3: app.score3, 4: app.score4, 
    5: app.score5, 6: app.score6, 7: app.score7, 8: app.score8, 9: app.score9}

    app.circle = ImageTk.PhotoImage(app.scaleImage(app.circleRaw, imgScale(app.circleRaw, 3 * app.map1.r)))
    app.approach = app.scaleImage(app.approachRaw, 3 * imgScale(app.circleRaw, 3 * app.map1.r))
    app.sliderCircle = ImageTk.PhotoImage(app.scaleImage(app.sliderCircleRaw, imgScale(app.circleRaw, 3 * app.map1.r)))
    app.sliderFollow = ImageTk.PhotoImage(app.scaleImage(app.sliderFollowRaw, imgScale(app.circleRaw, 3 * app.map1.r)))
    app.sliderReverseArrow = ImageTk.PhotoImage(app.scaleImage(app.sliderReverseArrowRaw, imgScale(app.circleRaw, 3 * app.map1.r)))
    app.hit300 = ImageTk.PhotoImage(app.scaleImage(app.hit300Raw, imgScale(app.circleRaw, 3 * app.map1.r)))
    app.hit100 = ImageTk.PhotoImage(app.scaleImage(app.hit100Raw, imgScale(app.circleRaw, 3 * app.map1.r)))
    app.hit50 = ImageTk.PhotoImage(app.scaleImage(app.hit50Raw, imgScale(app.circleRaw, 3 * app.map1.r)))
    app.hit0 = ImageTk.PhotoImage(app.scaleImage(app.hit0Raw, imgScale(app.circleRaw, 3 * app.map1.r)))
    app.cursor = ImageTk.PhotoImage(app.scaleImage(app.cursorRaw, cursor_size))
    app.bg = ImageTk.PhotoImage(app.scaleImage(app.bgRaw, imgScale(app.bgRaw, res_width)))
    app.bgDim = ImageTk.PhotoImage(app.scaleImage(app.bgDim, imgScale(app.bgDim, res_width)))

    app.circleR = (3 * app.map1.r) / 2


def drawHitObject(app, canvas):
    if len(app.currObjects) > 0: # Prevents out of index error for when there are no objects yet
        for hitObject in app.currObjects:
            if hitObject.type == 'Circle':
                drawCircle(app, canvas, hitObject)
                drawApproach(app, canvas, hitObject)
            elif hitObject.type == 'Slider':
                drawSlider(app, canvas, hitObject)
                drawApproach(app, canvas, hitObject)
   

def drawApproach(app, canvas, hitObject):
    elapsed = app.timePassed - hitObject.drawTime[0] 
    scale = 1 + 2 * (elapsed / hitObject.map.approachTiming) 
    if scale >= 3:
        scale = 3 
    canvas.create_image(hitObject.x, hitObject.y, image = ImageTk.PhotoImage(app.scaleImage(app.approach, 1 / scale)))


def drawCircle(app, canvas, hitObject):
    canvas.create_image(hitObject.x, hitObject.y, image = app.circle)


def drawSlider(app, canvas, hitObject):
    r = app.circleR
    slider = Slider(hitObject)
    elapsed = app.timePassed - hitObject.drawTime[0]

    if slider.direction == 'Left' or slider.direction == 'Right':
        if slider.direction == 'Left':
            canvas.create_rectangle(slider.endX, slider.endY - r, slider.x, slider.y + r, width = 0, fill = SliderBackground)
            canvas.create_line(slider.x, slider.y - r, slider.endX, slider.endY - r, fill = SliderBorder, width = 5) # width should scale
            canvas.create_line(slider.x, slider.y + r, slider.endX, slider.endY + r, fill = SliderBorder, width = 5)

            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'chord', fill = SliderBackground, width = 0, extent = -180, start = 90)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'chord', fill = SliderBackground, width = 0, extent = 180, start = 90)
            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'arc', outline = SliderBorder, width = 5, extent = -180, start = 90)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'arc', outline = SliderBorder, width = 5, extent = 180, start = 90)
        else:
            canvas.create_rectangle(slider.x, slider.y - r, slider.endX, slider.endY + r, width = 0, fill = SliderBackground)
            canvas.create_line(slider.x, slider.y - r, slider.endX, slider.endY - r, fill = SliderBorder, width = 5) 
            canvas.create_line(slider.x, slider.y + r, slider.endX, slider.endY + r, fill = SliderBorder, width = 5)

            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'chord', fill = SliderBackground, width = 0, extent = 180, start = 90)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'chord', fill = SliderBackground, width = 0, extent = -180, start = 90)
            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'arc', outline = SliderBorder, fill = SliderBackground, width = 5, extent = 180, start = 90)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'arc', outline = SliderBorder, fill = SliderBackground, width = 5, extent = -180, start = 90)

    elif slider.direction == 'Up' or slider.direction == 'Down':
        if slider.direction == 'Up':
            canvas.create_rectangle(slider.endX - r, slider.endY, slider.x + r, slider.y, width = 0, fill = SliderBackground)
            canvas.create_line(slider.x - r, slider.y, slider.endX - r, slider.endY, fill = SliderBorder, width = 5)
            canvas.create_line(slider.x + r, slider.y, slider.endX + r, slider.endY, fill = SliderBorder, width = 5)

            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'chord', fill = SliderBackground, width = 0, extent = -180)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'chord', fill = SliderBackground, width = 0, extent = 180)
            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'arc', outline = SliderBorder, width = 5, extent = -180)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'arc', outline = SliderBorder, width = 5, extent = 180)
            
        else:
            canvas.create_rectangle(slider.x - r, slider.y, slider.endX + r, slider.endY, width = 0, fill = SliderBackground)
            canvas.create_line(slider.x - r, slider.y, slider.endX - r, slider.endY, fill = SliderBorder, width = 5)
            canvas.create_line(slider.x + r, slider.y, slider.endX + r, slider.endY, fill = SliderBorder, width = 5)
            
            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'chord', fill = SliderBackground, width = 0, extent = 180)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'chord', fill = SliderBackground, width = 0, extent = -180)
            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'arc', outline = SliderBorder, width = 5, extent = 180)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'arc', outline = SliderBorder, width = 5, extent = -180)

    
    canvas.create_image(slider.x, slider.y, image = app.circle)

    repeats = slider.repeats

    scaling = ((((elapsed - slider.approachTiming) % slider.slideTime) / slider.slideTime))
    delX = (slider.endX - slider.x) * scaling
    delY = (slider.endY - slider.y) * scaling
    
    if scaling > 0.96 and repeats > 0: #something related to distance from each slider end
        repeats -= 1
        newX = slider.endX - delX
        newY = slider.endY - delY
        print('pizzas')
    else:
        newX = slider.x + delX
        newY = slider.y + delY
        print('wow')

    print(f'scaling: {scaling}')
    print(f'new x and new y: {newX, newY}')
    print(f'end x and end y: {slider.endX, slider.endY}')
    print(f'del x and del y: {delX, delY}')

    if elapsed >= slider.approachTiming:
        canvas.create_image(newX, newY, image = app.sliderCircle)
        if app.keyHeld:
            canvas.create_image(newX, newY, image = app.sliderFollow)
    


def drawSpinner(app, canvas, hitObject):
    return 42


def drawBackground(app, canvas):
    canvas.create_image(app.cx, app.cy, image = app.bg)
    # canvas.create_image(app.cx, app.cy, image = app.bgDim)


def drawAcc(app, canvas):
    if len(app.currDrawAcc) > 0: 
        for acc in app.currDrawAcc:
            x, y, accuracy = acc[0], acc[1], acc[2]
            if accuracy == 300:
                canvas.create_image(x, y, image = app.hit300)
            elif accuracy == 100:
                canvas.create_image(x, y, image = app.hit100)
            elif accuracy == 50:
                canvas.create_image(x, y, image = app.hit50)
            elif accuracy == 0:
                canvas.create_image(x, y, image = app.hit0)


def drawGameUI(app, canvas):
    drawCursor(app, canvas)
    drawCombo(app, canvas)
    drawTotalAcc(app, canvas)
    drawTimeRemaining(app, canvas)
    drawKeyPresses(app, canvas)
    drawScore(app, canvas)
    drawHitError(app, canvas)
    drawHP(app, canvas)
    drawDrainTime(app, canvas)
    drawLocalScores(app, canvas)


def drawCursor(app, canvas):
    canvas.create_image(app.cursorX, app.cursorY, image = app.cursor)


def drawCombo(app, canvas):
    ones = kthDigit(app.currCombo, 1)
    tens = kthDigit(app.currCombo, 2)
    hundreds = kthDigit(app.currCombo, 3)
    thousands = kthDigit(app.currCombo, 4)

    if app.currCombo < 10:
        canvas.create_image(app.width / 100, 49 * app.height / 50, image = app.comboNums[ones])
        canvas.create_image(2.5 * app.width / 100, 49 * app.height / 50, image = app.comboX)
    elif app.currCombo < 100:
        canvas.create_image(app.width / 100, 49 * app.height / 50, image = app.comboNums[tens])
        canvas.create_image(2.5 * app.width / 100, 49 * app.height / 50, image = app.comboNums[ones]) 
        canvas.create_image(4 * app.width / 100, 49 * app.height / 50, image = app.comboX)
    elif app.currCombo < 1000:
        canvas.create_image(app.width / 100, 49 * app.height / 50, image = app.comboNums[hundreds])
        canvas.create_image(2.5 * app.width / 100, 49 * app.height / 50, image = app.comboNums[tens])
        canvas.create_image(4 * app.width / 100, 49 * app.height / 50, image = app.comboNums[ones])
        canvas.create_image(5.5 * app.width / 100, 49 * app.height / 50, image = app.comboX)
    elif app.currCombo < 10000:
        canvas.create_image(app.width / 100, 49 * app.height / 50, image = app.comboNums[thousands])
        canvas.create_image(2.5 * app.width / 100, 49 * app.height / 50, image = app.comboNums[hundreds])
        canvas.create_image(4 * app.width / 100, 49 * app.height / 50, image = app.comboNums[tens])
        canvas.create_image(5.5 * app.width / 100, 49 * app.height / 50, image = app.comboNums[ones])
        canvas.create_image(7 * app.width / 100, 49 * app.height / 50, image = app.comboX)


def drawScore(app, canvas):
    ones = kthDigit(app.score, 1)
    tens = kthDigit(app.score, 2)
    hundreds = kthDigit(app.score, 3)
    thousands = kthDigit(app.score, 4)
    tenthousands = kthDigit(app.score, 5)
    hunthousands = kthDigit(app.score, 6)
    millions = kthDigit(app.score, 7)
    tenmillions = kthDigit(app.score, 8)
    
    canvas.create_image(99 * app.width / 100, app.height / 50, image = app.scoreNums[ones])
    canvas.create_image(97.5 * app.width / 100, app.height / 50, image = app.scoreNums[tens])
    canvas.create_image(96 * app.width / 100, app.height / 50, image = app.scoreNums[hundreds])
    canvas.create_image(94.5 * app.width / 100, app.height / 50, image = app.scoreNums[thousands])
    canvas.create_image(93 * app.width / 100, app.height / 50, image = app.scoreNums[tenthousands])
    canvas.create_image(91.5 * app.width / 100, app.height / 50, image = app.scoreNums[hunthousands])
    canvas.create_image(90 * app.width / 100, app.height / 50, image = app.scoreNums[millions])
    canvas.create_image(88.5 * app.width / 100, app.height / 50, image = app.scoreNums[tenmillions])


def drawTotalAcc(app, canvas):
    hundreths = kthDigit(app.totalAcc * 100, 1)
    tenths = kthDigit(app.totalAcc * 100, 2)
    ones = kthDigit(app.totalAcc * 100, 3)
    tens = kthDigit(app.totalAcc * 100, 4)
    
    canvas.create_image(99 * app.width / 100, 2.5 * app.height / 50, image = app.accpercent)
    canvas.create_image(98 * app.width / 100, 2.5 * app.height / 50, image = app.accNums[hundreths])
    canvas.create_image(97 * app.width / 100, 2.5 * app.height / 50, image = app.accNums[tenths])
    canvas.create_image(96 * app.width / 100, 2.25 * app.height / 50, image = app.dot)
    canvas.create_image(95 * app.width / 100, 2.5 * app.height / 50, image = app.accNums[ones])
    if app.totalAcc >= 10:
        canvas.create_image(94 * app.width / 100, 2.5 * app.height / 50, image = app.accNums[tens])
    if str(app.totalAcc) == "100.0":
        canvas.create_image(93 * app.width / 100, 2.5 * app.height / 50, image = app.accNums[1])


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

    app.keyHeld = True

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
                    if app.currCombo >= 20:
                        pygame.mixer.Sound.play(app.misssound)
                    app.currAcc = 0

        # elif hitObject.type == 'Slider':
        #     if dist < app.circleR:
        #         hitError = abs(app.timePassed - hitObject.time)
        #         if hitError > hitObject.map.hitWindow50:
                    # app.currAcc = 0
                app.currDrawAcc.append((hitObject.x, hitObject.y, app.currAcc))
                updateRun(app)

    timerFired(app)

def keyReleased(app, event):
    app.keyHeld = False

def timerFired(app):
    if app.waitingForFirstKeyPress:
        return

    # print(app.timePassed)
    app.timePassed += 10 # Change to delta time, multiply everything by constant

    if (app.timePassed, app.timePassed + 2 * app.map1.approachTiming) in app.map1.objects:
        app.currObjects.append(app.map1.objects[app.timePassed, app.timePassed + 2 * app.map1.approachTiming])
        if isinstance(app.currObjects[-1], HitObject):
            app.currObjectsEnd.append(app.timePassed + 2 * app.map1.approachTiming)
        elif isinstance(app.currObjects[-1], Slider):
            app.currObjectsEnd.append(app.timePassed + app.currObjects[-1].totalSlideTime + app.map1.approachTiming)

    if app.timePassed in app.currObjectsEnd:
        hitObject = app.currObjects[0]
        if isinstance(hitObject, HitObject):
            app.currAcc = 0
            app.currDrawAcc.append((hitObject.x, hitObject.y, app.currAcc))

        elif isinstance(hitObject, Slider):
            if hitObject.repeats % 2 == 0:
                app.currDrawAcc.append((hitObject.endX, hitObject.endY, app.currAcc))
            else:
                app.currDrawAcc.append((hitObject.x, hitObject.y, app.currAcc))

        if app.currCombo >= 20 and app.currAcc == 0:
            pygame.mixer.Sound.play(app.misssound)
        updateRun(app)

    if len(app.currDrawAcc) > 0:
        app.timeAfterDrawAcc += 10
        if app.timeAfterDrawAcc > 150:
            app.currDrawAcc.pop(0)
            app.timeAfterDrawAcc = 0

    # last timer fire call (frame time)

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
    drawHitObject(app, canvas)        
    drawGameUI(app, canvas)
    drawAcc(app, canvas)

runApp(width=res_width, height=res_height) 