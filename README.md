# code-change list

**2025/12/4_SPHP1_V1.01a, Thomas**
1. main.py 程式碼修改
  a. 參考智付小卡類比版，同步成相似的log列印和程式碼運行流程
  b. Import 順序和結構重整
     - 調整 import 順序：將系統模組（utime, uos, machine）放在前面，第三方模組（wifimgr）放在後面
     - 合併重複的 import：from machine import SPI, Pin, WDT 整合成一行
     - 移除重複的 from machine import Pin 宣告
  c. GPIO 配置重新組織
     - 將所有 GPIO 配置移到程式前段統一管理
     - 新增清楚的註解區分不同功能：
       - 卡機端的 TV-1 配置
       - 74HC165 的四個 IO 線配置和 UDP-WiFi 設定板配置
       - LCD 的背光配置
     - GPIO 配置從分散位置（原本 ESP32_TXD2_FEILOLI 和 74HC165 在 line 81-87）移到程式開頭集中管理
  d. WiFi 連線優化
     - UDP WiFi 連線等待時間從 500ms 縮短為 200ms
     - 新增空行改善程式碼可讀性
  e. WDT 初始化調整
     - WDT 初始化移到 utime.sleep(1) 之前，確保看門狗更早啟動
  f. Log 和註解優化
     - WiFi 無法初始化的迴圈中，移除註解 # you shall not pass :D
     - OTA 相關 log 訊息改進：
       - "checking files..." → "OTA checking files..."
       - "No changed-file for OTA!" → "Cannot find new-changed files for OTA, or check error"
     - Exception 處理改進：從 except: 改為 except Exception as e: 並印出錯誤訊息
  g. 記憶體管理優化
     - 在 WiFi 連線成功後新增 gc.collect() 和 print(gc.mem_free())
     - 在 OTA 檢查前新增 gc.collect() 和 print(gc.mem_free())
     - 在 OTA senko 初始化後新增 gc.collect() 和 print(gc.mem_free())
  h. 程式碼格式改善
     - 新增適當的空行分隔不同功能區塊
     - micropython.mem_info() 註解位置調整，改善可讀性
2. Data_Collection_Main.py 程式碼修改
  a. 參考智付小卡類比版，同步成相似的log列印和程式碼運行流程
  b. 狀態機邏輯修正
     - 新增 MainStatus.STANDBY_FEILOLI 狀態下也能接收 'FEILOLI UART is OK' 的處理，避免 UART 執行緒在已經 STANDBY 時收到封包產生錯誤訊息
  c. MQTT 錯誤處理優化
     - 調整如果 MQTT 傳送失敗，就把狀態打回 Wi-Fi 斷線（MainStatus.NONE_WIFI）並執行 mq_client.disconnect()
     - 改進 server_check_timer_callback() 的 MQTT check_msg() 錯誤處理
     - MQTT topic 字串組合優化：在 publish_MQTT_claw_data() 函數中，將 macid + '/' + token 移到函數開頭統一處理，減少重複程式碼
  d. 統一重開機處理機制
     - 新增 safe_reboot() 函數：統一的重開機處理機制，先關卡機電源，等待 3 秒後，下重開機指令
     - MQTT 收到 OTA 指令時，在重開機以前會先關掉刷卡功能
  e. 定期重開機機制
     - 新增定期重開機機制：開機超過 3 天，並且是早上 3 點時，進行重開機
  f. PAYOUT 中斷處理改進
     - 為了防止同樣的準位下，出現非預期的重複列印 log 和中斷處理，PAYOUT 新增 last_value
     - 中斷時會先判斷新值和舊值有沒有改變，若有才會做後續中斷處理
     - PAYOUT 的 last_value 在開機時會先讀取和初始化並印出
  g. 脈衝檢測參數優化
     - 脈衝檢測參數調整：PAYOUT 允許 Low 脈波時間範圍從 50-200ms 放寬到 5-300ms，Hi 持續時間也從 100ms 放寬到 50ms
  h. 時間處理優化
     - 新增 get_uptime_str() 函數：提供開機時間的格式化顯示，格式為「d天 h時 m分 s.ss秒」
     - pulse_time 的時間寬度改用 utime.ticks_diff(time2, time1)，可以避免 utime.ticks_ms() 溢位後的回繞問題
     - pulse_time 的名稱改成 pulse_ms，要和 rising_time(utime.ticks_ms()) 作區別
     - 開機秒數顯示從 utime.ticks_ms() / 1000 ，改成使用 get_uptime_str() 函式來顯示開機時間
     - LCD 顯示時間格式化從 format() 改用更簡潔的 "%02d/%02d %02d:%02d" % 格式
     - 檔案資訊日期格式化從 format() 改用 % 格式
  i. 主迴圈優化
     - 改進 last_time 更新邏輯：從 last_time = utime.ticks_ms() 改為 last_time = current_time，避免重複呼叫
     - gc.collect() 位置調整：從各個狀態內移到主迴圈統一處理（在所有狀態處理完後執行一次）
  j. 程式碼優化與清理
     - 簡化 MQTT publish 重複的程式碼
     - 移除測試用 GPIO 程式碼（GPO_IO21test 和 GPO_IO23test）
     - 刪減各種註解和多餘的註解程式碼區塊，優化程式碼長度
     - 註解更新：將「TV-1QR」改為「TV-1」
* Based on smartpay 2025/12/2_SPHP_V1.00e, Thomas
---
**2025/12/2_SPHP1_V1.00e, Thomas**
1. 統一所有 .py 檔案的行尾字元格式：CRLF → LF
2. 更新模組引用：os → uos (符合 MicroPython 標準)
    - 修改檔案：Data_Collection_Main.py, main.py, senko.py  
3. 此版本暫不發布 OTA 更新，將於下一版本一併測試新版 senko OTA 功能，不會再發生記憶體爆掉
4. 新增 Claude Code 的 CLAUDE.md 專案說明文件
* Based on smartpay 2025/7/29_SPHP_V1.00d, Thomas
---
**2025/7/29_SPHP1_V1.00d, Thomas**
1. 新增Sam寫的ntptime.py
2. 更新Sam寫的senko.py
3. 要再測試新版senko可否就能fota，不會再發生記憶體爆掉
4. 新增to-be-do list和push check list 
* Based on smartpay 2025/3/5_SPHP_V1.00c, Thomas
---
**2025/3/5_SPHP1_V1.00c, Thomas**
1. 以開心小卡硬體改成宏碁卡機使用，正式版第一版
2. SPHP1_V1.00C和HP_V1.00c的差異只有EPAY_EN的IO Define不一樣，兩者之後新版會同步修改
* Based on smartpay 2025/1/20_HP_V1.00c, Thomas
---
 
# to-be-do list
1. 確認OTA以下更新方式是否正常合理
a. 舊->新
b. 新->新
2. 記憶體優化、模組優化，導入新型的wifimgr.py和lcd_manager.py，或是導入其他較省記憶體的方式
3. 整理和簡化Log和註解
4. 可以接受MQTT的epays、freeplays的啟動指令，傳遞遊戲次數
5. main.py 配置系統重構
a. 可配置啟動延遲系統：新增 read_boot_delay() 函數，啟動時間從固定XX秒，改成可配置秒數
b. 支援從config.json配置檔案讀取 boot_delay_sec，預設3秒，包含完整錯誤處理機制
c. 新增系統配置檔案，支援啟動延遲配置 config.json：
{
    "boot_delay_sec": 60
}
6. class ReceivedClawData獨立出另一個md說明檔，可以瘦身程式碼本身