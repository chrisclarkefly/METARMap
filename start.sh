#!/bin/bash
echo 'start.sh:' $(date) >> /METARmaps/Logs/metar_start.log 2>&1 
/METARmaps/refresh.sh >> /METARmaps/Logs/metar_refresh.log 2>&1