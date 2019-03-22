maapiWatcher="MaaPi_Watcher.py"
interpreter="python3.6"
pid=$(cat .MaaPi.pid)
if ! kill $pid > /dev/null 2>&1; then
        killall python3.6
        echo starting $maapiWatcher
        nohup $interpreter $maapiWatcher >> log/Maapi_Selector-man.log  2>&1 & echo $! > .MaaPi.pid
        echo $pid
fi