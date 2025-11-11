#/usr/bin/sudo pkill -F /METARmaps/offpid.pid
/usr/bin/sudo pkill -F /METARmaps/metarpid.pid
echo 'refresh.sh:' $(date) >> /METARmaps/Logs/metar_refresh.log 2>&1

log=false
test=false
while getopts 'lt' opt; do
        case $opt in
            l) log=true ;;
            t) test=true ;;
            *) echo 'Error in command line parsing' >&2
               exit 1
        esac
    done
   #  shift "$(( OPTIND - 1 ))"

if [ $log = true ] && [ $test = true ]; then
   /usr/bin/sudo /usr/bin/python /METARmaps/metar.py -l -t >> /METARmaps/Logs/metar_refresh.log 2>&1 & echo $! > /METARmaps/metarpid.pid
elif "$log"; then
   /usr/bin/sudo /usr/bin/python /METARmaps/metar.py -l >> /METARmaps/Logs/metar_refresh.log 2>&1 & echo $! > /METARmaps/metarpid.pid
elif "$test"; then
   /usr/bin/sudo /usr/bin/python /METARmaps/metar.py -t >> /METARmaps/Logs/metar_refresh.log 2>&1 & echo $! > /METARmaps/metarpid.pid
else
   /usr/bin/sudo /usr/bin/python /METARmaps/metar.py >> /METARmaps/Logs/metar_refresh.log 2>&1 & echo $! > /METARmaps/metarpid.pid
fi
