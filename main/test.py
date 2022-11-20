# This demos loadImage and scaleImage from a url

from cmu_112_graphics import *

def appStarted(app):
    url = 'https://tinyurl.com/great-pitch-gif'
    app.image1 = app.loadImage(url)
    app.image2 = app.scaleImage(app.image1, 2/3)

def redrawAll(app, canvas):
    canvas.create_image(200, 300, image=ImageTk.PhotoImage(app.image1))
    canvas.create_image(500, 300, image=ImageTk.PhotoImage(app.image2))

runApp(width=700, height=600)