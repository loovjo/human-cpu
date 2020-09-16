GREEN="\033[38;5;2m"
RED="\033[38;5;1m"
BLUE="\033[38;5;4m"
RESET="\033[0m"

echo "$BLUE[ Checking config ]$RESET"

nginx -p . -c nginx-conf/nginx-conf.conf -t

if [ $? == 0 ]
then
    echo "$GREEN[ Killing old server ]$RESET"
    nginx -s quit
    echo "$GREEN[ Starting server ]$RESET"
    nginx -p . -c nginx-conf/nginx-conf.conf
else
    echo "$RED[ Got Error ]$RESET"
fi
