@echo off
::此文件用于安装所需的环境，编码为ANSI/GB 2312,请勿更改编码格式。::
::install config::
set git_source=https://mirror.ghproxy.com/https://github.com
set pip_source=https://pypi.tuna.tsinghua.edu.cn/simple

set python_installer=https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
set git_installer=%git_source%/git-for-windows/git/releases/download/v2.46.0.windows.1/Git-2.46.0-64-bit.exe
set gcc_installer=https://nuwen.net/files/mingw/mingw-19.0.exe

set enable_venv=1

set max_connection=16
set min_split_size=1M

set pip_extra_install_packages=
:::::::::::::::::

cd /d %~dp0
set ESC=
set RD=%ESC%[31m
set GN=%ESC%[32m
set YW=%ESC%[33m
set BL=%ESC%[34m
set WT=%ESC%[37m
set RN=%ESC%[0m
echo %GN%[INFO]%WT% 检测完整性...
if not exist install_env\aria2c.exe (
    echo %RD%[ERROR]%WT% aria2c.exe 未找到，请检查完整性。
    exit
)
if not exist install_env\7z.exe (
    echo %RD%[ERROR]%WT% 7z.exe 未找到，请检查完整性。
    exit
)
echo %GN%[INFO]%WT% 检测程序运行时...
python --version
if errorlevel 1 (
    set python_installed=0
) else (
    set python_installed=1
)
python --version|findstr /r /i "3.12" > NUL && echo %YW%[WARN]%WT% 你的python可能不兼容pytorch，请卸载后重新打开程序。 && exit
git --version
if errorlevel 1 (
    set git_installed=0
) else (
    set git_installed=1
)
gcc --version
if errorlevel 1 (
    set gcc_installed=0
) else (
    set gcc_installed=1
)
nvcc --version
if errorlevel 1 (
    set cuda_installed=0
) else (
    echo %GN%[INFO]%WT% CUDA已安装，将安装PyTorch-cuda版本。
    set cuda_installed=1
)
echo %GN%[INFO]%WT% 请检查列出的配置是否正确，如有错误请修改install_env.bat中的config。
echo.
echo     是否启用python venv = %enable_venv%
echo     aria2c最大连接数 = %max_connection%
echo     aria2c最小分片大小 = %min_split_size%
echo     pip源 = %pip_source%
echo     git源 = %git_source%
echo %BL%    pip额外安装包 = %pip_extra_install_packages%
if %python_installed%==0 (
    echo %RD%    未找到python，将尝试安装。
    echo %WT%    python安装包 = %python_installer%
) else (    
    echo %GN%    python已安装。
)
if %git_installed%==0 (
    echo %RD%    未找到git，将尝试安装。
    echo %WT%    git安装包 = %git_installer%
) else (
    echo %GN%    git已安装。
)
if %gcc_installed%==0 (
    echo %RD%    未找到gcc，将尝试安装。
    echo %WT%    gcc安装包 = %gcc_installer%
) else (
    echo %GN%    gcc已安装。
)
if %cuda_installed%==0 (
    echo %YW%    未找到CUDA，PyTorch将只安装CPU版本。%WT%
) else (
    echo %GN%    CUDA已安装,将安装PyTorch-cuda版本。%WT%
)
echo.
install_env\sleepx -p "如果要停止安装，请在10秒内按下任意键..." -k 10
if errorlevel 1 (
    echo %RD%[ERROR]%WT% 已停止安装。
    echo %WT%按任意键退出。
    pause>nul
    exit
)
echo %GN%[INFO]%WT% 开始安装...
if %python_installed%==0 (
    call :installpy
)
if %git_installed%==0 (
    call :installgit
)
if %gcc_installed%==0 (
    call :installgcc
)
if %enable_venv%==1 (
    echo %GN%[INFO]%WT% 启用python venv...
    if not exist Muice\Scripts\activate.bat python -m venv Muice
    call Muice\Scripts\activate.bat
)
echo %GN%[INFO]%WT% 安装依赖...
ping -n 2 127.1 > nul
call :install_req
echo %GN%[INFO]%WT% 安装PyTorch...
ping -n 2 127.1 > nul
call :install_pytorch
echo %GN%[INFO]%WT% 安装extra包...
ping -n 2 127.1 > nul
if not "%pip_extra_install_packages%"=="" (
    pip install %pip_extra_install_packages% -i %pip_source%
)
echo %GN%[INFO]%WT% 安装完成！
echo %GN%[INFO]%WT% 正在生成启动脚本...
ping -n 2 127.1 > nul
echo @echo off>start.bat
if %enable_venv%==1 echo call Muice\Scripts\activate.bat>>start.bat
echo python main.py>>start.bat
echo pause>>start.bat
echo %GN%[INFO]%WT% 你可以使用start.bat启动main.py。
if %enable_venv%==1 echo %GN%[INFO]%WT% 若要激活环境，使用"call Muice\Scripts\activate.bat"。
echo %GN%[INFO]%WT% 按任意键退出。
pause>nul
exit



:install_pytorch
if %cuda_installed%==0 goto :eof
echo %GN%[INFO]%WT% 检测CUDA版本...
set cudaver=
nvcc --version|findstr /r /i "11.8" > NUL && set cudaver=cu118
nvcc --version|findstr /r /i "12.1" > NUL && set cudaver=cu121
nvcc --version|findstr /r /i "12.4" > NUL && set cudaver=cu124
if "%cudaver%"=="" (
    echo %RD%[ERROR]%WT% 未知或不支持的CUDA版本，请卸载并安装11.8/12.1/12.4版本的CUDA。
    echo %WT%按任意键退出。
    pause>nul
    exit
)
pip install torch==2.4.1+%cudaver% torchvision torchaudio -i %pip_source% --extra-index-url https://download.pytorch.org/whl/%cudaver%
if errorlevel 1 (
    echo %RD%[ERROR]%WT% 安装PyTorch失败。
    echo %WT%按任意键退出。
    pause>nul
    exit
)
goto :eof

:install_req
pip install -r requirements.txt -i %pip_source%
if errorlevel 1 (
    echo %RD%[ERROR]%WT% 安装依赖失败。
    echo %WT%按任意键退出。
    pause>nul
    exit
    )
goto :eof

:installpy
md software
echo %GN%[INFO]%WT% 正在下载python...
if exist software\python-installer.exe (
    if not exist software\python-installer.exe.aria2 (
       del /q software\python-installer.exe
    )
  )
install_env\aria2c --max-connection-per-server=%max_connection% --min-split-size=%min_split_size% --dir software --out python-installer.exe %python_installer%
echo %GN%[INFO]%WT% 正在安装python...
echo %YW%[WARN]%WT% 请等待安装完成后重新打开程序。
echo %YW%[WARN]%WT% 若安装程序未运行，大概率为下载失败，请重新打开程序。
software\python-installer.exe /passive AppendPath=1 PrependPath=1 InstallAllUsers=1
echo 按任意键退出。
pause>nul
exit

:installgit
md software
echo %GN%[INFO]%WT% 正在下载git...
if exist software\git-installer.exe (
    if not exist software\git-installer.exe.aria2 (
       del /q software\git-installer.exe
    )
  )
install_env\aria2c --max-connection-per-server=%max_connection% --min-split-size=%min_split_size% --dir software --out git-installer.exe %git_installer%
echo %GN%[INFO]%WT% 正在安装git...
echo %YW%[WARN]%WT% 请等待安装完成后重新打开程序。
echo %YW%[WARN]%WT% 若安装程序未运行，大概率为下载失败，请重新打开程序。
software\git-installer.exe /SILENT /NORESTART
echo 按任意键退出。
pause>nul
exit

:installgcc
md software
echo %GN%[INFO]%WT% 正在下载gcc...
if exist software\gcc.7z (
    if not exist software\gcc.7z.aria2 (
       del /q software\gcc.7z
    )
  )
install_env\aria2c --max-connection-per-server=%max_connection% --min-split-size=%min_split_size% --dir software --out gcc-installer.exe %gcc_installer%
echo %GN%[INFO]%WT% 正在安装gcc...
echo %YW%[WARN]%WT% 安装完成后重新打开程序。
install_env\7z x software\gcc-installer.exe
echo %YW%[WARN]%WT% 杀软报错请同意。
setx PATH "%PATH%;%~dp0MinGW\bin"
set X_MEOW=%~dp0MinGW\include;%~dp0MinGW\include\freetype2
if defined C_INCLUDE_PATH (setx C_INCLUDE_PATH "%X_MEOW%;%C_INCLUDE_PATH%") else (setx C_INCLUDE_PATH "%X_MEOW%")
if defined CPLUS_INCLUDE_PATH (setx CPLUS_INCLUDE_PATH "%X_MEOW%;%CPLUS_INCLUDE_PATH%") else (setx CPLUS_INCLUDE_PATH "%X_MEOW%")
set X_MEOW=
echo 按任意键退出。
pause>nul
exit