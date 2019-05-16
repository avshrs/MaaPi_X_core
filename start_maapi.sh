maapiWatcher="MaaPi_Watcher.py"
interpreter="/usr/bin/python3.6"

loc=$(pwd)

if [ "$1" = "start" ]; then
    if ! kill -0 $(ps -aux | grep "[M]aaPi_Watcher.py" | awk '{print $2}') > /dev/null 2>&1; then
        echo "Starting MaaPi_Watcher"
        nohup $interpreter $maapiWatcher >> ${loc}/log/MaaPi_Watcher.log 2>&1 & echo $!
    else
        echo "MaaPi Running"
    fi
fi

if [ "$1" = "stop" ]; then
    if ! kill -0 $(ps -aux | grep "[M]aaPi_Watcher.py" | awk '{print $2}') > /dev/null 2>&1; then
        echo "MaaPi Not Running"
    else
        kill -2 $(ps -aux | grep "[M]aaPi_Watcher.py" | awk '{print $2}')
        sleep 1
        if ! kill -0 $(ps -aux | grep "[M]aaPi_Watcher.py" | awk '{print $2}') > /dev/null 2>&1; then
            echo "MaaPi - stoped"
        fi
    fi
fi
