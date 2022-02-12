maxlines=500
log_msg='Whatever the log message is'

sed -i -e1i"\\$log_msg" -e$((maxlines))',$d' hourly_restart.log

### go to the env
. /opt/anaconda3/bin/activate && conda activate /opt/anaconda3
#ROOTPATH="/Users/danny/Documents/Projects/princess/KokkoroBot-Multi-Platform-master/kokkoro/pcrjjc2-discord-main"
#TARTGETPATH="/Users/danny/Documents/Projects/princess/KokkoroBot-Multi-Platform-master/kokkoro/pcrjjc2-discord-main"
ps -ef | grep main.py | grep -v grep | awk '{print $2}' | xargs -r kill -9

cd /Users/danny/Documents/Projects/princess/KokkoroBot-Multi-Platform-master/kokkoro/pcrjjc2-discord-main/
python main.py 
