# import the necessary packages
from pyimagesearch.motion_detection.singlemotiondetector import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2
import serial
import os

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()
stopFlag = False
lightFlag = False
smartFlag = False
t0 = None
# initialize a flask object
app = Flask(__name__)
# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
time.sleep(2.0)
humidity_data_list_old = []
time_list_old = []
humidity_data_list_new = []
time_list_new = []
# delay of the webpage, 
# arduino:10s fixed, backend = delay/2, frontend = delay, IO = delay*10 
delay = 30
min_humidity = 612
max_humidity = 311
arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)
camera_delay = 0.25

@app.route("/")
def index():
	humidity_data_list_cut = humidity_data_list_old + humidity_data_list_new
	time_list_cut = time_list_old + time_list_new
	chart_data = {'labels': time_list_cut,'data': humidity_data_list_cut, 'delay': delay*1000}
	return render_template('index.html', chart_data=chart_data)

@app.route("/watering")
def watering():
	arduino.write("B".encode())
	print('watering')
	return 'watered'

@app.route("/smart")
def smart():
	arduino.write("C".encode())
	return 'smart mode'

@app.route("/humidity")
def humidity_data():
	# humidity_data_list_cut = humidity_data_list_old + humidity_data_list_new
	# time_list_cut = time_list_old + time_list_new
	if humidity_data_list_new and time_list_new:
		new_humidity = humidity_data_list_new[-1]
		new_label = time_list_new[-1]
	else:
		new_humidity = humidity_data_list_old[-1]
		new_label = time_list_old[-1]
	chart_data = {'label': new_label,'data': new_humidity}
	return chart_data

@app.route("/humidity2")
def humidity_datas():
	for timelabel in time_list_old:
		# get today
		today = time.strftime("%Y-%m-%d", time.localtime())
		#if time is yesterday, remove it
		if timelabel[:10] != today:
			time_list_old.remove(timelabel)
			humidity_data_list_old.remove(humidity_data_list_old[time_list_old.index(timelabel)])
	humidity_data_list_cut = humidity_data_list_old + humidity_data_list_new
	time_list_cut = time_list_old + time_list_new
	chart_data = {'labels': time_list_cut,'datas': humidity_data_list_cut}
	return chart_data

def average_sample(data_list, target_length=50):
	list_length = len(data_list)
	if list_length <= target_length:
		return data_list
	last_item = data_list[-1]
	data_list = data_list[:-1]
	step = list_length // target_length
	sampled_list = [data_list[i * step] for i in range(target_length)]
	sampled_list.append(last_item)
	return sampled_list

def normalization(number, max=max_humidity, min=min_humidity):
	# min=100%, max=0%
	number = (number - min) / (max - min)
	# number = 1 - number
	return number

def get_arduino_humidity(delay=30):
	while True:
		time.sleep(delay)
		value = arduino.readline()
		if value:
			# print(value)
			# value to string
			value = value.decode('utf-8')
			# remove \r\n
			value = value.strip()
			value = value.split('-')[0]
			# remove "%" and convert to float
			# value = float(value[:-1])
			value = float(value)
			# normalization
			value = normalization(value)*100
			if value > 100:
				value = 100
			elif value < 0:
				value = 0
			value = round(value, 2)
			# print(value)
			# add to list
			humidity_data_list_new.append(value)
			# current time add to list in format of YYYY-MM-DD@HH:MM:SS
			time_list_new.append(time.strftime("%Y-%m-%d@%H:%M:%S", time.localtime()))


def save_data(delay=120):
	global time_list_new
	global humidity_data_list_new
	global time_list_old
	global humidity_data_list_old
	while True:
		time.sleep(delay)
		with open('humidity_data_list.txt', 'a') as f:
			for i in range(len(humidity_data_list_new)):
				# write CURRENT TIME YYYY-MM-DD,HH:MM:SS,humidity
				f.write(str(time_list_new[i]).replace("@",",") + ',' + str(humidity_data_list_new[i]) + '\n')
		humidity_data_list_old += humidity_data_list_new
		time_list_old += time_list_new
		humidity_data_list_new = []
		time_list_new = []
		

def load_data():
	global time_list_old
	global humidity_data_list_old
	if os.path.exists('humidity_data_list.txt'):
		with open('humidity_data_list.txt', 'r') as f:
			for line in f.readlines():
				line = line.strip().split(',')
				# if date is today, read
				if line[0] == time.strftime("%Y-%m-%d", time.localtime()):
					time_list_old.append(line[0]+'@'+line[1])
					humidity_data_list_old.append(float(line[2]))
firstRun = True
cameraTime = 60	
startTime = 0		
def prepare_frame(frameCount):
	global vs, outputFrame, lock, stopFlag, firstRun, startTime, cameraTime
	while True:
		time.sleep(camera_delay)
		frame = vs.read()
		frame = imutils.resize(frame, width=400)
		timestamp = datetime.datetime.now()
		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
		with lock:
			outputFrame = frame.copy()
			# if firstRun:
			# 	startTime = time.time()
			# 	firstRun = False
			# 	stopFlag = True
			# 	break
			# if time.time() - startTime > cameraTime:
			# 	startTime = time.time()
			# 	stopFlag = True
			# 	break
		if stopFlag:
			break
		

def generate():
	global outputFrame, lock
	while True:
		time.sleep(camera_delay)
		with lock:
			if outputFrame is None:
				continue
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			if not flag:
				continue
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/video_pause")
def video_pause():
	global stopFlag, t0
	# kill thread t0
	stopFlag = True
	t0.join()
	return 'video paused'

@app.route("/video_resume")
def video_resume():
	global stopFlag, t0
	stopFlag = False
	if t0.is_alive():
		return 'video is running'
	else:
		t0.join()
		# start a thread that will perform motion detection
		t0 = threading.Thread(target=prepare_frame, args=(
			args["frame_count"],))
		t0.daemon = True
		t0.start()
		return 'video resumed'

@app.route("/video_status")
def video_status():
	global stopFlag, t0
	if stopFlag:
		t0.join()
	return {'camera': str(stopFlag), 'light': str(lightFlag), 'smart': str(smartFlag)}

@app.route("/light_on_off")
def light_on_off():
	global lightFlag
	lightFlag = not lightFlag
	arduino.write("A".encode())
	return 'light changed'

@app.route("//smart_on_off")
def smart_on_off():
	global smartFlag
	smartFlag = not smartFlag
	arduino.write("C".encode())
	return 'smart mode changed'

# check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())

	# start a thread that will perform motion detection
	t0 = threading.Thread(target=prepare_frame, args=(
		args["frame_count"],))
	t0.daemon = True
	t0.start()

	#异步执行 每1分钟寸一次humidity_data_list和time_list
	load_data()
	t1 = threading.Thread(target=save_data, args=(delay*10,))
	t1.daemon = True
	t1.start()
	
	#异步执行
	t2 = threading.Thread(target=get_arduino_humidity, args=(delay/2,))
	t2.daemon = True
	t2.start()

	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)

	
	
# release the video stream pointer
vs.stop()