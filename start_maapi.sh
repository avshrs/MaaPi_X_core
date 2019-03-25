maapiWatcher="MaaPi_Watcher.py"
interpreter="python3.6"

path="pid/"

cd $path


for f in *socket.pid
do

	pid=$(cat $f)
        echo "Checking Maapi module: $pid - $f"
    if kill -0 $pid > /dev/null 2>&1; then
        echo "Killing Maapi module: $f"
        kill "${pid}"
        if kill -0 $pid > /dev/null 2>&1; then
            echo "Process still exist killing -9  $f"
            kill -9 "${pid}"
        fi
    else
        echo "pid $pid - $f - is ded"
    fi



done

for f in *.pid
do

	pid=$(cat $f)
        echo "Checking Maapi module: $pid - $f"
    if kill -0 $pid > /dev/null 2>&1; then
        echo "Killing Maapi module: $f"
        kill "${pid}"
        if kill -0 $pid > /dev/null 2>&1; then
            echo "Process still exist killing -9  $f"
            kill -9 "${pid}"
        fi
    else
        echo "pid $pid - $f - is ded"
    fi



done