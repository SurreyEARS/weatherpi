import os  
import shutil  
import datetime  
import picamera  
import PIL  
from PIL import Image, ImageFont, ImageDraw  
import tweepy

import metoffer
api_key = '7fe18ea6-ca0d-4952-b166-aa0a0ae19ffb'
M = metoffer.MetOffer(api_key)
x = M.nearest_loc_forecast(51.215340, -0.602149, metoffer.THREE_HOURLY)
y = metoffer.parse_val(x)
forecast = y.data[0]

import math
import time
from ctypes import *

sensor = CDLL("./sensor.so")

class mpl3115a2:
	def __init__(self):
		if (0 == sensor.bcm2835_init()):
			print "bcm3835 driver init failed."
			return
			
	def writeRegister(self, register, value):
	    sensor.MPL3115A2_WRITE_REGISTER(register, value)
	    
	def readRegister(self, register):
		return sensor.MPL3115A2_READ_REGISTER(register)

	def active(self):
		sensor.MPL3115A2_Active()

	def standby(self):
		sensor.MPL3115A2_Standby()

	def initAlt(self):
		sensor.MPL3115A2_Init_Alt()

	def initBar(self):
		sensor.MPL3115A2_Init_Bar()

	def readAlt(self):
		return sensor.MPL3115A2_Read_Alt()

	def readTemp(self):
		return sensor.MPL3115A2_Read_Temp()

	def setOSR(self, osr):
		sensor.MPL3115A2_SetOSR(osr);

	def setStepTime(self, step):
		sensor.MPL3115A2_SetStepTime(step)

	def getTemp(self):
		t = self.readTemp()
		t_m = (t >> 8) & 0xff;
		t_l = t & 0xff;

		if (t_l > 99):
			t_l = t_l / 1000.0
		else:
			t_l = t_l / 100.0
		return (t_m + t_l)

	def getAlt(self):
		alt = self.readAlt()
		alt_m = alt >> 8 
		alt_l = alt & 0xff
		
		if (alt_l > 99):
			alt_l = alt_l / 1000.0
		else:
			alt_l = alt_l / 100.0
			
		return self.twosToInt(alt_m, 16) + alt_l
	def getBar(self):
		alt = self.readAlt()
		alt_m = alt >> 6 
		alt_l = alt & 0x03
		
		if (alt_l > 99):
			alt_l = alt_l 
		else:
			alt_l = alt_l 

		return (self.twosToInt(alt_m, 18))

	def twosToInt(self, val, len):
		# Convert twos compliment to integer
		if(val & (1 << len - 1)):
			val = val - (1<<len)

		return val

def capture_image(t):  
  cam = picamera.PiCamera()
  cam.resolution = (3280, 2464)
  cam.hflip = True
  cam.vflip = True
  filename = '/home/pi/weather/latest.jpg'
  cam.capture(filename, quality=100)
  return filename

def sensor_vals_as_string(sensor_vals):  
  sensor_str = 'Temp: %.2f C, Press: %.2f hPa' % (sensor_vals['temperature'],sensor_vals['pressure']/100)
  return sensor_str

def timestamp_image(t, sensor_vals):  
  ts_read = t.strftime('%H:%M, %a. %d %b %Y')
  sensor_str = sensor_vals_as_string(sensor_vals)
  img = Image.open('/home/pi/weather/latest.jpg')
  img = img.resize((1438, 1080))
  emfwm = Image.open('/home/pi/weather/emflogo.jpg')
  earswm = Image.open('/home/pi/weather/earslogo.png')
  emfwm.thumbnail((149, 149),Image.ANTIALIAS)
  earswm.thumbnail((325, 149),Image.ANTIALIAS)
  img.paste(emfwm, (0, 931))
  img.paste(earswm, (1113, 931))
  draw = ImageDraw.Draw(img)
  font = ImageFont.truetype('/home/pi/roboto/Roboto-Regular.ttf', 36)
  draw.text((10, 10), ts_read, (255, 255, 255), font=font)
  draw.text((10, 46), sensor_str, (255, 255, 255), font=font)
  filename = '/home/pi/weather/latest_ts.jpg'
  img.save(filename)
  return filename

def tweet_pic(status, latest, symbol):  
  ckey = 'igVZ1gE6NZffb9iWSry51tES9'
  csecret = 'Uw9cRGp50RpC32za7Ws22s32TAaIb4NZN3oqcLT9tqRoYlx8gN'
  akey = '758745982301417472-N8Tgjegs9WSkpfRv0ygDwpJgIO0XgEv'
  asecret = '2eiMefCdjxs9vOLm4P7Wb3WZzbfu0odif6fO1bWIO01AU'
  auth = tweepy.OAuthHandler(ckey, csecret)
  auth.set_access_token(akey, asecret)
  api = tweepy.API(auth)
  api.update_with_media(latest, status=status)
  api.update_profile_image(symbol)

def get_symbol(code):
  symbolmap = {
    0: 'moon.png',
    1: 'sunny.png',
    2: 'cloudy.png',
    3: 'cloudy.png',
    5: 'cloudy.png',
    6: 'cloudy.png',
    7: 'cloudy.png',
    8: 'cloudy.png',
    9: 'shower.png',
    10: 'shower.png',
    11: 'shower.png',
    12: 'shower.png',
    13: 'rain.png',
    14: 'rain.png',
    15: 'rain.png',
    16: 'rain.png',
    17: 'rain.png',
    18: 'rain.png',
    19: 'rain.png',
    20: 'rain.png',
    21: 'rain.png',
    22: 'snow.png',
    23: 'snow.png',
    24: 'snow.png',
    25: 'snow.png',
    26: 'snow.png',
    27: 'snow.png',
    28: 'thunder.png',
    29: 'thunder.png',
    30: 'thunder.png'
  }
  return 'symbols/' + symbolmap.get(code, 'sunny.png')

mpl = mpl3115a2()
#mpl.initAlt()
mpl.initBar()
mpl.active()
time.sleep(1)

t = datetime.datetime.now()
ts = t.strftime('%Y-%m-%d-%H-%M')
img = capture_image(t)
sensor_vals = {}
sensor_vals['temperature'] = mpl.getTemp()
sensor_vals['pressure'] = mpl.getBar()
latest = timestamp_image(t, sensor_vals)
status = '%s: Temp: %.2f C, Press: %.2f hPa, Met Forecast: %s' % (ts,sensor_vals['temperature'],sensor_vals['pressure']/100,metoffer.WEATHER_CODES[forecast["Weather Type"][0]])
symbol = get_symbol(forecast['Weather Type'][0])
tweet_pic(status, latest, symbol)
