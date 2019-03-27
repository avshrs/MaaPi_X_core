maapiWatcher="MaaPi_Watcher.py"
interpreter="python3.7"

pid=$(cat pid/MaaPi_Watcher.pid)

if [ "$1" = "start" ]; then
    if ! kill -0 $pid > /dev/null 2>&1; then
        echo "Starting MaaPi_Watcher"
        nohup $interpreter $maapiWatcher > log/MaaPi_Watcher.log 2>&1 & echo $!
        # nohup $interpreter $maapiWatcher > log/MaaPi_Watcher.log 2>&1 & echo $!

    else
        echo "MaaPi_Watcher Running"
    fi
fi
if [ "$1" = "stop" ]; then
    kill -9 $pid
fi
