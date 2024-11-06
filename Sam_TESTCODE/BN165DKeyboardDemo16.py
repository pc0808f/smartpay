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
meaningStrList=["-","6","5","4",
                "+","3","2","1",
                "/","BS","0",".",
                "*","9","8","7"]

#OLED初始化
sda=Pin(25)
scl=Pin(26)
i2c=machine.I2C(0,sda=sda,scl=scl,freq=400000)
oled=SSD1306_I2C(128,64,i2c)

#当前内容字符串
currStr=""
#当前光标
cursor="_"
#光标闪烁计数器
cursorCount=0
#每行显示字符数
LINE_LEN=16

#主循环
while True:
    #获取当前按键编码
    keyData=readKBData(2,CP,CE,PL,Q7)
    #将按键编码解析为有意义的列表
    currML=parseKeyData(keyData,meaningStrList)
    #要显示的内容
    currNr=currStr+cursor
    #清空屏幕
    oled.fill(0)
    #行计数器
    lineCount=0
    #显示结束标志
    isFinish=False
    #遍历每一行进行显示
    while True:
        #如果当前剩余内容大于一行
        if(len(currNr)>LINE_LEN):
            #截取当前行内容
            currLine=currNr[0:LINE_LEN]
            #将当前行从总内容中删除
            currNr=currNr[LINE_LEN:]
        else:
            #剩余内容为当前行内容
            currLine=currNr
            #显示工作结束标志设置为True
            isFinish=True
        #显示当前行
        oled.text(currLine,0,lineCount*10)
        #行数加1
        lineCount=lineCount+1
        #若显示工作结束标志为True则退出循环
        if isFinish:break
    #实际执行显示
    oled.show()    
    #若当前有且仅有一个键按下
    if(len(currML)==1):
        #若不是backspace
        if(currML[0]!="BS"):
            currStr=currStr+currML[0]
        #若是backspace
        else:
            if(len(currStr)>0):
                currStr=currStr[:-1]
        #处理完按键休眠200ms，防止无效连按
        utime.sleep(0.2)
    #光标闪烁计数器加1
    cursorCount=cursorCount+1
    #若光标闪烁计数器大于等于阈值
    if(cursorCount>=10):
        #光标闪烁计数器归0
        cursorCount=0
        #光标在空格和下划线之间来回转换
        if(cursor=="_"):
            cursor=" "
        else:
            cursor="_"
    #主循环每步休眠5ms
    utime.sleep(0.005)



