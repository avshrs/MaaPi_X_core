maapiWatcher="MaaPi_Watcher.py"
interpreter="python3.6"

nohup python3.6 MaaPi_Watcher.py > /log/Maapi_console.log 2>&1 & echo $! > pid/MaaPi_wacher_sh.pid