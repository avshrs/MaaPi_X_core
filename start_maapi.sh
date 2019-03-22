maapiWatcher="MaaPi_Watcher.py"
interpreter="python3.6"

echo Killing $maapiWatcher
killall python3.6
echo Starting $maapiWatcher
nohup $interpreter $maapiWatcher >> log/Maapi_console.log  2>&1 & echo $

