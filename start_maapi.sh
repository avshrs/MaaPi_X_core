maapiWatcher="MaaPi_Watcher.py"
interpreter="python3.6"
pid=$(cat .MaaPi.pid)
path="/home/pi/MaaPi_X_core/"
cd $path
if [ "$1" == "start" ]; then
    if ! kill $pid > /dev/null 2>&1; then
        echo starting $maapiWatcher
        nohup $interpreter $maapiWatcher > /dev/null 2>&1 & echo $! > .MaaPi.pid
    fi
fi
if [ "$1" == "stop" ]; then
    if  kill $pid > /dev/null 2>&1; then
        echo stoping $maapiWatcher
        kill $pid
    fi
fi