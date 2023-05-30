# Complete project details at https://RandomNerdTutorials.com

import wifimgr
from time import sleep
import machine
import senko
import os
from dr.st7735.st7735_16bit import ST7735
from machine import SPI, Pin


try:
  import usocket as socket
except:
  import socket

led = machine.Pin(2, machine.Pin.OUT)
keyMenu = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
keyU = machine.Pin(36, machine.Pin.IN, machine.Pin.PULL_UP)
keyD = machine.Pin(39, machine.Pin.IN, machine.Pin.PULL_UP)


spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13))
st7735 = ST7735(spi,4,15,None,128,160,rotate=3)
st7735.initr()
st7735.setrgb(True)


from gui.colors import colors
color = colors(st7735)

from dr.display import display

import fonts.spleen16 as spleen16
dis = display(st7735,'ST7735_FB',color.WHITE,color.BLACK)
dis.fill(color.BLACK)
dis.draw_text(spleen16, 'Happy Collector', 0, 0, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)

dis.dev.show()


wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D

# Main Code goes here, wlan is a working network.WLAN(STA_IF) instance.
print("ESP OK")


# 檔案名稱
filename = 'otalist.dat'

# 取得目錄下的所有檔案和資料夾
file_list = os.listdir()
print(file_list)
# 檢查檔案是否存在
if filename in file_list:
    #在這邊要做讀取OTA列表，然後進行OTA的執行
    print("OTA檔案存在")
    with open(filename) as f:
        lines = f.readlines()[0].strip()
     
    lines = lines.replace(' ', '')
    
    # 移除字串中的雙引號和空格，然後使用逗號分隔字串
    file_list = [file.strip('"') for file in lines.split(',')]
  
    OTA = senko.Senko(
      user="pc0808f", # Required
      repo="happycollector", # Required
      branch="alpha", # Optional: Defaults to "master"
      working_dir="happyboard/20230524V1", # Optional: Defaults to "app"
      files = file_list
    )
    if OTA.update():
        print("Updated to the latest version! Rebooting...")
        os.remove(filename)
        machine.reset()   
else:
    print("OTA檔案不存在")
    
print("ESP OTA OK")

def web_page():
  if led.value() == 1:
    gpio_state="ON"
  else:
    gpio_state="OFF"
  
  html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}</style></head><body> <h1>ESP Web Server</h1> 
  <p>GPIO state: <strong>""" + gpio_state + """</strong></p><p><a href="/?led=on"><button class="button">ON</button></a></p>
  <p><a href="/?led=off"><button class="button button2">OFF</button></a></p></body></html>"""
  return html
  
try:
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind(('', 80))
  s.listen(5)
except OSError as e:
  machine.reset()

while True:
#   print("while true loop")
  try:
    if gc.mem_free() < 102000:
      gc.collect()
#     conn, addr = s.accept()
#     conn.settimeout(3.0)
#     print('Got a connection from %s' % str(addr))
#     request = conn.recv(1024)
#     conn.settimeout(None)
#     request = str(request)
#     print('Content = %s' % request)
#     led_on = request.find('/?led=on')
#     led_off = request.find('/?led=off')
#     if led_on == 6:
#       print('LED ON')
#       led.value(1)
#     if led_off == 6:
#       print('LED OFF')
#       led.value(0)
#     response = web_page()
#     conn.send('HTTP/1.1 200 OK\n')
#     conn.send('Content-Type: text/html\n')
#     conn.send('Connection: close\n\n')
#     conn.sendall(response)
#     conn.close()
  except OSError as e:
    conn.close()
    print('Connection closed')
  if keyMenu.value()==0:
      sleep(0.02)
      if keyMenu.value()==0:
          print("reset wifi")
          try:
                # 刪除檔案
              os.remove('wifi.dat')
              print("檔案刪除成功")
              machine.reset()
          except OSError as e:
              print("刪除檔案時發生錯誤:", e)          
                      
  if keyU.value()==0:
    sleep(0.02)
    if keyU.value()==0:
        OTA = senko.Senko(
            user="pc0808f", # Required
            repo="happycollector", # Required
            branch="alpha", # Optional: Defaults to "master"
            working_dir="happyboard/20230524V1", # Optional: Defaults to "app"
            files = ["otatest1.py"]
            )
        if OTA.fetch():
            print("A newer version is available!")
            if OTA.update():
                print("Updated to the latest version! Rebooting...")
                    #machine.reset()
            else:
                print("Up to date!" )
                
  if keyD.value()==0:
    sleep(0.02)
    if keyD.value()==0:
        execfile('main2.py')