#  METARmaps.com
#  USA v1.82
#  OS v2.02

import urllib2
import xml.etree.ElementTree as ET
from neopixel import *
import datetime
import time
from weather_utils import Condition

# LED strip configuration:
LED_COUNT      = 248     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 10      # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

COLOR_VFR		= 	Color(255,0,0)		# Green
COLOR_VFR_FADE		= Color(125,0,0)		# Green Fade for wind
COLOR_MVFR		= 	Color(0,0,255)		# Blue
COLOR_MVFR_FADE		= Color(0,0,125)		# Blue Fade for wind
COLOR_IFR		= 	Color(0,255,0)		# Red
COLOR_IFR_FADE		= Color(0,125,0)		# Red Fade for wind
COLOR_LIFR		= 	Color(0,125,125)		# Magenta
COLOR_LIFR_FADE		= Color(0,75,75)		# Magenta Fade for wind
COLOR_UNK		= 	Color(255,255,255)		# Green
COLOR_UNK_FADE		= Color(255,255,255)		# Green Fade for wind
COLOR_CLEAR		= 	Color(0,0,0)		# Clear
COLOR_LIGHTNING		= Color(255,255,255)		# White

# ----- Blink/Fade functionality for Wind and Lightning -----
# Do you want the METARMap to be static to just show flight conditions, or do you also want blinking/fading based on current wind conditions
ACTIVATE_WINDCONDITION_ANIMATION = True	# Set this to False for Static or True for animated wind conditions
#Do you want the Map to Flash white for lightning in the area
ACTIVATE_LIGHTNING_ANIMATION = True		# Set this to False for Static or True for animated Lightning
# Fade instead of blink
FADE_INSTEAD_OF_BLINK	= False			# Set to False if you want blinking
# Blinking Windspeed Threshold
WIND_BLINK_THRESHOLD	= 25			# Knots of windspeed
ALWAYS_BLINK_FOR_GUSTS	= False			# Always animate for Gusts (regardless of speeds)
# Blinking Speed in seconds
BLINK_SPEED		= 1.0			# Float in seconds, e.g. 0.5 for half a second
# Total blinking time in seconds.
# For example set this to 300 to keep blinking for 5 minutes if you plan to run the script every 5 minutes to fetch the updated weather
BLINK_TOTALTIME_SECONDS	= 300

pixels = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
pixels.begin()

with open("/METARmaps/airports") as f:
    airports = f.readlines()
airports = [x.strip() for x in airports]

url = "https://aviationweather.gov/api/data/metar?format=xml&hoursBeforeNow=5&mostRecentForEachStation=true&ids="

airport_list = [airportcode for airportcode in airports if airportcode != "NULL"]
url = url + ",".join(airport_list)

#print (url)
content = urllib2.urlopen(url).read()

root = ET.fromstring(content)
missingCondList=[]
conditionDict = { "NULL": {"flightCategory" : "", "windDir": "", "windSpeed" : 0, "windGustSpeed" :  0, "windGust" : False, "lightning": False, "tempC" : 0, "dewpointC" : 0, "vis" : 0, "altimHg" : 0, "obs" : "", "skyConditions" : {}, "obsTime" : datetime.datetime.now() } }
conditionDict.pop("NULL")

for metar in root.iter('METAR'):
	stationId = metar.find('station_id').text
	if metar.find('flight_category') is None:
		print ("Skipping " + stationId + " no flight category")
		missingCondList.append(stationId)
		continue

	flightCategory = metar.find('flight_category').text
	windDir = ""
	windSpeed = 0
	windGustSpeed = 0
	windGust = False
	lightning = False
	tempC = 0
	dewpointC = 0
	vis = 0
	altimHg = 0.0
	obs = ""
	skyConditions = []

	if metar.find('wind_gust_kt') is not None:
		windGustSpeed = int(metar.find('wind_gust_kt').text)
		windGust = (True if (ALWAYS_BLINK_FOR_GUSTS or windGustSpeed > WIND_BLINK_THRESHOLD) else False)
	if metar.find('wind_speed_kt') is not None:
		windSpeed = int(metar.find('wind_speed_kt').text)
	if metar.find('wind_dir_degrees') is not None:
		windDir = metar.find('wind_dir_degrees').text
	if metar.find('temp_c') is not None:
		tempC = int(round(float(metar.find('temp_c').text)))
	if metar.find('dewpoint_c') is not None:
		dewpointC = int(round(float(metar.find('dewpoint_c').text)))
	if metar.find('visibility_statute_mi') is not None:
		vis = int(round(float(metar.find('visibility_statute_mi').text.replace('+',''))))
	if metar.find('altim_in_hg') is not None:
		altimHg = float(round(float(metar.find('altim_in_hg').text), 2))
	if metar.find('wx_string') is not None:
		obs = metar.find('wx_string').text
	if metar.find('observation_time') is not None:
		obsTimeStr = metar.find('observation_time').text.replace("Z", "+00:00")
		obsTime = datetime.datetime.strptime(obsTimeStr.split('+')[0], "%Y-%m-%dT%H:%M:%S.%f")
	for skyIter in metar.iter("sky_condition"):
		skyCond = { "cover" : skyIter.get("sky_cover"), "cloudBaseFt": int(skyIter.get("cloud_base_ft_agl", default=0)) }
		skyConditions.append(skyCond)
	if metar.find('raw_text') is not None:
		rawText = metar.find('raw_text').text
		lightning = False if rawText.find('LTG') == -1 else True

	conditionDict[stationId] = { "flightCategory" : flightCategory, "windDir": windDir, "windSpeed" : windSpeed, "windGustSpeed": windGustSpeed, "windGust": windGust, "vis": vis, "obs" : obs, "tempC" : tempC, "dewpointC" : dewpointC, "altimHg" : altimHg, "lightning": lightning, "skyConditions" : skyConditions, "obsTime": obsTime }

print("Missing conditions for stations:", missingCondList)
print("Getting weather for " + str(len(airports)) + " airports")

looplimit = int(round(BLINK_TOTALTIME_SECONDS / BLINK_SPEED)) if (ACTIVATE_WINDCONDITION_ANIMATION or ACTIVATE_LIGHTNING_ANIMATION) else 1
windCycle = False

while looplimit > 0:
	i = 0

	# Set light color and status for all entries in airports list
	for airport in airports:
		color = COLOR_CLEAR
		conditions = conditionDict.get(airport, None)
		windy = False
		lightningConditions = False
		fltCat = conditions.flightCategory if conditions is not None else "None"
		if conditions != None:
			windy = True if (ACTIVATE_WINDCONDITION_ANIMATION and windCycle == True and (conditions["windSpeed"] > WIND_BLINK_THRESHOLD or conditions["windGust"] == True)) else False
			lightningConditions = True if (ACTIVATE_LIGHTNING_ANIMATION and windCycle == False and conditions.lightning == True) else False

			if conditions.flightCategory == "VFR":
				color = COLOR_VFR if not (windy or lightningConditions) else COLOR_LIGHTNING if lightningConditions else (COLOR_VFR_FADE if FADE_INSTEAD_OF_BLINK else COLOR_CLEAR) if windy else COLOR_CLEAR
				colorName = "Green"
			elif conditions.flightCategory == "MVFR":
				color = COLOR_MVFR if not (windy or lightningConditions) else COLOR_LIGHTNING if lightningConditions else (COLOR_MVFR_FADE if FADE_INSTEAD_OF_BLINK else COLOR_CLEAR) if windy else COLOR_CLEAR
				colorName = "Blue"
			elif conditions.flightCategory == "IFR":
				color = COLOR_IFR if not (windy or lightningConditions) else COLOR_LIGHTNING if lightningConditions else (COLOR_IFR_FADE if FADE_INSTEAD_OF_BLINK else COLOR_CLEAR) if windy else COLOR_CLEAR
				colorName = "Red"
			elif conditions.flightCategory == "LIFR":
				color = COLOR_LIFR if not (windy or lightningConditions) else COLOR_LIGHTNING if lightningConditions else (COLOR_LIFR_FADE if FADE_INSTEAD_OF_BLINK else COLOR_CLEAR) if windy else COLOR_CLEAR
				colorName = "Magenta"
			elif conditions.flightCategory == None:
				color = COLOR_UNK if not (windy or lightningConditions) else COLOR_LIGHTNING if lightningConditions else (COLOR_UNK_FADE if FADE_INSTEAD_OF_BLINK else COLOR_CLEAR) if windy else COLOR_CLEAR
				colorName = "Clear"
			else:
				color = COLOR_CLEAR

		#print("Setting LED " + str(i) + " for " + airport + " to " + ("lightning " if lightningConditions else "") + ("windy " if windy else "") + (fltCat if conditions != None else "None") + " " + colorName)
		pixels.setPixelColor(i, color)
		i += 1

	pixels.show()

	# Switching between animation cycles
	time.sleep(BLINK_SPEED)
	windCycle = False if windCycle else True
	looplimit -= 1
print ("finished")