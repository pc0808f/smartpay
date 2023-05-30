# Complete project details at https://RandomNerdTutorials.com

import wifimgr
from time import sleep
import machine
import senko
import os
from dr.st7735.st7735_4bit import ST7735
from machine import SPI, Pin

from machine import Pin
from BN165DKBDriver import readKBData

# 165D键盘的四根数据线对应的GPIO
CP = Pin(0, Pin.OUT)
CE = Pin(0, Pin.OUT)
PL = Pin(32, Pin.OUT)
Q7 = Pin(33, Pin.IN)

try:
    import usocket as socket
except:
    import socket

led = machine.Pin(2, machine.Pin.OUT)
LCD_EN = machine.Pin(27, machine.Pin.OUT)
keyMenu = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
keyU = machine.Pin(36, machine.Pin.IN, machine.Pin.PULL_UP)
keyD = machine.Pin(39, machine.Pin.IN, machine.Pin.PULL_UP)

gc.collect()
print(gc.mem_free())

LCD_EN.value(1)
spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13))
st7735 = ST7735(spi, 4, 15, None, 128, 160, rotate=0)
st7735.initb2()
st7735.setrgb(True)

from gui.colors import colors

color = colors(st7735)

from dr.display import display

import fonts.spleen16 as spleen16

dis = display(st7735, 'ST7735_FB', color.WHITE, color.BLUE)
dis.fill(color.BLACK)
dis.draw_text(spleen16, 'Happy Collector', 0, 0, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0)

dis.dev.show()

gc.collect()
print(gc.mem_free())

# if (wifimgr.read_profiles() != {}):
#     print(wifimgr.read_profiles())
#     dis.draw_text(spleen16, 'SSID:', 0, 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
#     dis.draw_text(spleen16, list(wifimgr.read_profiles().keys())[0][:10], 5 * 8, 16, 1, dis.fgcolor, dis.bgcolor, 0,
#                   True, 0, 0)
# else:
#     dis.draw_text(spleen16, 'no ssid', 0, 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
#     dis.draw_text(spleen16, 'need setup wifi..', 0, 16 + 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
# dis.dev.show()

wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D

# Main Code goes here, wlan is a working network.WLAN(STA_IF) instance.
print("ESP OK")

dis.draw_text(spleen16, 'SSID:', 0, 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
dis.draw_text(spleen16, wlan.config('essid'), 5 * 8, 16, 1, dis.fgcolor, dis.bgcolor, 0, )

dis.draw_text(spleen16, wlan.ifconfig()[0], 0, 16 + 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
# dis.draw_text(spleen16, list(wifimgr.read_profiles().keys())[0][:10], 5*8, 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
dis.dev.show()

# 檔案名稱
filename = 'otalist.dat'

# 取得目錄下的所有檔案和資料夾
file_list = os.listdir()
print(file_list)
# 檢查檔案是否存在
if filename in file_list:
    # 在這邊要做讀取OTA列表，然後進行OTA的執行
    print("OTA檔案存在")
    dis.draw_text(spleen16, "OTAing...", 0, 16 + 16 + 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
    # dis.draw_text(spleen16, list(wifimgr.read_profiles().keys())[0][:10], 5*8, 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
    dis.dev.show()
    with open(filename) as f:
        lines = f.readlines()[0].strip()

    lines = lines.replace(' ', '')

    # 移除字串中的雙引號和空格，然後使用逗號分隔字串
    file_list = [file.strip('"') for file in lines.split(',')]

    OTA = senko.Senko(
        user="pc0808f",  # Required
        repo="happycollector",  # Required
        branch="alpha",  # Optional: Defaults to "master"
        working_dir="happyboard/20230524V1",  # Optional: Defaults to "app"
        files=file_list
    )
    if OTA.update():
        print("Updated to the latest version! Rebooting...")
        os.remove(filename)
        machine.reset()
    os.remove(filename)
else:
    dis.draw_text(spleen16, "No OTA", 0, 16 + 16 + 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
    # dis.draw_text(spleen16, list(wifimgr.read_profiles().keys())[0][:10], 5*8, 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
    dis.dev.show()
    print("OTA檔案不存在")

print("ESP OTA OK")

while True:
    for i in range(9, 0, -1):
        dis.draw_text(spleen16, "CountDown..." + str(i), 0, 16 + 16 + 16, 1, dis.fgcolor, color.BLACK, -1, True, 0, 0)
        # dis.draw_text(spleen16, list(wifimgr.read_profiles().keys())[0][:10], 5*8, 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
        dis.dev.show()
        sleep(1)

    try:
        del dis
        del color
        del st7735
        del spi
        del spleen16
        del colors
        del display
        del ST7735
    except:
        print("del error")
        pass
    gc.collect()
    print(gc.mem_free())
    execfile('Data_Collection_Main_0525v4RX_task.py')


