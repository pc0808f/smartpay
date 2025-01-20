# code-change list

**2025/1/20_HP_V1.00b, Thomas**
1. 為了順利OTA，刪減註解，另外使用README.md當作code-change list
* Based on smartpay 2025/1/20_HP_V1.00a, Thomas
---
**2025/1/20_HP_V1.00a, Thomas**
1. 為了讓IO中斷能即時處理，原本的三個timer改用thread來運行
2. thread不能做WDT，因此用flag轉到main loop下清除WDT
3. 為了3分鐘回報sales、status的時間準確性，這部份用timer啟動flag
4. IO中斷有一些測試程式碼，下次可以清掉
5. 刪減註解或用不到的舊程式碼，優化程式碼長度
6. Data_xxx.py會判斷LCD是否有經過main.py初始化，若沒有被初始化過才會做初始化，避免重複執行浪費資源
* Based on smartpay 2024/12/9_HP_V0.03, Thomas
 ---
 