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

cpuid = binascii.hexlify(machine.unique_id()).decode()
token = 'a44a4cd6-20d7-4ac1-a183-7a7431ba27e9'

client = MQTTClient(
    client_id=cpuid,
    keepalive=30,
    server="172.104.127.68",
    user = "myuser",
    port = 1883,
    password = "propskymqtt",
    ssl=False)
client.connect()

def get_msg(topic, msg):
    print("topic=",topic)
    print("msg=",msg)
    decode=ujson.load(msg)
    print(decode)

client.set_callback(get_msg)
#cardid/token/fota
subTopic=cpuid+'/'+token
client.subscribe(subTopic)
subTopic=cpuid+'/'+token+'/fota'
client.subscribe(subTopic)


counter = 0
while True:
    client.check_msg()
    print(counter)
    counter = counter + 1
    client.ping()

    time.sleep(1)
