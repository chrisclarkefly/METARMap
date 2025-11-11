/usr/bin/sudo pkill -F /METARmaps/offpid.pid
/usr/bin/sudo pkill -F /METARmaps/metarpid.pid
/usr/bin/sudo /usr/bin/python /METARmaps/pixelsoff.py & echo $! > /METARmaps/offpid.pid