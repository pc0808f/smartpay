import wifimgr
import utime
import machine
import os
from dr.st7735.st7735_4bit import ST7735
from machine import SPI, Pin
from machine import WDT
import network
import ntptime
from machine import Pin
from BN165DKBDriver import readKBData

print('\n\r開始執行main.py初始化')
print('開機秒數:', utime.ticks_ms() / 1000)
gc.collect()
print(gc.mem_free())

GPO_CardReader_EPAY_EN = machine.Pin(19, machine.Pin.OUT)
GPO_CardReader_EPAY_EN.value(0)

LCD_EN = machine.Pin(27, machine.Pin.OUT)
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

def UDP_Load_Wifi():
    try:
        import usocket as socket
    except:
        import socket
    dis.draw_text(spleen16, 'wait UDP Wi-Fi.', 0, 16*1, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
    dis.dev.show()
    # Connect to Wi-Fi
    wifi_ssid = "Sam"
    wifi_password = "0928666624"

    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(wifi_ssid, wifi_password)
    while not station.isconnected():
        utime.sleep_ms(500)
    print("Connected to Wi-Fi")
    print('Network config: ', station.ifconfig())
    dis.draw_text(spleen16, 'UDP Wi-Fi OK', 0, 16*2, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
    dis.draw_text(spleen16, 'IP:', 0, 16*3, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
    dis.draw_text(spleen16, station.ifconfig()[0], 3, 16*4, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
    dis.dev.show()

    # Set up UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0", 1234))

    print("Listening for UDP messages on port 1234")
    dis.draw_text(spleen16, "wait UDP...", 0, 16*5, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
    dis.dev.show()

    while True:
        data, addr = udp_socket.recvfrom(1024)
        print("Received message: {}".format(data.decode('utf-8')))
        dis.draw_text(spleen16, data.decode('utf-8'), 0, 16*6, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
        dis.dev.show()
        with open('wifi.dat', "w") as f:
            f.write(data.decode('utf-8'))
        utime.sleep(3)
        machine.reset()

ESP32_TXD2_FEILOLI = machine.Pin(17, machine.Pin.IN)
# 165D键盘的四根数据线对应的GPIO
CP = Pin(0, Pin.OUT)
CE = Pin(0, Pin.OUT)
PL = Pin(32, Pin.OUT)
Q7 = Pin(33, Pin.IN)
Data_74HC165 = readKBData(1, CP, CE, PL, Q7)
print("74HC165:", Data_74HC165)
if Data_74HC165[3] == 0 :
    print("SW1被按下，結束程式")
    import sys
    sys.exit()
elif Data_74HC165[0] == 0 :
    print("SW4被按下，進入UDP load wifi")
    UDP_Load_Wifi()
elif ESP32_TXD2_FEILOLI.value() == 0 :
    print("ESP32_TXD2_FEILOLI被拉Low，進入UDP load wifi")
    UDP_Load_Wifi()

utime.sleep(1)
wdt=WDT(timeout=1000*60*5) 

wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        utime.sleep_ms(500)     # you shall not pass :D

def get_wifi_signal_strength(wlan):
    if wlan.isconnected():
        signal_strength = wlan.status('rssi')
        return signal_strength
    else:
        return None

signal_strength = get_wifi_signal_strength(wlan)
if signal_strength is not None:
    print("Wi-Fi Signal Strength:", signal_strength, "dBm")
else:
    print("Unable to retrieve signal strength.")

print("ESP Wi-Fi OK")

dis.draw_text(spleen16, 'SSID:', 0, 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
dis.draw_text(spleen16, wlan.config('essid'), 5 * 8, 16, 1, dis.fgcolor, dis.bgcolor, 0, )
dis.draw_text(spleen16, wlan.ifconfig()[0], 0, 16 + 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
dis.dev.show()

def tw_ntp(host='clock.stdtime.gov.tw', must=False):
    """
    host: 台灣可用的 ntp server 如下可任選，未指定預設為 clock.stdtime.gov.tw
        tock.stdtime.gov.tw
        watch.stdtime.gov.tw
        time.stdtime.gov.tw
        clock.stdtime.gov.tw
        tick.stdtime.gov.tw
    must: 是否非對到不可
    """ 
    ntptime.NTP_DELTA = 3155673600 # UTC+8 的 magic number
    ntptime.host = host
    count = 1
    if must:
        count = 100
    for _ in  range(count):
        try:
            ntptime.settime()
        except:
            utime.sleep(1)
            continue
        else:
            return True
    return False

tw_ntp(must=True)

# 檔案名稱
filename = 'otalist.dat'
# 取得目錄下的所有檔案和資料夾
file_list = os.listdir()
print(file_list)
# 檢查OTA檔案是否存在
if filename in file_list:
    # 在這邊要做讀取OTA列表，然後進行OTA的執行
    print("OTA檔案存在, checking files...")
    dis.draw_text(spleen16, "OTAing...", 0, 16 + 16 + 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
    dis.dev.show()
    try:
        with open(filename) as f:
            lines = f.readlines()[0].strip()

        lines = lines.replace(' ', '')

        # 移除字串中的雙引號和空格，然後使用逗號分隔字串
        file_list = [file.strip('"') for file in lines.split(',')]
        import senko
        OTA = senko.Senko(
            user="pc0808f",  # Required
            repo="smartpay",  # Required
            branch="SPHP_HWv1",  # Optional: Defaults to "master"
            working_dir="releaseFiles/latestVersion",  # Optional: Defaults to "app"
            files=file_list
        )

        if OTA.update():
            print("Updated to the latest version!")
        else:
            print("No changed-file for OTA!")
    except:
        print("Updated error!")
    
    print("刪除OTA檔案, rebooting...")
    os.remove(filename)
    machine.reset()
else:
    dis.draw_text(spleen16, "No OTA", 0, 16 + 16 + 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
    dis.dev.show()
    print("OTA檔案不存在")

print("ESP OTA OK")

while True:
    for i in range(3, 0, -1):
        dis.draw_text(spleen16, "CountDown..." + str(i), 0, 16 + 16 + 16, 1, dis.fgcolor, color.BLACK, -1, True, 0, 0)
        dis.dev.show()
        utime.sleep(1)

    # 釋放資源
    try:
        del ntptime
        del wifimgr
    except Exception as e:
        print("del error:", e)
        pass

    print(st7735)
    # import micropython
    gc.collect()
    # print(micropython.mem_info())
    print(gc.mem_free())
    try:
        print("執行 Data_Collection_Main.py ...")
        execfile('Data_Collection_Main.py')
    except Exception as e:
        print("執行失敗:", e)
        utime.sleep(5)
