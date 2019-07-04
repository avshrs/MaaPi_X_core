maapiWatcher="MaaPi_Watcher.py"
interpreter="/usr/bin/python3.6"

loc=$(pwd)

if [ "$1" = "start" ]; then
    if ! kill -0 $(ps -aux | grep "[M]aaPi_Watcher.py" | awk '{print $2}') > /dev/null 2>&1; then
        echo "Starting MaaPi_Watcher"
        nohup $interpreter $maapiWatcher >> /dev/null 2>&1 &
    else
        echo "MaaPi Running"
    fi
else
    if [ "$1" = "stop" ]; then
        if ! kill -0 $(ps -aux | grep "[M]aaPi_Watcher.py" | awk '{print $2}') > /dev/null 2>&1; then
            echo "MaaPi Not Running"
        else
            kill $(ps -aux | grep "[M]aaPi_Watcher.py" | awk '{print $2}')
            sleep 1
            if ! kill -0 $(ps -aux | grep "[M]aaPi_Watcher.py" | awk '{print $2}') > /dev/null 2>&1; then
                echo "MaaPi - stoped"
            fi
        fi
    else
           echo "Use ./start_maapi.sh start|stop"
    fi

fi