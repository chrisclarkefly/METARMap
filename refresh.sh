/usr/bin/sudo pkill -F /METARmaps/metarpid.pid
echo 'refresh.sh:' $(date) >> /METARmaps/Logs/metar_refresh.log 2>&1
/usr/bin/sudo /usr/bin/python /METARmaps/metar.py >> /METARmaps/Logs/metar_refresh.log 2>&1 & echo $! > /METARmaps/metarpid.pid

