# This demos playing sounds using Pygame:

from cmu_112_graphics import *
import pygame



class Sound(object):
    def __init__(self, path):
        self.path = path
        self.loops = 1
        pygame.mixer.music.load(path)

    # Returns True if the sound is currently playing
    def isPlaying(self):
        return bool(pygame.mixer.music.get_busy())

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
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.mixer.init()
    app.sound = pygame.mixer.Sound("hitsound.wav")
    app.music = Sound("Tokyo's Starlight.mp3")
    app.music.start(1)

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
    pass

def redrawAll(app, canvas):
    canvas.create_oval(250, 50, 350, 150, fill = 'blue')

runApp(width=600, height=200)