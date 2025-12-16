# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這是一個 ESP32 MicroPython 專案，用於開心小卡（Happy Collector）支付板，整合娃娃機與電子支付功能。

### 硬體平台
- **目標硬體**: ESP32 開發板
- **硬體版本**: SPHP_HWv1 (開心小卡硬體改成宏碁卡機使用)
- **當前韌體版本**: SPHP1_V1.01b
- **主要差異**: SPHP1_V1.00C 和 HP_V1.00c 的差異只有 EPAY_EN 的 IO Define 不一樣

### 程式碼規範
- **檔案編碼**: UTF-8
- **行尾字元**: LF (Unix style)
- **模組使用**: 使用 `uos` 而非 `os` (符合 MicroPython 標準)

### 韌體架構

#### 啟動流程
1. **main.py** - 系統初始化與啟動程式
   - LCD 顯示初始化 (ST7735)
   - WiFi 連線管理 (支援 wifimgr 或 UDP 配置模式)
   - NTP 時間同步 (台灣 NTP server)
   - OTA 更新檢查 (透過 senko.py 從 GitHub 下載)
   - 執行主程式 Data_Collection_Main.py

2. **Data_Collection_Main.py** - 主要業務邏輯
   - 狀態機管理 (MainStateMachine)
   - MQTT 通訊 (訂閱/發佈)
   - UART 娃娃機通訊 (FEILOLI 協議)
   - GPIO 中斷處理 (卡機 PAYOUT 信號)
   - 定時器與執行緒任務
   - LCD 資訊顯示更新

#### 核心狀態機 (MainStatus)
```
NONE_WIFI (0) → NONE_INTERNET (1) → NONE_MQTT (2) → NONE_FEILOLI (3) → STANDBY_FEILOLI (4) ⇄ WAITING_FEILOLI (5)
```

## 目錄結構

```
smartpay/
├── sourceFiles/          # 開發中的原始碼
│   ├── main.py          # 系統啟動程式
│   ├── Data_Collection_Main.py  # 主程式邏輯
│   ├── BN165DKBDriver.py        # 74HC165 鍵盤驅動
│   ├── wifimgr.py       # WiFi 管理模組
│   ├── senko.py         # OTA 更新模組
│   ├── ntptime.py       # NTP 時間同步
│   ├── token.dat        # MQTT token (36 字元 UUID)
│   └── wifi.dat         # WiFi 設定檔
│
├── releaseFiles/
│   ├── latestVersion/   # 最新版本 (用於 OTA)
│   └── SPHP1_Vxxxx/     # 版本備份資料夾
│
├── docs/                 # 文檔目錄
│   └── 娃娃機通訊協議.md  # ReceivedClawData 欄位對照文檔
│
├── README.md            # 版本變更歷史
└── push-check-list.md   # 發布檢查清單
```

## 開發工作流程

### 修改程式碼
1. 在 `sourceFiles/` 目錄修改程式碼
2. 在小卡和娃娃機上測試新功能
3. 更新 `Data_Collection_Main.py` 第一行的 `VERSION` 變數

### 發佈新版本
依照 `push-check-list.md` 的步驟：

1. 測試功能是否正常
2. 更新版本號 (在 Data_Collection_Main.py 第一行)
3. 檢查 sourceFiles 與上一版的差異
4. 複製 sourceFiles 到 releaseFiles/latestVersion (供 OTA 使用)
5. 壓縮 latestVersion 為 SPHP1_Vxxxxx.zip 備份（若需要 OTA 發布）
6. 更新 README.md 的版本歷史記錄
7. 建立 git commit (格式: `年/月/日_硬體版本_韌體版本, 發布人`)
8. 確認 GitHub commit 內容合理

**注意**: 若該版本不進行 OTA 發布，可跳過壓縮備份步驟

### Commit 訊息格式
```
**2025/12/16_SPHP1_V1.01b, Thomas**
1. Data_Collection_Main.py 改版，細項如下
  a. ReceivedClawData 類別註解簡化與文檔分離
     - 減少行數 38 行 (從 68 行縮短到 30 行)，字元數減少約 3450 字元
     - 詳細對應關係移至獨立文檔 docs/娃娃機通訊協議.md
  b. uart_FEILOLI_send_packet 函數重構與優化
     - 減少程式碼重複，字元數減少約 380 字元
  c. new_sales_flag 變數新增（MQTT 發布優化）
  ... (以下省略)
```

## OTA (Over-The-Air) 更新機制

### OTA 觸發流程
1. 透過 MQTT 發送 `fota` 指令，包含 `file_list` 和 `password`
2. 系統在根目錄建立 `otalist.dat` 檔案
3. 重開機後 main.py 檢測到 `otalist.dat`
4. 使用 senko.py 從 GitHub `releaseFiles/latestVersion` 下載檔案
5. 更新完成後刪除 `otalist.dat` 並重開機

### OTA 設定
- **GitHub Repository**: `pc0808f/smartpay`
- **Branch**: `SPHP_HWv1`
- **Working Directory**: `releaseFiles/latestVersion`
- **Password**: `c0b82a2c-4b03-42a5-92cd-3478798b2a90`

## 重要技術細節

### MQTT 通訊
- **Server**: `happycollect.propskynet.com`
- **認證**: myuser / propskymqtt
- **Client ID**: MAC Address
- **Topic 格式**: `{MAC_ADDRESS}/{TOKEN}/...`
- **主要 Topics**:
  - `/commands` - 接收控制指令
  - `/fota` - 接收 OTA 更新指令
  - `/sales` - 發送銷售資料 (每 3 分鐘)
  - `/status` - 發送狀態資料 (每 3 分鐘)
  - `/commandack` - 發送指令回應
  - `/fotaack` - 發送 OTA 確認

### UART 娃娃機通訊
- **UART2**: TX=Pin(17), RX=Pin(16), Baudrate=19200
- **協議**: FEILOLI 16-byte 封包格式
- **Header**: 0xBB 0x73
- **Trailer**: Checksum + 0xAA
- **接收格式**: 0x2D 0x8A + 14 bytes data + checksum
- **執行緒**: 使用獨立執行緒處理 UART 接收

### GPIO 配置
- **Pin 19**: GPO_CardReader_EPAY_EN (卡機支付啟用)
- **Pin 18**: GPIO_CardReader_PAYOUT (卡機支付訊號，中斷)
- **Pin 27**: LCD_EN (LCD 啟用)
- **Pin 14**: SPI SCK (LCD)
- **Pin 13**: SPI MOSI (LCD)
- **Pin 4**: LCD DC
- **Pin 15**: LCD CS
- **Pin 32**: 74HC165 PL
- **Pin 33**: 74HC165 Q7

### WiFi 配置模式
系統支援兩種 WiFi 配置方式：

1. **wifimgr 模式**: 使用 wifi.dat 儲存的 SSID/密碼
2. **UDP 配置模式**:
   - 按住 SW4 或 ESP32_TXD2_FEILOLI 拉低
   - 連接預設 WiFi "Sam" / "0928666624"
   - 監聽 UDP port 1234
   - 接收新的 WiFi 設定並儲存到 wifi.dat

### 記憶體管理
- 定期執行 `gc.collect()` 釋放記憶體
- 使用 `del` 刪除不需要的模組
- 使用流式處理避免大檔案佔用記憶體 (senko.py)
- 監控 `gc.mem_free()` 確保記憶體充足

### MicroPython 模組使用
- 使用 `uos` 取代標準 Python 的 `os` 模組
- 常用函式：
  - `uos.listdir()` - 列出目錄內容
  - `uos.stat()` - 取得檔案資訊
  - `uos.remove()` - 刪除檔案
  - `uos.rename()` - 重新命名檔案
- 所有檔案操作都應使用 `try-except OSError` 進行錯誤處理

### Watchdog Timer
- **主程式**: 10 分鐘 timeout (1000*60*10)
- **main.py**: 5 分鐘 timeout (1000*60*5)
- 透過 `WDT_feed_flag` 從執行緒觸發主迴圈餵狗

### 執行緒架構
1. **uart_FEILOLI_recive_packet_task**: UART 接收處理
2. **three_timer_task**: 每秒執行的定時任務
   - claw_check_timer_callback (每 10 秒)
   - LCD_update_timer_callback (每秒)
   - server_check_timer_callback (每秒)
3. **Timer(0)**: server_report_timer (每 10 秒)

## 除錯與測試

### 測試快速設定
- 修改 `server_report_period = 1` 可將 MQTT 回報週期從 3 分鐘縮短到 10 秒

### 常見問題
1. **記憶體不足**: 檢查 gc.collect() 是否正常執行，確認沒有循環引用
2. **OTA 失敗**: 檢查 GitHub 連線、檔案路徑、senko.py 流式下載
3. **娃娃機無法連線**: 檢查 UART 接線、封包格式、checksum 計算
4. **MQTT 斷線**: 檢查 WiFi 連線、MQTT 憑證、網路穩定性
5. **Interrupt WDT Timeout (看門狗超時重開機)**:
   - **現象**: `Guru Meditation Error: Core 0 panic'ed (Interrupt wdt timeout on CPU0)`
   - **常見原因**: PAYOUT (Pin 18) 硬體接線問題導致 GPIO 中斷頻繁觸發
   - **檢查方式**:
     - 查看 log 是否有大量 `PAYOUT收到中斷和變化` 訊息
     - 檢查是否在短時間內出現數十次中斷
   - **解決方法**: 檢查並修正 Pin 18 硬體接線（可能是接觸不良或雜訊干擾）
   - **記錄時間**: 2025/12/2

## 特殊注意事項

### 程式碼優化原則
- 刪減註解以減少程式碼長度 (為了 OTA 記憶體限制)
- 詳細註解移至獨立文檔檔案 (如 `docs/娃娃機通訊協議.md`)
- 使用 README.md 當作 code-change list
- 移除舊的測試程式碼和無用註解

### 不可修改的檔案
- 不可刪除 `main.py` (遠端指令會拒絕刪除)

### Token 檔案
- token.dat 必須是 36 字元的 UUID
- 程式會檢查長度，不正確會進入無限迴圈

### 分支管理
- **主分支**: main
- **當前分支**: SPHP_HWv1 (宏碁卡機硬體版本)
- 兩個硬體版本會同步修改新功能

### 敏感檔案管理
- **不納入版本控制的檔案**: token.dat、wifi.dat
- 這些檔案包含敏感資訊（MQTT token、WiFi 密碼），已在 `.gitignore` 中設定不追蹤
- 本地開發需保留這些檔案，但不會上傳到 GitHub
- OTA 更新時這些檔案不會被覆蓋，保持設備獨立的設定

### 已知未實作功能
參考 README.md to-be-do list：

1. **MQTT clawstartgame 指令的參數傳遞** (README 第 146 行)
   - 位置: `Data_Collection_Main.py` Line 206-211
   - 現況: 已接收 `epays` 和 `freeplays` 參數，但尚未傳遞給娃娃機
   - 計畫: 需要實作將遊戲次數傳遞給 FEILOLI 協議的機制

2. **FEILOLI 指令未完成項目**
   - `Send_Machine_shutdown` (Line 436) - 關機指令（已註解）
   - `Send_Payment_countdown_Or_fail` (Line 437) - 支付倒數/失敗指令（已註解）

3. **ReceivedClawData 類別文檔化** (已完成於 V1.01b)
   - 位置: `docs/娃娃機通訊協議.md`
   - 說明: 記錄 ReceivedClawData 類別欄位與 FEILOLI 協議的對應關係
   - 目的: 減少程式碼註解長度，便於 OTA 更新
