from cmu_112_graphics import *
import os
import shutil
from zipfile import ZipFile 
from map import *



def readingFile(file_path):
    content = ''
    for line in open(file_path, encoding = 'utf-8'):
        content += line
    return content


def oszToZip(file): # Way of iterating through directories and renaming files found here: https://www.guru99.com/python-rename-file.html
    file = os.path.splitext('maps/' + file)[0]
    os.rename(file + '.osz', file + '.zip')


def formatFileTitle(title):
    if '[no video]' in title:
        title = title.replace('[no video]', '')
    if '/' in title:
        title = title.replace('/', '_')
    return title.strip()


def extractingMaps(): # Way of processing zip files found here: https://stackoverflow.com/questions/7533677/how-to-process-zip-file-with-python
    destination_folder = 'maps/imported/'
    for file in os.listdir('maps'):
        if file.endswith('.zip'):
            with ZipFile('maps/' + file, 'r') as zip:
                for name in zip.namelist():
                    if name.endswith('.osu') and not os.path.exists('maps/imported/' + name):
                        zip.extract(name)
                        destination = destination_folder + name
                        shutil.move(name, destination)


def extractingBgAndAudio(): # Way of moving files found here: https://stackoverflow.com/questions/8858008/how-to-move-a-file-in-python
    for file in os.listdir('maps'):
        if file != 'imported':
            title = file.split('-')[1].strip().replace('.zip', '')
            title = formatFileTitle(title)
        if file.endswith('.zip') and not os.path.exists('songs/' + title + '.mp3'):
            with ZipFile('maps/' + file, 'r') as zip:
                title = file.split('-')[1].strip().replace('.zip', '')
                title = formatFileTitle(title)
                for name in zip.namelist():
                    if name.endswith('.jpg'):
                        zip.extract(name)
                        os.rename(name, title + '.jpg')
                        shutil.move(title + '.jpg', 'backgrounds/' + title + '.jpg')
                    elif name.endswith('.mp3'):
                        zip.extract(name)
                        os.rename(name, title + '.mp3')
                        shutil.move(title + '.mp3', 'songs/' + title + '.mp3')


def importingMaps():
    for map in os.listdir('maps/imported'):
        content = readingFile('maps/imported/' + map)
        title, artist, creator, version, mapID, setID, HP, CS, OD, AR = '', '', '', '', 0, 0, 0, 0, 0, 0
        for section in content.split('['):
            objectList = []
            map = Map(title, artist, creator, version, mapID, setID, HP, CS, OD, AR)
            if 'Metadata' in section:
                for data in section.split('\n'):
                    valList = data.split(':')
                    if valList[0] == 'Title':
                        title = formatFileTitle(valList[1])
                    elif valList[0] == 'Artist':
                        artist = valList[1]
                    elif valList[0] == 'Creator':
                        creator = valList[1]
                    elif valList[0] == 'Version':
                        version = valList[1]
                    elif valList[0] == 'BeatmapID':
                        mapID = valList[1]
                    elif valList[0] == 'BeatmapSetID':
                        setID = valList[1]

            if 'Difficulty' in section:
                for data in section.split('\n'):
                    valList = data.split(':')
                    if valList[0] == 'HPDrainRate':
                        HP = float(valList[1])
                    elif valList[0] == 'CircleSize':
                        CS = float(valList[1])
                    elif valList[0] == 'OverallDifficulty':
                        OD = float(valList[1])
                    elif valList[0] == 'ApproachRate':
                        AR = float(valList[1])

            if 'HitObjects' in section:
                for hitObject in section.split('\n'):
                    valList = hitObject.split(',')
                    if len(valList) > 2:
                        objectList.append(Circle(HitObject(map, int(valList[0]), int(valList[1]), int(valList[2]))))

        map.addObjects(objectList)
        maps.append(map)


def importingAll():
    for file in os.listdir('maps'):
        if file.endswith('.osz'):
            oszToZip(file)
            extractingMaps()
            extractingBgAndAudio()
    importingMaps()
    return maps

