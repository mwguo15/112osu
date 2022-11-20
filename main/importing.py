from cmu_112_graphics import *
from main import *

def decimalToBinary(num):
    binStr = [0] * 8
    for i in range(8):
        binStr[8 - i - 1] = num % 2
        num = num // 2
    return binStr


