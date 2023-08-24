VERSION = "V1.04g"

import machine
import binascii
from machine import UART
from umqtt.simple import MQTTClient
import _thread
import utime, time
import network
import ujson
from dr.st7735.st7735_4bit import ST7735
from machine import SPI, Pin
import gc

#Based on 2023/8/17_V1.04f, Sam

# 定義狀態類型
class MainStatus:
    NONE_WIFI = 0       # 還沒連上WiFi
    NONE_INTERNET = 1   # 連上WiFi，但還沒連上外網      現在先不做這個判斷
    NONE_MQTT = 2       # 連上外網，但還沒連上MQTT Broker
    NONE_FEILOLI = 3    # 連上MQTT，但還沒連上FEILOLI娃娃機
    STANDBY_FEILOLI = 4 # 連上FEILOLI娃娃機，正常運行中
    WAITING_FEILOLI = 5 # 連上FEILOLI娃娃機，等待娃娃機回覆
    GOING_TO_OTA = 6    # 接收到要OTA，但還沒完成OTA
    UNEXPECTED_STATE = -1


# 定義狀態機類別
class MainStateMachine:

    def __init__(self):
        self.state = MainStatus.NONE_WIFI
        # 以下執行"狀態機初始化"相應的操作
        print('\n\rInit, MainStatus: NONE_WIFI')
        global main_while_delay_seconds
        main_while_delay_seconds = 1
        unique_id_hex = binascii.hexlify(machine.unique_id()).decode().upper()

        dis.fill(color.BLACK)
        dis.draw_text(spleen16, 'Happy Collector', 0, 0, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0)
        dis.fgcolor = color.RED     # 设置前景颜色为紅色
        dis.bgcolor = color.WHITE   # 设置背景颜色为黑色
        dis.draw_text(spleen16, unique_id_hex, 5, 8 * 16 + 5, 1.3, dis.fgcolor, dis.bgcolor, -1, True, 0, 0) 
        dis.dev.show()
        dis.fgcolor = color.WHITE   # 设置前景颜色为白色
        dis.bgcolor = color.BLACK   # 设置背景颜色为黑色
        dis.draw_text(spleen16, 'IN:--------', 0, 1 * 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
        dis.draw_text(spleen16, 'OUT:--------', 0, 2 * 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
        dis.draw_text(spleen16, 'EP:--------', 0, 3 * 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
        dis.draw_text(spleen16, 'FP:--------', 0, 4 * 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
        dis.draw_text(spleen16, 'ST:--', 0, 5 * 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
        dis.draw_text(spleen16, 'Time:mm/dd hh:mm', 0, 6 * 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0)
        dis.draw_text(spleen16, 'Wifi:-----', 0, 7 * 16, 1, dis.fgcolor, dis.bgcolor, 0, True, 0, 0) 
        dis.dev.show()

    def transition(self, action):
        global main_while_delay_seconds
        if action == 'WiFi is disconnect':
            self.state = MainStatus.NONE_WIFI
            # 以下執行"未連上WiFi後"相應的操作
            print('\n\rAction: WiFi is disconnect, MainStatus: NONE_WIFI')
            main_while_delay_seconds = 1
            dis.draw_text(spleen16, 'dis  ', 5 * 8, 7 * 16, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0) #顯示wifi和MQTT狀態
            dis.dev.show()

        elif self.state == MainStatus.NONE_WIFI and action == 'WiFi is OK':
            self.state = MainStatus.NONE_INTERNET
            # 以下執行"連上WiFi後"相應的操作
            print('\n\rAction: WiFi is OK, MainStatus: NONE_INTERNET')
            main_while_delay_seconds = 1
            dis.draw_text(spleen16, 'dis  ', 5 * 8, 7 * 16, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0) #顯示wifi和MQTT狀態
            dis.dev.show()

        elif self.state == MainStatus.NONE_INTERNET and action == 'Internet is OK':
            self.state = MainStatus.NONE_MQTT
            # 以下執行"連上Internet後"相應的操作
            print('\n\rAction: Internet is OK, MainStatus: NONE_MQTT')
            main_while_delay_seconds = 1
            dis.draw_text(spleen16, 'error', 5 * 8, 7 * 16, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0) #顯示wifi和MQTT狀態
            dis.dev.show()

        elif self.state == MainStatus.NONE_MQTT and action == 'MQTT is OK':
            self.state = MainStatus.NONE_FEILOLI
            # 以下執行"連上MQTT後"相應的操作
            print('\n\rAction: MQTT is OK, MainStatus: NONE_FEILOLI')
            main_while_delay_seconds = 10
            dis.draw_text(spleen16, 'ok   ', 5 * 8, 7 * 16, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0) #顯示wifi和MQTT狀態
            dis.draw_text(spleen16,  "%02d" % 99, 3 * 8, 5 * 16, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0) #顯示娃娃機狀態
            dis.dev.show()

        elif (self.state == MainStatus.NONE_FEILOLI or self.state == MainStatus.WAITING_FEILOLI) and action == 'FEILOLI UART is OK':
            self.state = MainStatus.STANDBY_FEILOLI
            # 以下執行"連上FEILOLI娃娃機後"相應的操作
            print('\n\rAction: FEILOLI UART is OK, MainStatus: STANDBY_FEILOLI')
            main_while_delay_seconds = 10

        elif self.state == MainStatus.STANDBY_FEILOLI and action == 'FEILOLI UART is waiting':
            self.state = MainStatus.WAITING_FEILOLI
            # 以下執行"等待FEILOLI娃娃機後"相應的操作
            print('\n\rAction: FEILOLI UART is waiting, MainStatus: WAITING_FEILOLI')
            main_while_delay_seconds = 10

        elif self.state == MainStatus.WAITING_FEILOLI and action == 'FEILOLI UART is not OK':
            self.state = MainStatus.NONE_FEILOLI
            # 以下執行"等待失敗後"相應的操作
            print('\n\rAction: FEILOLI UART is not OK, MainStatus: NONE_FEILOLI')
            main_while_delay_seconds = 10    
            dis.draw_text(spleen16,  "%02d" % 99, 3 * 8, 5 * 16, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0) #顯示娃娃機狀態
            dis.dev.show()

        elif (self.state == MainStatus.NONE_FEILOLI or self.state == MainStatus.STANDBY_FEILOLI or self.state == MainStatus.WAITING_FEILOLI) and action == 'MQTT is not OK':
            self.state = MainStatus.NONE_MQTT
            # 以下執行"MQTT失敗後"相應的操作
            print('\n\rAction: MQTT is not OK, MainStatus: NONE_MQTT')
            main_while_delay_seconds = 1
            dis.draw_text(spleen16, 'error', 5 * 8, 7 * 16, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0) #顯示wifi和MQTT狀態
            dis.dev.show()

        else:
            print('\n\rInvalid action:', action, 'for current state:', self.state)
            main_while_delay_seconds = 1
 
# 開啟 token 檔案
def load_token():
    global token
    try:
        with open('token.dat') as f:
            token = f.readlines()[0].strip()
        print('Get token:', token)
        len_token = len(token)
        if len_token != 36:
            while True:
                print('token的長度不對:', len_token)
                time.sleep(30)
    except Exception as e:
        print("Open token.dat failed:", e)
        while True:
            print('遺失 token 檔案')
            time.sleep(30)


def connect_wifi():
    wifi = network.WLAN(network.STA_IF)

    if not wifi.config('essid'):
        print('沒有經過wifimgr.py')
        wifi_ssid = 'paypc'
        wifi_password = 'abcd1234'
        wifi.active(True)
        wifi.connect(wifi_ssid, wifi_password)

    print('Start to connect WiFi, SSID : {}'.format(wifi.config('essid')))

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
            print('WiFi({}) connection Error'.format(wifi.config('essid')))
            for i in range(30, -1, -1):
                print("倒數{}秒後重新連線WiFi".format(i))
                time.sleep(1)


class InternetData:
    def __init__(self):
        self.ip_address = ""
        self.mac_address = ""


def connect_mqtt():
    mq_server = 'happycollect.propskynet.com'
    mq_id = my_internet_data.mac_address
    mq_user = 'myuser'
    mq_pass = 'propskymqtt'
    while True:
        try:
            mq_client = MQTTClient(mq_id, mq_server, user=mq_user, password=mq_pass)
            mq_client.connect()
            print('MQTT Broker connection OK!')
            return mq_client
        except Exception as e:
            print("MQTT Broker connection failed:", e)
            for i in range(10, -1, -1):
                print("倒數{}秒後重新連線MQTT Broker".format(i))
                time.sleep(1)


def subscribe_MQTT_claw_recive_callback(topic, message):
    print("MQTT Subscribe recive data")
    print("MQTT Subscribe topic:", topic)
    print("MQTT Subscribe data(JSON_str):", message)
    try:
        data = ujson.loads(message)
        print("MQTT Subscribe data:", data)

        macid = my_internet_data.mac_address
        mq_topic = macid + '/' + token
        if topic.decode() == (mq_topic + '/fota'):
            otafile = 'otalist.dat'
            if ('file_list' in data) and ('password' in data):
                if data['password'] == 'c0b82a2c-4b03-42a5-92cd-3478798b2a90':
                    #print("password checked")
                    publish_MQTT_claw_data(claw_1, 'fotaack')                    
                    with open(otafile, "w") as f:
                        f.write(''.join(data['file_list']))
                    print("otafile 輸出完成，即將重開機...")
                    time.sleep(3)
                    machine.reset()
                else:
                    print("password failed")
        elif topic.decode() == (mq_topic + '/commands'):
            if data['commands'] == 'ping':
                publish_MQTT_claw_data(claw_1, 'commandack-pong')
            elif data['commands'] == 'version':
                publish_MQTT_claw_data(claw_1, 'commandack-version')
            elif data['commands'] == 'clawreboot':
                if 'state' in data:
                    publish_MQTT_claw_data(claw_1, 'commandack-clawreboot',data['state'])
                    uart_FEILOLI_send_packet(KindFEILOLIcmd.Send_Machine_reboot)
                # else:
                #     publish_MQTT_claw_data(claw_1, 'commandack-clawreboot')
                #     uart_FEILOLI_send_packet(KindFEILOLIcmd.Send_Machine_reboot)
            elif data['commands'] == 'clawstartgame':
                if 'state' in data:
                    publish_MQTT_claw_data(claw_1, 'commandack-clawstartgame',data['state'])
                    epays=data['epays'] 
                    freeplays=data['freeplays']
                    uart_FEILOLI_send_packet(KindFEILOLIcmd.Send_Starting_once_game)                                       
                # publish_MQTT_claw_data(claw_1, 'commandack-clawstartgame')   
                # epays=['epays'] 
                # freeplays=['freeplays']
                # uart_FEILOLI_send_packet(KindFEILOLIcmd.Send_Starting_once_game)                             
    #       elif data['commands'] == 'getstatus':

    except Exception as e:
        print("MQTT Subscribe data to JSON Error:", e)

def subscribe_MQTT_claw_topic():  # MQTT_client暫時固定為mq_client_1
    mq_client_1.set_callback(subscribe_MQTT_claw_recive_callback)
    macid = my_internet_data.mac_address
    mq_topic = macid + '/' + token + '/commands'
    mq_client_1.subscribe(mq_topic)
    print("MQTT Subscribe topic:", mq_topic)
    mq_topic = macid + '/' + token + '/fota'
    mq_client_1.subscribe(mq_topic)
    print("MQTT Subscribe topic:", mq_topic)

def publish_data(mq_client, topic, data):
    try:
        # mq_message = ujson.dumps(data)
        print("MQTT Publish topic:", topic)
        print("MQTT Publish data(JSON_str):", data)
        mq_client.publish(topic, data)
        print("MQTT Publish Successful")
    except Exception as e:
        print("MQTT Publish Error:", e)
        now_main_state.transition('MQTT is not OK')

def publish_MQTT_claw_data(claw_data, MQTT_API_select, para1=""):  # 可以選擇claw_1、claw_2、...，但MQTT_client暫時固定為mq_client_1
    if MQTT_API_select == 'sales':
        WCU_Freeplaytimes = (
                    claw_data.Number_of_Total_games - claw_data.Number_of_Original_Payment - claw_data.Number_of_Coin - claw_data.Number_of_Gift_Payment)
        if WCU_Freeplaytimes < 0:
            WCU_Freeplaytimes = 0
            # 上行是 Thomas 測試
        macid = my_internet_data.mac_address
        mq_topic = macid + '/' + token + '/sales'
        MQTT_claw_data = {
            "Epayplaytimes": claw_data.Number_of_Original_Payment,
            "Coinplaytimes": claw_data.Number_of_Coin,
            "Giftplaytimes": claw_data.Number_of_Gift_Payment,
            "GiftOuttimes":  claw_data.Number_of_Award,
            "Freeplaytimes": WCU_Freeplaytimes,
            "time": utime.time()
        }
    elif MQTT_API_select == 'status':
        macid = my_internet_data.mac_address
        mq_topic = macid + '/' + token + '/status'
        MQTT_claw_data = {
            "status": "%02d" % (claw_data.Error_Code_of_Machine),
            "time":   utime.time()
        }
    elif MQTT_API_select == 'commandack-pong':
        macid = my_internet_data.mac_address
        mq_topic = macid + '/' + token + '/commandack'
        MQTT_claw_data = {
            "ack": "pong",
            "time": utime.time()
        }
    elif MQTT_API_select == 'commandack-version':
        macid = my_internet_data.mac_address
        mq_topic = macid + '/' + token + '/commandack'
        MQTT_claw_data = {
            "ack":  VERSION,
            "time": utime.time()
        }
    elif MQTT_API_select == 'fotaack':
        macid = my_internet_data.mac_address
        mq_topic = macid + '/' + token + '/fotaack'
        MQTT_claw_data = {
            "ack": "OK",
            "time": utime.time()
        }
    elif MQTT_API_select == 'commandack-clawreboot':
        macid = my_internet_data.mac_address
        mq_topic = macid + '/' + token + '/commandack'
        if para1=="" :
            MQTT_claw_data = {
                "ack": "OK",
                "time": utime.time()
            }
        else :
            MQTT_claw_data = {
                "ack": "OK",
                "state" : para1,
                "time": utime.time()
            }            
    elif MQTT_API_select == 'commandack-clawstartgame':
        macid = my_internet_data.mac_address
        mq_topic = macid + '/' + token + '/commandack'
        if para1=="" :
            MQTT_claw_data = {
                "ack": "OK",
                "time": utime.time()
            }
        else :
            MQTT_claw_data = {
                "ack": "OK",
                "state" : para1,
                "time": utime.time()
            }                   
    mq_json_str = ujson.dumps(MQTT_claw_data)
    publish_data(mq_client_1, mq_topic, mq_json_str)


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


class ReceivedClawData:
    def __init__(self):
        self.CMD_Verification_code_and_Card_function = 0    # for 一、通訊說明\回覆修改驗證碼、刷卡功能的指令
        self.Verification_code = bytearray(4)               # for 一、通訊說明\驗證碼
        self.Machine_Code_number = bytearray(2)             # for 一、通訊說明\機台代號
        self.Machine_FW_version = bytearray(2)              # for 一、通訊說明\程式版本
        self.Feedback_Card_function = 0                     # for 一、通訊說明\回覆目前刷卡功能

        self.CMD_Control_Machine = 0                        # for 二、主控制\機台狀態\回覆控制指令 (機台回覆控制代碼)
        self.Status_of_Current_machine = bytearray(2)       # for 二、主控制\機台狀態\機台目前狀況
        self.Time_of_Current_game = 0                       # for 二、主控制\機台狀態\當機台目前狀況[0]為0x10=遊戲開始(未控制搖桿)時，回傳的遊戲時間
        self.Game_amount_of_Player = 0                      # for 二、主控制\機台狀態\玩家遊戲金額(累加金額)
        self.Way_of_Starting_game = 0                       # for 二、主控制\機台狀態\遊戲啟動方式
        self.Cumulation_amount_of_Sale_card = 0             # for 二、主控制\機台狀態\售價小卡顯示用累加金額

        self.Payment_amount_of_This_order = 0               # for 二、主控制\傳送交易資料\此次扣款金額
        self.Number_of_Original_games_to_Start = 0          # for 二、主控制\傳送交易資料\啟動原局數
        self.Number_of_Gift_games_to_Start = 0              # for 二、主控制\傳送交易資料\啟動贈局數
        self.Number_dollars_of_Per_game = 0                 # for 二、主控制\傳送交易資料\每局幾元
        self.Time_of_Payment_countdown_Or_fail = 0          # for 二、主控制\等待刷卡倒數/交易失敗\IPC倒數時間or失敗
        self.CMD_Mode_of_Payment = 0                        # for 二、主控制\回覆遊戲啟動方式(01=電子支付)

        # 未定義                                            # for 二、主控制\套餐設定、參數回報

        self.Number_of_Original_Payment = 0     # for 三、帳目查詢\遠端帳目\悠遊卡支付次數
        self.Number_of_Gift_Payment = 0         # for 三、帳目查詢\遠端帳目\悠遊卡贈送次數
        self.Number_of_Coin = 0                 # for 三、帳目查詢\遠端帳目\投幣次數
        self.Number_of_Award = 0                # for 三、帳目查詢\遠端帳目、投幣帳目\禮品出獎次數
        self.Bank_of_Award_rate = 0             # for 三、帳目查詢\投幣帳目\中獎率銀行
        self.Number_of_Total_games = 0          # for 三、帳目查詢\投幣帳目\總遊戲次數
        # 以下 四、五、六都還沒檢查、還沒逐一順過
        '''
        self.CMD_Item_of_Machine_Setting = 0        # for 四、機台設定查詢
        self.Time_of_game = 0                       # for 四、機台設定查詢\基本設定A
        self.Time_of_Keeping_cumulation = 0         # for 四、機台設定查詢\基本設定A
        self.Time_of_Show_music = 0                 # for 四、機台設定查詢\基本設定A
        self.Enable_of_Midair_Grip = 0              # for 四、機台設定查詢\基本設定A
        self.Amount_of_Award = 0                    # for 四、機台設定查詢\基本設定A
        self.Amount_of_Present_cumulation = 0       # for 四、機台設定查詢\基本設定A
        self.Delay_of_Push_talon = 0                # for 四、機台設定查詢\基本設定B
        self.Delay_of_Suspend_pulled_talon = 0      # for 四、機台設定查詢\基本設定B
        self.Enable_random_of_Pushing_talon = 0     # for 四、機台設定查詢\基本設定B
        self.Enable_random_of_Clamping = 0          # for 四、機台設定查詢\基本設定B
        self.Time_of_Push_talon = 0                 # for 四、機台設定查詢\基本設定B
        self.Time_of_Suspend_and_Pull_talon = 0     # for 四、機台設定查詢\基本

        self.Delay_of_Pull_talon = 0                            # for 四、機台設定查詢\基本設定B
        self.Enable_of_Sales_promotion = 0                      # for 四、機台設定查詢\基本設定C
        self.Which_number_starting_when_Sales_promotion = 0     # for 四、機台設定查詢\基本設定C
        self.Number_of_Strong_grip_when_Sales_promotion = 0     # for 四、機台設定查詢\基本設定C
        self.Value_of_Hi_voltage = 0                    # for 四、機台設定查詢\抓力電壓
        self.Value_of_Mid_voltage = 0                   # for 四、機台設定查詢\抓力電壓
        self.Value_of_Lo_voltage = 0                    # for 四、機台設定查詢\抓力電壓
        self.Distance_of_Mid_voltage_and_Top = 0        # for 四、機台設定查詢\抓力電壓
        self.Hi_voltage_of_Guaranteed_prize = 0         # for 四、機台設定查詢\抓力電壓
        self.Speed_of_Moving_forward = 0                # for 四、機台設定查詢\馬達速度
        self.Speed_of_Moving_back = 0                   # for 四、機台設定查詢\馬達速度
        self.Speed_of_Moving_left = 0                   # for 四、機台設定查詢\馬達速度
        self.Speed_of_Moving_right = 0                  # for 四、機台設定查詢\馬達速度
        self.Speed_of_Moving_up = 0                     # for 四、機台設定查詢\馬達速度
        self.Speed_of_Moving_down = 0                   # for 四、機台設定查詢\馬達速度
        self.RPM_of_All_horizontal_sides = 0            # for 四、機台設定查詢\馬達速度
        self.CMD_State_of_Display = 0           # for 五、悠遊卡功能\維修顯示
        self.X_Value_of_02_State = 0            # for 五、悠遊卡功能\維修顯示
        self.CMD_Backstage_function = 0         # for 五、悠遊卡功能\後台功能
        self.Error_Code_of_IPC_Feedback = 0     # for 五、悠遊卡功能\後台功能
        '''
        self.Error_Code_of_Machine = 0          # for 六、 機台故障代碼表

# 发送封包給娃娃機的副程式
FEILOLI_packet_id = 0


def uart_FEILOLI_send_packet(FEILOLI_cmd):
    global FEILOLI_packet_id
    FEILOLI_packet_id = (FEILOLI_packet_id + 1) % 256
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
        uart_send_packet = bytearray([0xBB, 0x73, 0x02, 0x01, 0x00, 0x00, 0x00, 0x00,
                                      0x00, 0x00, 0x00, 0x00, 0x00, FEILOLI_packet_id, 0x00, 0xAA])
    if uart_send_packet[13] == FEILOLI_packet_id:
        for i in range(2, 14):
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
    global claw_1
    while True:
        if uart_FEILOLI.any():
            receive_data = uart_FEILOLI.readline()
            uart_FEILOLI_rx_queue.extend(receive_data)
            while len(uart_FEILOLI_rx_queue) >= 16:
                #                 print("uart_FEILOLI_rx_queue:", bytearray(uart_FEILOLI_rx_queue))
                uart_recive_packet = bytearray(16)
                uart_recive_packet[0] = uart_FEILOLI_rx_queue.pop(0)  # 從佇列中取出第一個字元
                if uart_recive_packet[0] == 0x2D:
                    uart_recive_packet[1] = uart_FEILOLI_rx_queue.pop(0)  # 從佇列中取出下一個字元
                    if uart_recive_packet[1] == 0x8A:
                        uart_recive_check_sum = 0xAA
                        for i in range(2, 16):
                            uart_recive_packet[i] = uart_FEILOLI_rx_queue.pop(0)
                            uart_recive_check_sum ^= uart_recive_packet[i]
                        if uart_recive_check_sum == 0x00:  # check sum算完正確，得到正確16Byte
                            print("Recive packet from 娃娃機:", uart_recive_packet)
                            ######################  在這裡進行packet的處理  ############################################
                            if uart_recive_packet[2] == 0x81 and uart_recive_packet[3] == 0x01:                 # CMD => 二、主控制\機台狀態
                                claw_1.CMD_Control_Machine = uart_recive_packet[4]                                  # 回覆控制指令 (機台回覆控制代碼)
                                claw_1.Status_of_Current_machine[0] = uart_recive_packet[5]                         # 機台目前狀況
                                claw_1.Status_of_Current_machine[1] = uart_recive_packet[6]                         # 機台目前狀況
                                claw_1.Time_of_Current_game = uart_recive_packet[7]                                 # 當機台目前狀況[0]為0x10=遊戲開始(未控制搖桿)時，回傳的遊戲時間
                                claw_1.Game_amount_of_Player = uart_recive_packet[8] * 256 + uart_recive_packet[9]  # 玩家遊戲金額(累加金額)
                                claw_1.Way_of_Starting_game = uart_recive_packet[10]                                # 遊戲啟動方式
                                claw_1.Cumulation_amount_of_Sale_card = uart_recive_packet[11] * 256 + uart_recive_packet[14]  # 售價小卡顯示用累加金額
                                claw_1.Error_Code_of_Machine = uart_recive_packet[12]                   # 六、 機台故障代碼表
                                print("Recive 娃娃機 : 二、主控制\機台狀態")
                            elif uart_recive_packet[2] == 0x82 and uart_recive_packet[3] == 0x01:               # CMD => 三、 帳目查詢\遠端帳目
                                claw_1.Number_of_Original_Payment = uart_recive_packet[4] * 256 + uart_recive_packet[5]     # 悠遊卡支付次數
                                claw_1.Number_of_Gift_Payment = uart_recive_packet[6] * 256 + uart_recive_packet[7]         # 悠遊卡贈送次數
                                claw_1.Number_of_Coin = uart_recive_packet[8] * 256 + uart_recive_packet[9]                 # 投幣次數
                                claw_1.Number_of_Award = uart_recive_packet[10] * 256 + uart_recive_packet[11]              # 禮品出獎次數
                                claw_1.Error_Code_of_Machine = uart_recive_packet[12]                   # 六、 機台故障代碼表
                                print("Recive 娃娃機 : 三、 帳目查詢\遠端帳目")
                            now_main_state.transition('FEILOLI UART is OK')
                            utime.sleep_ms(100)     # 休眠一小段時間，避免過度使用CPU資源
                            continue
                print("佇列收到無法對齊的封包:", bytearray(uart_recive_packet))
        utime.sleep_ms(100)                         # 休眠一小段時間，避免過度使用CPU資源

server_report_sales_period = 3 * 60  # 3分鐘 = 3*60 單位秒
# server_report_sales_period = 10   # For快速測試
server_report_sales_counter = 0

# 定義server_report計時器回調函式 (每1秒執行1次)
def server_report_timer_callback(timer):
    if now_main_state.state == MainStatus.NONE_FEILOLI or now_main_state.state == MainStatus.STANDBY_FEILOLI or now_main_state.state == MainStatus.WAITING_FEILOLI:
        try:
            # 更新 MQTT Subscribe
            mq_client_1.check_msg()
            #mq_client_1.ping()
        except OSError as e:
            print("WiFi is disconnect")
            now_main_state.transition('WiFi is disconnect')

        global server_report_sales_counter
        server_report_sales_counter = (server_report_sales_counter + 1) % server_report_sales_period
        if server_report_sales_counter == 0:
            publish_MQTT_claw_data(claw_1, 'sales')
            # if claw_1.Error_Code_of_Machine != 0x00 :
            publish_MQTT_claw_data(claw_1, 'status')

# 定義claw_check計時器回調函式
counter_of_WAITING_FEILOLI = 0

def claw_check_timer_callback(timer):
    global counter_of_WAITING_FEILOLI
    if now_main_state.state == MainStatus.NONE_FEILOLI:
        print("Updating 娃娃機 機台狀態 ...")
        uart_FEILOLI_send_packet(KindFEILOLIcmd.Ask_Machine_status)

    elif now_main_state.state == MainStatus.STANDBY_FEILOLI:
        print("Updating 娃娃機 遠端帳目、投幣帳目 ...")
        uart_FEILOLI_send_packet(KindFEILOLIcmd.Ask_Transaction_account)
        # uart_FEILOLI_send_packet(KindFEILOLIcmd.Ask_Coin_account)
        now_main_state.transition('FEILOLI UART is waiting')
        counter_of_WAITING_FEILOLI = 0

    if now_main_state.state == MainStatus.WAITING_FEILOLI:
        counter_of_WAITING_FEILOLI = counter_of_WAITING_FEILOLI + 1
        if counter_of_WAITING_FEILOLI >= 2:
            if counter_of_WAITING_FEILOLI == 2:
                print("Updating 娃娃機 失敗 ...")
                now_main_state.transition('FEILOLI UART is not OK')
            print("Updating 娃娃機 機台狀態 ...")
            uart_FEILOLI_send_packet(KindFEILOLIcmd.Ask_Machine_status)


############################################# 初始化 #############################################

# 開啟 token 檔案
load_token()

# LCD配置
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

# 創建狀態機
now_main_state = MainStateMachine()

# 創建娃娃機資料
claw_1 = ReceivedClawData()

# 創建 MQTT Client 1 資料
mq_client_1 = None

# UART配置
uart_FEILOLI = machine.UART(2, baudrate=19200, tx=17, rx=16)

# 創建計時器物件
server_report_timer = machine.Timer(0)
claw_check_timer = machine.Timer(1)

# 建立並執行uart_FEILOLI_recive_packet_task
_thread.start_new_thread(uart_FEILOLI_recive_packet_task, ())

# 設定server_report計時器的間隔和回調函式
TIMER_INTERVAL = 1000  # 設定1秒鐘 = 1000（單位：毫秒）
server_report_timer.init(period=TIMER_INTERVAL, mode=machine.Timer.PERIODIC, callback=server_report_timer_callback)
TIMER_INTERVAL = 10 * 1000  # 設定10秒鐘 = 10*1000（單位：毫秒）
claw_check_timer.init(period=TIMER_INTERVAL, mode=machine.Timer.PERIODIC, callback=claw_check_timer_callback)

last_time = 0
main_while_delay_seconds = 1
while True:

    utime.sleep_ms(100)
    current_time = time.ticks_ms()
    if (time.ticks_diff(current_time, last_time) >= main_while_delay_seconds * 1000):
        last_time = time.ticks_ms()

        if now_main_state.state == MainStatus.NONE_WIFI:
            print('\n\rnow_main_state: WiFi is disconnect, 開機秒數:', current_time / 1000)

            my_internet_data = connect_wifi()
            # 打印 myInternet 内容
            print("My IP Address:", my_internet_data.ip_address)
            print("My MAC Address:", my_internet_data.mac_address)
            now_main_state.transition('WiFi is OK')

        elif now_main_state.state == MainStatus.NONE_INTERNET:
            print('\n\rnow_main_state: WiFi is OK, 開機秒數:', current_time / 1000)
            now_main_state.transition('Internet is OK')  # 目前不做判斷，狀態機直接往下階段跳轉

        elif now_main_state.state == MainStatus.NONE_MQTT:
            print('now_main_state: Internet is OK, 開機秒數:', current_time / 1000)
            mq_client_1 = connect_mqtt()
            if mq_client_1 is not None:
                subscribe_MQTT_claw_topic()
                now_main_state.transition('MQTT is OK')
            gc.collect()
            print(gc.mem_free())

        elif now_main_state.state == MainStatus.NONE_FEILOLI:
            print('\n\rnow_main_state: MQTT is OK (FEILOLI UART is not OK), 開機秒數:', current_time / 1000)
            gc.collect()
            print(gc.mem_free())

        elif now_main_state.state == MainStatus.STANDBY_FEILOLI:
            print('\n\rnow_main_state: FEILOLI UART is OK, 開機秒數:', current_time / 1000)
            gc.collect()
            print(gc.mem_free())
            dis.draw_text(spleen16,  "%-8d" % claw_1.Number_of_Coin, 3 * 8, 1 * 16, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0)
            dis.draw_text(spleen16,  "%-8d" % claw_1.Number_of_Award, 4 * 8, 2 * 16, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0)
            dis.draw_text(spleen16,  "%-8d" % claw_1.Number_of_Original_Payment, 3 * 8, 3 * 16, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0)
            dis.draw_text(spleen16,  "%-8d" % claw_1.Number_of_Gift_Payment, 3 * 8, 4 * 16, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0)
            dis.draw_text(spleen16,  "%02d" % claw_1.Error_Code_of_Machine, 3 * 8, 5 * 16, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0) #顯示娃娃機狀態
            dis.dev.show()


        elif now_main_state.state == MainStatus.WAITING_FEILOLI:
            print('\n\rnow_main_state: FEILOLI UART is witing, 開機秒數:', current_time / 1000)
            gc.collect()
            print(gc.mem_free())

        else:
            print('\n\rInvalid action! now_main_state:', now_main_state.state)
            print('開機秒數:', current_time / 1000)

    # 获取当前时间戳
    timestamp = utime.time()
    # 转换为本地时间
    local_time = utime.localtime(timestamp)
    # 格式化为 "mm/dd hh:mm" 格式的字符串
    formatted_time = "{:02d}/{:02d} {:02d}:{:02d}".format(local_time[1], local_time[2], local_time[3], local_time[4])
    dis.draw_text(spleen16,  formatted_time, 5 * 8, 6 * 16, 1, dis.fgcolor, dis.bgcolor, -1, True, 0, 0)    #顯示時間
    dis.dev.show()
