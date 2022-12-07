import pygame

class Sound(object): # Taken from Animations Part 4 on the CS-112 website, slightly edited
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

