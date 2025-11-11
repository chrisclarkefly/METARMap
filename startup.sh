#!/bin/bash
echo 'Rainbow Test' $(date) >> /METARmaps/Logs/metar_start.log 2>&1 
/usr/bin/sudo /usr/bin/python /METARmaps/test.py >> /METARmaps/Logs/metar_start.log 2>&1
echo 'startup.sh:' $(date) >> /METARmaps/Logs/metar_start.log 2>&1 
/METARmaps/refresh.sh >> /METARmaps/Logs/metar_refresh.log 2>&1