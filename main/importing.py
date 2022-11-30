from cmu_112_graphics import *
import os
# from main import *
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
    os.rename("maps/1504828 Nanahoshi Kangengakudan - MAKE A LOSER (inst).osz", "maps/1504828 Nanahoshi Kangengakudan - MAKE A LOSER (inst).zip")

# def readingFile(file_path):
#     content = [line.strip() for line in open(file_path)]
#     return content

def readingFile(file_path):
    content = ''
    for line in open(file_path):
        content += line
    return content

def importingFerb():
    hitObjects = []
    content = readingFile("maps/Bowling For Soup - Today is Gonna be a Great Day (TV Size) (Smoke) [Turtle Unicorn].osu")
    for section in content.split('['):
        if 'HitObjects' in section:
            for hitObject in section.split('\n'):
                if ':' in hitObject:
                    hitObject.join(',')
                    hitObjects.append(main.HitObject(main.app.map1, hitObject[0] * 3, hitObject[1] * 3, hitObject[2], 'Circle', None))
    return hitObjects

print(importingFerb())



