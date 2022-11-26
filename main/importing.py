from cmu_112_graphics import *
import os
# from main import *
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


