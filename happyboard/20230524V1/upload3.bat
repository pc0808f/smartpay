@echo off

REM 檢查是否提供了 COM 參數
IF "%~1"=="" (
    echo need COM Port。
    echo 請提供 COM 參數。
    goto :EOF
)

REM 設定 ampy 工具路徑
SET AMPY_PATH="ampy"

@REM REM 檢查 ampy 工具是否存在
@REM IF NOT EXIST %AMPY_PATH% (
@REM     echo ampy not found。
@REM     goto :EOF
@REM )

REM 檢查指定的 COM 參數是否有效
SET COM_PORT=%~1
MODE %COM_PORT% > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo COM 參數無效。請檢查 COM 口是否存在。
    goto :EOF
)

REM 上傳檔案到 MicroPython 裝置
%AMPY_PATH% -p %COM_PORT% rm main.py
%AMPY_PATH% -p %COM_PORT% put BN165DKBDriver.py
%AMPY_PATH% -p %COM_PORT% put Data_Collection_Main_0525v4RX_task.py
%AMPY_PATH% -p %COM_PORT% put senko.py
%AMPY_PATH% -p %COM_PORT% put wifimgr.py
%AMPY_PATH% -p %COM_PORT% put wifi.dat
%AMPY_PATH% -p %COM_PORT% put main.py

echo 檔案上傳完成。

:EOF
