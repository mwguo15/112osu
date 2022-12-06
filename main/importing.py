from cmu_112_graphics import *
import os
from main import Circle, HitObject, Slider
import main
from zipfile import ZipFile 


def decimalToBinary(num):
    binStr = [0] * 8
    for i in range(8):
        binStr[8 - i - 1] = num % 2
        num = num // 2
    return binStr


def readingZip(zip_name, file_name): # Way of reading zip files found here: https://www.geeksforgeeks.org/working-zip-files-python/ 
    with ZipFile(zip_name, 'r') as zip:
        zip.extract(file_name)

def extractUI(skin_name):
    return 42

def importMap(map_name): # Way of renaming files found here: https://www.guru99.com/python-rename-file.html
    for file in os.listdir("maps"):
        if file.endswith(".osu"):
            newstr = file.replace(".osu", "")
            newstr = newstr.replace("_face_righteyeclahe_closed", "")
            print(newstr)



def readingFile(file_path):
    content = ''
    for line in open(file_path):
        content += line
    return content

def importingCircles():
    hitObjects = []
    content = readingFile("maps/Peter Lambert - osu! tutorial (Sushi) [Rookie Gameplay].osu")
    for section in content.split('['):
        if 'HitObjects' in section:
            for hitObject in section.split('\n'):
                valList = hitObject.split(',')
                if len(valList) > 2:
                    print(valList[0], valList[1], valList[2])

                    hitObjects.append(Circle(HitObject(main.maps, int(valList[0]), int(valList[1]), int(valList[2]), None)))
    return hitObjects

print(importingCircles())



