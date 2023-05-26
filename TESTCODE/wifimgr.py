"""
這個檔案，是要展示如何用MQTT做OTA指令的
包含訂閱了cardid/token/fota
還有解析送回來的資料並把他存到otalist.dat中
OTA指令的密碼固定為 c0b82a2c-4b03-42a5-92cd-3478798b2a90

"""

import time
import network
from umqtt.simple import MQTTClient
import machine
import binascii
import ujson

sta_if = network.WLAN(network.STA_IF)
while not sta_if.isconnected():
    pass
print("connected")

with open('token.dat') as f:
    token = f.readlines()[0].strip()
print(token)

cpuid = binascii.hexlify(machine.unique_id()).decode()
#token = 'a44a4cd6-20d7-4ac1-a183-7a7431ba27e9'
otafile = 'otalist.dat'

client = MQTTClient(
    client_id=cpuid,
    keepalive=30,
    server="172.104.127.68",
    user="myuser",
    port=1883,
    password="propskymqtt",
    ssl=False)
client.connect()


def get_msg(topic, msg):
    payload = msg
    decode = ujson.loads(payload)

    if topic.decode() == (cpuid + '/' + token + '/fota'):
        if ('file_list' in decode) and ('password' in decode):
            if decode['password'] == 'c0b82a2c-4b03-42a5-92cd-3478798b2a90':
                print("password checked")
                with open(otafile, "w") as f:
                    f.write(''.join(decode['file_list']))
            else:
                print("password failed")


client.set_callback(get_msg)
# cardid/token/fota
subTopic = cpuid + '/' + token
client.subscribe(subTopic)
subTopic = cpuid + '/' + token + '/fota'
client.subscribe(subTopic)

counter = 0
while True:
    client.check_msg()
    print(counter)
    counter = counter + 1
    client.ping()

    time.sleep(1)

