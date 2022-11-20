from cmu_112_graphics import *

def appStarted(app):
    url = 'http://www.cs.cmu.edu/~112/notes/sample-spritestrip.png'
    spritestrip = app.loadImage(url)
    app.sprites = [ ]
    for i in range(6):
        sprite = spritestrip.crop((30+260*i, 30, 230+260*i, 250))
        app.sprites.append(sprite)
    app.spriteCounter = 0

def timerFired(app):
    app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)

def redrawAll(app, canvas):
    sprite = app.sprites[app.spriteCounter]
    canvas.create_image(200, 200, image=ImageTk.PhotoImage(sprite))

runApp(width=400, height=400)