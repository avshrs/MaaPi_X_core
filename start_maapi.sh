maapiWatcher="MaaPi_Watcher.py"
interpreter="/usr/bin/python3.6"

loc=$(pwd)

#cd $loc

pid=$(cat ${loc}/pid/MaaPi_Watcher.pid)

echo "old ${pid}"
if [ "$1" = "start" ]; then
    if ! kill -0 $pid > /dev/null 2>&1; then
        echo "Starting MaaPi_Watcher"
        nohup $interpreter $maapiWatcher > ${loc}/log/MaaPi_Watcher.log 2>&1 & echo $! > ${loc}/pid/MaaPi_Watcher.pid
    else
        echo "MaaPi_Watcher Running"
    fi
fi

if [ "$1" = "stop" ]; then
    kill -15 $pid
    sleep 3
    ps -aux | grep -i [m]aapi | awk '{print $2}' | while read line ;do  kill -15 $line ; done
fi

if [ "$1" = "restart" ]; then
    kill -15 $pid
    sleep 3
    ps -aux | grep -i [m]aapi | awk '{print $2}' | while read line ;do  kill -15 $line ; done
    echo "Starting MaaPi_Watcher"
    nohup $interpreter $maapiWatcher > log/MaaPi_Watcher.log 2>&1 & echo $!

fi
