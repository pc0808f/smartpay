# code-change list

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
