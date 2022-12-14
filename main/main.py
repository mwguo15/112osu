from cmu_112_graphics import *
from importing import *
import math
from timeit import default_timer as timer
from importing import *
from sound import *
from map import *



# Settings

effects_vol = 1
music_vol = 1
master_vol = 1
cursor_size = 1
universal_offset = 0
background_dim = 0

SliderBackground = 'black'
SliderBorder = 'gray'


def imgScale(img, base):
    width = img.size[0]
    scale = base / width
    return scale

def kthDigit(num, k):
    return (num // 10**(k-1)) % 10

def almostEqual(d1, d2): 
    return (abs(d2 - d1) < 100)

# Found out how to do different screens through 112 Part 4 Animations notes

##########################################
# Welcome Mode
##########################################


def welcomeMode_keyPressed(app, event):
    app.mode = 'selectMode'

def welcomeMode_redrawAll(app, canvas):
    canvas.create_image(res_width / 2, res_height / 2, image = app.welcomeScreen)
    canvas.create_text(res_width / 2, 93 * res_height / 100, text = 'Press anything to start!', font = ("Garamond", "30", "bold"), fill = 'black')


##########################################
# Select Mode
##########################################


def selectMode_keyPressed(app, event):

    if event.key == 'Up' and app.mapSelect > 0:
        app.mapSelect -= 1
    if event.key == 'Down' and app.mapSelect < len(app.maps) - 1:
        app.mapSelect += 1


    app.currMap = app.maps[app.mapSelect]
    app.music = Sound(app.currMap.song)
    app.bgRaw = app.loadImage(app.currMap.background)
    app.bg = ImageTk.PhotoImage(app.scaleImage(app.bgRaw, imgScale(app.bgRaw, res_width)))
    
    if event.key == 'p' and not app.paused:
        app.paused = True
    elif event.key == 'p' and app.paused:
        app.paused = False

    if not app.paused:
        app.music.start(-1)

    if event.key == 'Space':
        pygame.mixer.Sound.play(app.menuclicksound)
        app.music.stop()
        setScalings(app)
        app.mode = 'playMode'
    else:
        pygame.mixer.Sound.play(app.menuhitsound)


def selectMode_redrawAll(app, canvas):
    canvas.create_image(res_width / 2, res_height / 2, image = app.bg)
    canvas.create_rectangle(0, 0, res_width, 10 * res_height / 100, fill = 'black', outline = 'white')
    canvas.create_text(res_width / 2, 5 * res_height / 100, text = f"{app.currMap.artist} " + '-' + f" {app.currMap.title}" + f' [{app.currMap.version}]' + ' by ' + f"{app.currMap.creator}", font = ("Garamond", "30", "bold"), fill = 'blue')



##########################################
# Play Mode
##########################################

def playMode_keyPressed(app, event):
    if app.waitingForFirstKeyPress:
        app.waitingForFirstKeyPress = False
        app.music.start(1)

    if event.key == 'Escape':
        app.waitingForKeyPress = True
        app.music.stop()
        resetMap(app)
        pygame.mixer.Sound.play(app.menuhitsound)
        app.mode = 'selectMode'
    
    app.keyHeld = True

    if len(app.currObjects) > 0 and event.key in ('a', 's', 'A', 'S'):
        hitObject = app.currObjects[0]
        dist = math.dist([hitObject.x, hitObject.y], [app.cursorX, app.cursorY])
        if isinstance(hitObject, Circle):
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
                    if app.currCombo >= 10:
                        pygame.mixer.Sound.play(app.misssound)
                    app.currAcc = 0
                app.currDrawAcc.append((hitObject.x, hitObject.y, app.currAcc))
                updateRun(app)

        elif isinstance(hitObject, Slider):
            if dist < app.circleR:
                if app.followedSlider and app.drawSliderStart:
                    pygame.mixer.Sound.play(app.hitsound)
                    app.currAcc = 300
                if not app.followedSlider:
                    app.currAcc = 0         
                  

    playMode_timerFired(app)


def playMode_keyReleased(app, event):
    app.keyHeld = False


def playMode_timerFired(app):
    if app.waitingForFirstKeyPress:
        app.start = timer()


    if (app.drawObjCount < len(app.currMap.objects) and 
        (almostEqual(app.timePassed, app.currMap.objects[app.drawObjCount][0][0]) and 
        almostEqual(app.timePassed + app.currMap.approachTiming + app.currMap.hitWindow50, app.currMap.objects[app.drawObjCount][0][1]))):
        app.currObjects.append(app.currMap.objects[app.drawObjCount][1])
        if isinstance(app.currObjects[-1], Circle):
            app.currObjectsEnd.append(app.timePassed + app.currMap.approachTiming + 2 * app.currMap.hitWindow50)
        elif isinstance(app.currObjects[-1], Slider):
            app.currObjectsEnd.append(app.timePassed + app.currObjects[-1].totalSlideTime + app.currMap.approachTiming)
        app.drawObjCount += 1

    if len(app.currObjectsEnd) > 0 and almostEqual(app.timePassed, app.currObjectsEnd[0]):
        hitObject = app.currObjects[0]
        if isinstance(hitObject, Circle):
            app.currAcc = 0
            app.currDrawAcc.append((hitObject.x, hitObject.y, app.currAcc))
        elif isinstance(hitObject, Slider):
            if hitObject.repeats % 2 == 0:
                app.currDrawAcc.append((hitObject.endX, hitObject.endY, app.currAcc))
            else:
                app.currDrawAcc.append((hitObject.x, hitObject.y, app.currAcc))
            if app.currAcc > 0:
                pygame.mixer.Sound.play(app.hitsound)
        if app.currCombo >= 10 and app.currAcc == 0:
            pygame.mixer.Sound.play(app.misssound)
        updateRun(app)


    if len(app.currObjects) > 0 and isinstance(app.currObjects[0], Slider):
        slider = app.currObjects[0]

        elapsed = app.timePassed - slider.drawTime[0] - slider.approachTiming

        if elapsed >= 0:

            scaling = 1 - ((abs(elapsed - slider.slideTime) % (slider.slideTime + 1)) / slider.slideTime)
            delX = (slider.endX - slider.x) * scaling
            delY = (slider.endY - slider.y) * scaling

            if app.repeatCount % 2 == 0 and app.repeatCount > 0:
                newX = slider.endX - delX
                newY = slider.endY - delY
            else:
                newX = slider.x + delX
                newY = slider.y + delY

            if not app.keyHeld or math.dist([newX, newY], [app.cursorX, app.cursorY]) > app.sliderR:
                app.followedSlider = False
        
        if elapsed >= (app.repeatCount + 1) * slider.slideTime - 1:
            app.repeatCount += 1
            if app.followedSlider:
                pygame.mixer.Sound.play(app.hitsound)
        if elapsed >= 0:
            app.drawSliderStart = False
    
    if len(app.currDrawAcc) > 0:
        app.timeAfterDrawAcc += 150
        if app.timeAfterDrawAcc > app.accDrawTime:
            app.currDrawAcc.pop(0)
            app.timeAfterDrawAcc = 0

    end = timer()
    app.timePassed = 1000 * (end - app.start) + universal_offset


def playMode_mouseMoved(app, event):
    app.cursorX, app.cursorY = event.x, event.y


def playMode_redrawAll(app, canvas):
    drawBackground(app, canvas)
    drawHitObject(app, canvas)        
    drawGameUI(app, canvas)
    drawAcc(app, canvas)



##########################################
# Main App
##########################################

def appStarted(app):

    app.maps = importingAll()

    app._root.config(cursor = "None") # Hides mouse cursor, figured this out through the help of Professor Mike Taylor!

    pygame.mixer.pre_init(44100, -16, 1, 1024) # Used to remove sound delay, especially with hitsounds. Taken from https://stackoverflow.com/questions/18273722/pygame-sound-delay 
    pygame.mixer.init()

    app.waitingForFirstKeyPress = True # Taken from 15-112 Animations Part 3

    app.start = timer()

    app.mode = 'welcomeMode'

    app.mapSelect = 0

    app.currMap = app.maps[app.mapSelect]

    # app.mode = 'playMode' # Uncomments these five lines out if you want to only see the slider
    # app.custom1 = app.maps[2] 
    # app.currMap = app.custom1
    # app.custom1.objects = [0]
    # app.custom1.objects[0] = (12244.0, 13004.5), Slider(HitObject(app.custom1, 416, 250, 12889), 200, 1000, 1)
    
    app.welcomesound = pygame.mixer.Sound('audio/welcome.mp3') # Sound taken from here: https://www.youtube.com/watch?v=FSc48Rmpyj0 
    app.menuhitsound = pygame.mixer.Sound('audio/menuhit.wav') # Sound taken from "- ryan fancy edit", found at https://github.com/Mizaruuu/osu-RyuK-s-super-cool-skins/blob/master/Skins.md
    app.menuclicksound = pygame.mixer.Sound('audio/menuclick.wav') # Sound taken from "- ryan fancy edit", found at https://github.com/Mizaruuu/osu-RyuK-s-super-cool-skins/blob/master/Skins.md
    app.hitsound = pygame.mixer.Sound('audio/drum-hitnormal.wav') # Sound taken from "- ryan fancy edit", found at https://github.com/Mizaruuu/osu-RyuK-s-super-cool-skins/blob/master/Skins.md
    app.misssound = pygame.mixer.Sound('audio/combobreak.wav') # Sound taken from "- ryan fancy edit", found at https://github.com/Mizaruuu/osu-RyuK-s-super-cool-skins/blob/master/Skins.md
    app.music = Sound(app.currMap.song) # All songs taken from the beatmaps themselves, which are found on osu.ppy.sh
    app.paused = False

    pygame.mixer.Sound.play(app.welcomesound)

    app.currObjects = [] # Holds the current drawn objects 
    app.currObjectsEnd = [] # Holds the current drawn objects' ending draw time
    app.currDrawAcc = [] # Holds the accuracy symbols that are currently being drawn

    app.cx = app.width / 2
    app.cy = app.height / 2
    app.cursorX = 0
    app.cursorY = 0
    app.timePassed = 0
    app.timerDelay = 20
    app.timeAfterDrawAcc = 0
    app.accDrawTime = 500
    app.mouseMovedDelay = 5

    app.modMultiplier = 1
    app.currAcc = 0
    app.totalAcc = 100.00
    app.accObjCount = 0
    app.drawObjCount = 0
    app.score = 0
    app.rawScore = 0
    app.currCombo = 0
    app.highestCombo = 0
    app.keyHeld = False
    app.repeatCount = 0

    app.circleScaling = 2

    app.followedSlider = True
    app.drawSliderStart = True

    app.welcomeScreenRaw = app.loadImage("backgrounds/welcome.jpg") # Image taken from the background of https://cytoid.io/levels/bloo.neko.circles
    app.welcomeScreen = ImageTk.PhotoImage(app.scaleImage(app.welcomeScreenRaw, imgScale(app.welcomeScreenRaw, res_width)))

    # All of the following images, besides bgDim, taken from "- ryan fancy edit"

    app.circleRaw = app.loadImage("skins/current/hitcircleoverlay.png")
    app.approachRaw = app.loadImage("skins/current/approachcircle.png")
    app.sliderFollowRaw = app.loadImage("skins/current/sliderfollowcircle.png")
    app.sliderCircleRaw = app.loadImage("skins/current/sliderb.png")
    app.sliderReverseArrowLeftRaw = app.loadImage("skins/current/reversearrowleft.png")
    app.sliderReverseArrowRightRaw = app.loadImage("skins/current/reversearrowright.png")
    app.sliderReverseArrowUpRaw = app.loadImage("skins/current/reversearrowup.png")
    app.sliderReverseArrowDownRaw = app.loadImage("skins/current/reversearrowdown.png")
    app.hit300Raw = app.loadImage("skins/current/hit300.png")      
    app.hit100Raw = app.loadImage("skins/current/hit100.png")
    app.hit50Raw = app.loadImage("skins/current/hit50.png")
    app.hit0Raw = app.loadImage("skins/current/hit0.png")
    app.cursorRaw = app.loadImage("skins/current/cursor.png")
    app.bgRaw = app.loadImage(app.currMap.background)
    app.bgDim = app.loadImage('backgrounds/bgdim.jpg') # Random black square found here: https://cornellsun.com/2020/06/03/we-need-more-than-a-black-square/
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

    app.cursor = ImageTk.PhotoImage(app.scaleImage(app.cursorRaw, cursor_size))
    app.bg = ImageTk.PhotoImage(app.scaleImage(app.bgRaw, imgScale(app.bgRaw, res_width)))
    app.bgDim = ImageTk.PhotoImage(app.scaleImage(app.bgDim, imgScale(app.bgDim, res_width)))

    setScalings(app)


def setScalings(app):
    app.circle = ImageTk.PhotoImage(app.scaleImage(app.circleRaw, imgScale(app.circleRaw, app.circleScaling * app.currMap.r)))
    app.approach = app.scaleImage(app.approachRaw, 3 * imgScale(app.circleRaw, app.circleScaling * app.currMap.r))
    app.sliderCircle = ImageTk.PhotoImage(app.scaleImage(app.sliderCircleRaw, imgScale(app.circleRaw, app.circleScaling * app.currMap.r)))
    app.sliderFollow = ImageTk.PhotoImage(app.scaleImage(app.sliderFollowRaw, imgScale(app.circleRaw, app.circleScaling * 1.5 * app.currMap.r)))
    app.sliderReverseArrowLeft = ImageTk.PhotoImage(app.scaleImage(app.sliderReverseArrowLeftRaw, imgScale(app.circleRaw, 1.5 * app.currMap.r)))
    app.sliderReverseArrowRight = ImageTk.PhotoImage(app.scaleImage(app.sliderReverseArrowRightRaw, imgScale(app.circleRaw, 1.5 * app.currMap.r)))
    app.sliderReverseArrowUp = ImageTk.PhotoImage(app.scaleImage(app.sliderReverseArrowUpRaw, imgScale(app.circleRaw, 1.5 * app.currMap.r)))
    app.sliderReverseArrowDown = ImageTk.PhotoImage(app.scaleImage(app.sliderReverseArrowDownRaw, imgScale(app.circleRaw, 1.5 * app.currMap.r)))
    app.hit300 = ImageTk.PhotoImage(app.scaleImage(app.hit300Raw, imgScale(app.circleRaw, app.circleScaling * app.currMap.r)))
    app.hit100 = ImageTk.PhotoImage(app.scaleImage(app.hit100Raw, imgScale(app.circleRaw, app.circleScaling * app.currMap.r)))
    app.hit50 = ImageTk.PhotoImage(app.scaleImage(app.hit50Raw, imgScale(app.circleRaw, app.circleScaling * app.currMap.r)))
    app.hit0 = ImageTk.PhotoImage(app.scaleImage(app.hit0Raw, imgScale(app.circleRaw, app.circleScaling * app.currMap.r)))
    app.circleR = app.circleScaling * app.currMap.r / 2
    app.sliderR = app.circleR * 1.5


def resetMap(app):
    app.currObjects = [] 
    app.currObjectsEnd = [] 
    app.currDrawAcc = []
    app.accObjCount = 0
    app.drawObjCount = 0
    app.totalAcc = 100.0
    app.currAcc = 300
    app.score = 0
    app.rawScore = 0
    app.currCombo = 0
    app.highestCombo = 0
    app.keyHeld = False
    app.repeatCount = 0
    app.waitingForFirstKeyPress = True 
    app.start = timer()


def drawHitObject(app, canvas):
    if len(app.currObjects) > 0: # Prevents out of index error for when there are no objects yet
        for hitObject in app.currObjects:
            if isinstance(hitObject, Circle):
                drawCircle(app, canvas, hitObject)
                drawApproach(app, canvas, hitObject)
            elif isinstance(hitObject, Slider):
                drawSlider(app, canvas, hitObject)
   

def drawApproach(app, canvas, hitObject):
    elapsed = app.timePassed - hitObject.drawTime[0] 
    scale = 1 + 2 * (elapsed / hitObject.approachTiming) 
    if scale >= 3:
        scale = 3 
    canvas.create_image(hitObject.x, hitObject.y, image = ImageTk.PhotoImage(app.scaleImage(app.approach, 1 / scale)))


def drawCircle(app, canvas, hitObject):
    canvas.create_image(hitObject.x, hitObject.y, image = app.circle)


def drawSlider(app, canvas, hitObject):
    r = app.circleR
    slider = hitObject

    if slider.direction == 'Left' or slider.direction == 'Right':
        if slider.direction == 'Left':
            canvas.create_rectangle(slider.endX, slider.endY - r, slider.x, slider.y + r, width = 0, fill = SliderBackground)
            canvas.create_line(slider.x, slider.y - r, slider.endX, slider.endY - r, fill = SliderBorder, width = 5) 
            canvas.create_line(slider.x, slider.y + r, slider.endX, slider.endY + r, fill = SliderBorder, width = 5)

            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'chord', fill = SliderBackground, outline = SliderBackground, width = 0, extent = -180, start = 90)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'chord', fill = SliderBackground, outline = SliderBackground, width = 0, extent = 180, start = 90)
            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'arc', outline = SliderBorder, width = 5, extent = -180, start = 90)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'arc', outline = SliderBorder, width = 5, extent = 180, start = 90)
        else:
            canvas.create_rectangle(slider.x, slider.y - r, slider.endX, slider.endY + r, width = 0, fill = SliderBackground)
            canvas.create_line(slider.x, slider.y - r, slider.endX, slider.endY - r, fill = SliderBorder, width = 5) 
            canvas.create_line(slider.x, slider.y + r, slider.endX, slider.endY + r, fill = SliderBorder, width = 5)

            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'chord', fill = SliderBackground, outline = SliderBackground, width = 0, extent = 180, start = 90)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'chord', fill = SliderBackground, outline = SliderBackground, width = 0, extent = -180, start = 90)
            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'arc', outline = SliderBorder, fill = SliderBackground, width = 5, extent = 180, start = 90)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'arc', outline = SliderBorder, fill = SliderBackground, width = 5, extent = -180, start = 90)

    elif slider.direction == 'Up' or slider.direction == 'Down':
        if slider.direction == 'Up':
            canvas.create_rectangle(slider.endX - r, slider.endY, slider.x + r, slider.y, width = 0, fill = SliderBackground)
            canvas.create_line(slider.x - r, slider.y, slider.endX - r, slider.endY, fill = SliderBorder, width = 5)
            canvas.create_line(slider.x + r, slider.y, slider.endX + r, slider.endY, fill = SliderBorder, width = 5)

            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'chord', fill = SliderBackground, outline = SliderBackground, width = 0, extent = -180)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'chord', fill = SliderBackground, outline = SliderBackground, width = 0, extent = 180)
            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'arc', outline = SliderBorder, width = 5, extent = -180)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'arc', outline = SliderBorder, width = 5, extent = 180)
            
        else:
            canvas.create_rectangle(slider.x - r, slider.y, slider.endX + r, slider.endY, width = 0, fill = SliderBackground)
            canvas.create_line(slider.x - r, slider.y, slider.endX - r, slider.endY, fill = SliderBorder, width = 5)
            canvas.create_line(slider.x + r, slider.y, slider.endX + r, slider.endY, fill = SliderBorder, width = 5)
            
            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'chord', fill = SliderBackground, outline = SliderBackground, width = 0, extent = 180)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'chord', fill = SliderBackground, outline = SliderBackground, width = 0, extent = -180)
            canvas.create_arc(slider.x - r, slider.y - r, slider.x + r, slider.y + r, style = 'arc', outline = SliderBorder, width = 5, extent = 180)
            canvas.create_arc(slider.endX - r, slider.endY - r, slider.endX + r, slider.endY + r, style = 'arc', outline = SliderBorder, width = 5, extent = -180)

    if app.drawSliderStart:
        canvas.create_image(slider.x, slider.y, image = app.circle)
        drawApproach(app, canvas, hitObject)


    elapsed = app.timePassed - slider.drawTime[0] - slider.approachTiming

    if elapsed >= 0:

        scaling = 1 - ((abs(elapsed - slider.slideTime) % (slider.slideTime + 1)) / slider.slideTime)
        delX = (slider.endX - slider.x) * scaling
        delY = (slider.endY - slider.y) * scaling

        if app.repeatCount % 2 == 0 and app.repeatCount > 0:
            newX = slider.endX - delX
            newY = slider.endY - delY
        else:
            newX = slider.x + delX
            newY = slider.y + delY

        canvas.create_image(newX, newY, image = app.sliderCircle)
        if app.keyHeld and math.dist([newX, newY], [app.cursorX, app.cursorY]) <= app.sliderR:
            canvas.create_image(newX, newY, image = app.sliderFollow)

        if slider.repeats - app.repeatCount > 0:
            if app.repeatCount % 2 == 0:
                if slider.direction == 'Left':
                    canvas.create_image(slider.endX, slider.endY, image = app.sliderReverseArrowRight)
                elif slider.direction == 'Right':
                    canvas.create_image(slider.endX, slider.endY, image = app.sliderReverseArrowLeft)
                elif slider.direction == 'Up':
                    canvas.create_image(slider.endX, slider.endY, image = app.sliderReverseArrowDown)
                elif slider.direction == 'Down':
                    canvas.create_image(slider.endX, slider.endY, image = app.sliderReverseArrowUp)

            if app.repeatCount % 2 == 1:
                if slider.direction == 'Left':
                    canvas.create_image(slider.x, slider.y, image = app.sliderReverseArrowLeft)
                elif slider.direction == 'Right':
                    canvas.create_image(slider.x, slider.y, image = app.sliderReverseArrowRight)
                elif slider.direction == 'Up':
                    canvas.create_image(slider.x, slider.y, image = app.sliderReverseArrowUp)
                elif slider.direction == 'Down':
                    canvas.create_image(slider.x, slider.y, image = app.sliderReverseArrowDown)
            

def drawBackground(app, canvas):
    canvas.create_image(app.cx, app.cy, image = app.bg)
    # canvas.create_image(app.cx, app.cy, image = app.bgDim)  # Heavily lags program for some reason


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
    drawScore(app, canvas)


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


def appStopped(app):
    app.music.stop()


def updateRun(app):
    app.repeatCount = 0
    app.drawSliderStart = True
    if app.currCombo > app.highestCombo:
        app.highestCombo = app.currCombo
    if app.currAcc == 0:
        app.currCombo = 0
    else:
        app.currCombo += 1
    app.currObjects.pop(0)
    app.currObjectsEnd.pop(0)
    app.accObjCount += 1
    app.rawScore += app.currAcc
    app.score += app.currAcc * (1 + (max(app.currCombo - 1, 0) * app.modMultiplier * app.currMap.diffMultiplier) / 25)
    # Score scaling calculations taken from the osu! wiki: https://osu.ppy.sh/wiki/en/Gameplay/Score/ScoreV1/osu%21 
    app.totalAcc = (app.rawScore / 3) / app.accObjCount

runApp(width = res_width, height = res_height) 
