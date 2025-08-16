# push check list 

1. 有在小卡和娃娃機上測試過，確定新功能是否正常
2. 更新Data_Collection_Main.py第一行的版本號
3. 檢查sourceFiles內的檔案和程式碼與上一版的差異，判斷是否合理
4. 讓外面小卡可以OTA更新到最新程式碼：將sourceFiles檔案複製到releaseFiles\latestVersion
5. 檢查releaseFiles\latestVersion內的檔案和程式碼與上一版的差異，判斷是否合理
6. latestVersion資料夾壓縮成SPHP1_Vxxxxx.zip，保存備份放進releaseFiles資料夾，可以參考以前的SPHP1_V1.00d.zip
7. 修改README.md的code-change list，參考之前的格式，新增這次新版的修改內容：
    **年/月/日_硬體架構版本_韌體版本, 發布人**
    1. 修改項目1
    a. 修改項目1.a
    b. 修改項目1.b
    2. 修改項目2
    3. 修改項目3
    * Based on 案子版本 年/月/日_硬體架構版本_韌體版本, 發布人
    ---
8. 第7點除了Base on那行以外，第一行日期版本+內容都複製填入commit，然後即可以下push
9. 打開Github網站的這個案子，判斷這次的commit變動內容是否合理



[返回主頁](README.md)