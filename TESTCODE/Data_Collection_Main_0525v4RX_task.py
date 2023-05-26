import time
import machine
from machine import UART
# import uasyncio as asyncio
import _thread
import utime

# 定義狀態類型
class MainStatus:
    NONE_WIFI = 0         # 還沒連上WiFi
    NONE_INTERNET = 1     # 連上WiFi，但還沒連上外網      現在先不做這個判斷
    NONE_MQTT = 2         # 連上外網，但還沒連上MQTT Broker
    NONE_FEILOLI = 3      # 連上MQTT，但還沒連上FEILOLI娃娃機
    STANDBY_FEILOLI = 4   # 連上FEILOLI娃娃機，正常運行中
    GOING_TO_OTA = 5      # 接收到要OTA，但還沒完成OTA
    UNEXPECTED_STATE = -1

# 定義狀態機類別
class MainStateMachine:
    def __init__(self):
        self.state = MainStatus.NONE_WIFI
        # 以下執行"狀態機初始化"相應的操作
        print('Init, MainStatus: NONE_WIFI')
        
    def transition(self, action):
        if action == 'WiFi is disconnect':
            self.state = MainStatus.NONE_WIFI
            # 以下執行"未連上WiFi後"相應的操作
            print('Action: WiFi is disconnect, MainStatus: NONE_WIFI')
            
        elif self.state == MainStatus.NONE_WIFI and action == 'WiFi is OK':
            self.state = MainStatus.NONE_MQTT
            # 以下執行"連上WiFi後"相應的操作
            print('Action: WiFi is OK, MainStatus: NONE_MQTT')
            
        elif self.state == MainStatus.NONE_INTERNET and action == 'Internet is OK':
            self.state = MainStatus.NONE_MQTT
            # 以下執行"連上Internet後"相應的操作
            print('Action: Internet is OK, MainStatus: NONE_MQTT')
            
        elif self.state == MainStatus.NONE_MQTT and action == 'MQTT is OK':
            self.state = MainStatus.NONE_FEILOLI
            # 以下執行"連上MQTT後"相應的操作
            print('Action: MQTT is OK, MainStatus: NONE_FEILOLI')

            
        elif self.state == MainStatus.NONE_FEILOLI and action == 'FEILOLI is OK':
            self.state = MainStatus.STANDBY_FEILOLI
            # 以下執行"連上FEILOLI娃娃機後"相應的操作
            print('Action: FEILOLI is OK, MainStatus: STANDBY_FEILOLI')

        else:
            print('Invalid action:', action, 'for current state:', self.state)    
    
import ujson
# 定義資料類別
class ClawData:
    sales = {
        "Epayplaytimes": 0,
        "Coinplaytimes": 0,
        "Giftplaytimes": 0,
        "GiftOuttimes": 0,
        "Freeplaytimes": 0,
        "time": 0
    } 
    status = {
        "status":0,
        "time": 0
    }


class InternetData:
    def __init__(self):
        self.ip_address = ""
        self.mac_address = ""
    
from umqtt.simple import MQTTClient
import utime, time, network
def connect_wifi():
#     wifi_ssid = 'propsky'
#     wifi_password = '42886178sky'
    wifi_ssid = 'paypc'
    wifi_password = 'abcd1234'
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(wifi_ssid, wifi_password)
    print('Start to connect WiFi')
    while True:
        for i in range(20):
            print('Try to connect WiFi in {}s'.format(i))
            utime.sleep(1)
            if wifi.isconnected():
                break
        if wifi.isconnected():
            print('WiFi connection OK!')
            print('Network Config=', wifi.ifconfig())
            connect_internet_data = InternetData()
            connect_internet_data.ip_address = wifi.ifconfig()[0]
            tmp_mac_address = wifi.config('mac')
            connect_internet_data.mac_address = ''.join(['{:02X}'.format(byte) for byte in tmp_mac_address])
            return connect_internet_data
        else:
            print('WiFi connection Error')
            for i in range(30, -1, -1):
                print("倒數{}秒後重新連線WiFi".format(i))
                time.sleep(1)

def connect_mqtt():
    mq_server = '172.104.127.68'
    mq_id = 'esp00001'
    mq_topic = b'cardid/token/sales'
    mq_user = 'myuser'
    mq_pass = 'propskymqtt'
    while True:
        try:
            mqClient = MQTTClient(mq_id, mq_server, user=mq_user, password=mq_pass)
            mqClient.connect()
            print('MQTT Broker connection OK!')
            return mqClient
        except Exception as e:
            print("MQTT Broker connection failed:", e)
            for i in range(10, -1, -1):
                print("倒數{}秒後重新連線MQTT Broker".format(i))
                time.sleep(1)
                       
def publish_data(mqClient, topic, data):
    try:
        mq_message = ujson.dumps(data)
        print("mq_message topic:", topic)
        print("mq_message data(JSON):", mq_message)
        mqClient.publish(topic, mq_message)
        print("MQTT Publish Successful")
    except Exception as e:
        print("MQTT Publish Error:", e)


class KindFEILOLIcmd:
    Ask_Machine_status = 210
    Send_Machine_reboot = 215
    Send_Machine_shutdown = 216
    Send_Payment_countdown_Or_fail = 231
#     Send_Starting_games = 220
    Send_Starting_once_game = 221
    Ask_Transaction_account = 321
    Ask_Coin_account = 322
    Ask_Machine_setting = 431

# 发送封包給娃娃機的副程式
FEILOLI_packet_id = 0
def uart_FEILOLI_send_packet(FEILOLI_cmd):
    global FEILOLI_packet_id
    FEILOLI_packet_id = (FEILOLI_packet_id+1) % 256
    if FEILOLI_cmd == KindFEILOLIcmd.Ask_Machine_status:
        uart_send_packet = bytearray([0xBB, 0x73, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
                                      0x00, 0x00, 0x00, 0x00, 0x00, FEILOLI_packet_id, 0x00, 0xAA])
    elif FEILOLI_cmd == KindFEILOLIcmd.Send_Machine_reboot:
        uart_send_packet = bytearray([0xBB, 0x73, 0x01, 0x01, 0x05, 0x00, 0x00, 0x00,
                                      0x00, 0x00, 0x00, 0x00, 0x00, FEILOLI_packet_id, 0x00, 0xAA])
    elif FEILOLI_cmd == KindFEILOLIcmd.Send_Machine_shutdown:
        pass
    elif FEILOLI_cmd == KindFEILOLIcmd.Send_Payment_countdown_Or_fail:
        pass
    elif FEILOLI_cmd == KindFEILOLIcmd.Send_Starting_once_game:
        uart_send_packet = bytearray([0xBB, 0x73, 0x01, 0x02, 0x01, 0x01, 0x00, 0x00,
                                      0x00, 0x00, 0x00, 0x00, 0x00, FEILOLI_packet_id, 0x00, 0xAA])
    elif FEILOLI_cmd == KindFEILOLIcmd.Ask_Transaction_account:
        pass
    if uart_send_packet[13] == FEILOLI_packet_id:
        for i in range(2,14):
            uart_send_packet[15] ^= uart_send_packet[i]
        uart_FEILOLI.write(uart_send_packet)
        print("Sent packet to 娃娃機:    ", uart_send_packet)
    else:
        print("FEILOLI_cmd 是無效的指令:", FEILOLI_cmd)


# 定義最大佇列容量
# MAX_RX_QUEUE_SIZE = 200
# 建立佇列
uart_FEILOLI_rx_queue = []

# 從佇列中讀取資料的任務
def uart_FEILOLI_recive_packet_task():
    while True:
        if uart_FEILOLI.any():
            receive_data = uart_FEILOLI.readline()
            uart_FEILOLI_rx_queue.extend(receive_data)
            while len(uart_FEILOLI_rx_queue)>=16:
#                 print("uart_FEILOLI_rx_queue:", bytearray(uart_FEILOLI_rx_queue))
                uart_recive_packet = bytearray(16)
                uart_recive_packet[0] = uart_FEILOLI_rx_queue.pop(0)  # 從佇列中取出第一個字元
                if uart_recive_packet[0]==0x2D:
                    uart_recive_packet[1] = uart_FEILOLI_rx_queue.pop(0)  # 從佇列中取出下一個字元
                    if uart_recive_packet[1]==0x8A:
                        uart_recive_check_sum = 0xAA
                        for i in range(2,16):
                            uart_recive_packet[i] = uart_FEILOLI_rx_queue.pop(0)
                            uart_recive_check_sum ^= uart_recive_packet[i]
                        if uart_recive_check_sum == 0x00:   #check sum算完正確，得到正確16Byte
                            print("Recive packet from 娃娃機:", uart_recive_packet)
                            # 在這裡進行packet的處理
                            utime.sleep_ms(100)  # 休眠一小段時間，避免過度使用CPU資源
                            continue
                print("佇列收到無法對齊的封包:", bytearray(uart_recive_packet))
        utime.sleep_ms(100)  # 休眠一小段時間，避免過度使用CPU資源


# 定義server_check計時器回調函式
def server_check_timer_callback(timer):
    print("Checking WiFi status...")
    # 之後要檢查 WiFi狀態的程式碼
    
    print("Checking network status...")
    # 之後要檢查網路狀態的程式碼
    
    print("Checking MQTT status...")
    # 之後要檢查 MQTT 狀態的程式碼
    
# 定義claw_check計時器回調函式
def claw_check_timer_callback(timer):
    print("Checking 娃娃機 status...")
    uart_FEILOLI_send_packet(KindFEILOLIcmd.Ask_Machine_status)
    
    # 之後要檢查 娃娃機 狀態的程式碼


#------------------ 初始化 ------------------ 

# 創建狀態機
now_main_state = MainStateMachine()

# 創建娃娃機資料
claw1 = ClawData()

# UART配置
uart_FEILOLI = machine.UART(2, baudrate=19200, tx=17, rx=16)

# 創建計時器物件
server_check_timer = machine.Timer(-1)
claw_check_timer = machine.Timer(-1)

# 設定UART中斷
# uart_FEILOLI.irq(trigger=UART.RX_ANY, handler=uart_FEILOLI_rx_interrupt_handler)

# 建立並執行uart_FEILOLI_recive_packet_task
_thread.start_new_thread(uart_FEILOLI_recive_packet_task, ())


TIMER_INTERVAL = 50000  # 設定計時器間隔（單位：毫秒）
# 設定server_check計時器的間隔和回調函式
server_check_timer.init(period=TIMER_INTERVAL, mode=machine.Timer.PERIODIC, callback=server_check_timer_callback)
TIMER_INTERVAL = 10000  # 設定計時器間隔（單位：毫秒）
claw_check_timer.init(period=TIMER_INTERVAL, mode=machine.Timer.PERIODIC, callback=claw_check_timer_callback)



while True:
        if now_main_state.state == MainStatus.NONE_WIFI:
            print('now_main_state: WiFi is disconnect')
            time.sleep(1)
            my_internet_data = connect_wifi()
            # 打印 myInternet 内容
            print("My IP Address:", my_internet_data.ip_address)
            print("My MAC Address:", my_internet_data.mac_address)
            now_main_state.transition('WiFi is OK')

        elif now_main_state.state == MainStatus.NONE_INTERNET:
            print('now_main_state: WiFi is OK')
            time.sleep(1)
            now_main_state.transition('Internet is OK')
            
        elif now_main_state.state == MainStatus.NONE_MQTT:
            print('now_main_state: Internet is OK')
            time.sleep(1)
            mqClient = connect_mqtt()
            if mqClient is not None:
                now_main_state.transition('MQTT is OK')

        elif now_main_state.state == MainStatus.NONE_FEILOLI:
            print('now_main_state: MQTT is OK')
            time.sleep(30)
            
            macid = my_internet_data.mac_address
            mq_topic = macid + '/token/sales'
            claw1.sales["Coinplaytimes"] +=1
            claw1.sales["time"] = utime.time()
            mq_json_str = ujson.dumps(claw1.sales)
            publish_data(mqClient, mq_topic, mq_json_str)
            
#             uart_FEILOLI_send_packet(KindFEILOLIcmd.Send_Starting_once_game)
            uart_FEILOLI_send_packet(KindFEILOLIcmd.Send_Machine_reboot)
    
            
        elif now_main_state.state == MainStatus.STANDBY_FEILOLI:
            print('now_main_state: FEILOLI is OK')
            time.sleep(1)


        else:
            print('Invalid action! now_main_state:', now_main_state.state)
            time.sleep(10)  # 延遲 10 秒