import machine
from machine import Pin
from ssd1306 import SSD1306_I2C
import utime
from BN165DKBDriver import readKBData,parseKeyData

#165D键盘的四根数据线对应的GPIO
CP=Pin(12,Pin.OUT)
CE=Pin(13,Pin.OUT)
PL=Pin(14,Pin.OUT)
Q7=Pin(15,Pin.IN)
#按键编码翻译列表
meaningStrList=["C","D","B","A","DOWN","RIGHT","UP","LEFT"]

#OLED初始化
sda=Pin(25)
scl=Pin(26)
i2c=machine.I2C(0,sda=sda,scl=scl,freq=400000)
oled=SSD1306_I2C(128,64,i2c)

#屏幕尺寸
SCREEN_WIDTH=128
SCREEN_HEIGHT=64

#可控制方块的边长
span=20
#每次方块移动的步进
step=2
#方块的绘制模式
#0-中心A  1-中心B  2-中心C  3-中心D
mode=0

#可控制方块的位置
x=54
y=22

while True:
    #获取当前按键编码
    keyData=readKBData(1,CP,CE,PL,Q7)
    #将按键编码解析为有意义的字符串列表
    currML=parseKeyData(keyData,meaningStrList)
    #清空屏幕
    oled.fill(0)
    #根据不同绘制模式绘制方块中央的字母
    if mode==0:
        oled.text("A", x+6, y+6)
    elif mode==1:
        oled.text("B", x+6, y+6)
    elif mode==2:
        oled.text("C", x+6, y+6)
    elif mode==3:
        oled.text("D", x+6, y+6)
    #绘制方块的外包围框
    oled.rect(x,y,span,span,1)
    #执行显示
    oled.show()
    
    #根据按键情况完成任务
    for kStr in currML:
        if kStr=="LEFT":
            x=x-step
        elif kStr=="UP":
            y=y-step
        elif kStr=="DOWN":
            y=y+step
        elif kStr=="RIGHT":
            x=x+step
        elif kStr=="A":
            mode=0
            utime.sleep(0.2)
        elif kStr=="B":
            mode=1
            utime.sleep(0.2)
        elif kStr=="C":
            mode=2
            utime.sleep(0.2)
        elif kStr=="D":
            mode=3
            utime.sleep(0.2)
    #检查更新后的方块位置
    #不允许超出屏幕
    if x<0:
        x=0
    elif x>SCREEN_WIDTH-span:
        x=SCREEN_WIDTH-span
    if y<0:
        y=0
    elif y>SCREEN_HEIGHT-span:
        y=SCREEN_HEIGHT-span
    utime.sleep(0.005)


