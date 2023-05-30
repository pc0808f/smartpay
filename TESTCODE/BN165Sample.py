import machine
from machine import Pin
import utime
from BN165DKBDriver import readKBData, parseKeyData

# 165D键盘的四根数据线对应的GPIO
CP = Pin(0, Pin.OUT)
CE = Pin(0, Pin.OUT)
PL = Pin(32, Pin.OUT)
Q7 = Pin(33, Pin.IN)

count = 0
while True:
    # 获取当前按键编码
    keyData = readKBData(1, CP, CE, PL, Q7)
    if (keyData[0] == 0):
        print("key0 press", count)
        count = count + 1
        while (keyData[0] == 0):
            keyData = readKBData(1, CP, CE, PL, Q7)

    if (keyData[1] == 0):
        print("key1 press")
        while (keyData[1] == 0):
            keyData = readKBData(1, CP, CE, PL, Q7)

    if (keyData[2] == 0):
        print("key2 press")
        while (keyData[2] == 0):
            keyData = readKBData(1, CP, CE, PL, Q7)

    if (keyData[3] == 0):
        print("key3 press")
        while (keyData[3] == 0):
            keyData = readKBData(1, CP, CE, PL, Q7)
