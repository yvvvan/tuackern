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
new_data = False
# delay of the webpage, 
# arduino:10s fixed, backend = delay/2, frontend = delay, IO = delay*10 
delay = 30

@app.route("/")
def index():
	humidity_data_list_cut = humidity_data_list_old
	time_list_cut = time_list_old
	chart_data = {'labels': time_list_cut,'data': humidity_data_list_cut, 'delay': delay*1000}
	return render_template('index.html', chart_data=chart_data)

@app.route("/watering")
def watering():
	print('watering')
	return 'watered'

@app.route("/humidity")
def humidity_data():
	global new_data
	humidity_data_list_cut = humidity_data_list_old + humidity_data_list_new
	time_list_cut = time_list_old + time_list_new
	chart_data = {'labels': time_list_cut,'data': humidity_data_list_cut, 'new_data': new_data}
	new_data = False
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

def normalization(number, max=663, min=311):
	# min=100%, max=0%
	number = (number - min) / (max - min)
	number = 1 - number
	return number

def humidity(delay=30):
	while True:
		arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)
		time.sleep(delay)
		value = arduino.readline()
		if value:
			# value to string
			value = value.decode('utf-8')
			# remove \r\n
			value = value.strip()
			value = value.split('-')[1]
			# remove "%" and convert to float
			# value = float(value[:-1])
			value = float(value)
			# normalization
			value = normalization(value)*100
			value = round(value, 2)
			# add to list
			humidity_data_list_new.append(value)
			# current time
			time_list_new.append(time.strftime("%H:%M:%S", time.localtime()))
			global new_data
			new_data = True


def save_data(delay=120):
	global time_list_new
	global humidity_data_list_new
	global time_list_old
	global humidity_data_list_old
	while True:
		time.sleep(delay)
		with open('humidity_data_list.txt', 'a') as f:
			for i in range(len(humidity_data_list_new)):
				# write todays date
				f.write(time.strftime("%Y-%m-%d", time.localtime()) + ',')
				f.write(str(time_list_new[i]) +","+ str(humidity_data_list_new[i]) + '\n')
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
					time_list_old.append(line[1])
					humidity_data_list_old.append(float(line[2]))
			


def detect_motion(frameCount):
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lock
	# initialize the motion detector and the total number of frames
	# read thus far
	md = SingleMotionDetector(accumWeight=0.1)
	total = 0

	# loop over frames from the video stream
	while True:
		# read the next frame from the video stream, resize it,
		# convert the frame to grayscale, and blur it
		frame = vs.read()
		frame = imutils.resize(frame, width=400)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)
		# grab the current timestamp and draw it on the frame
		timestamp = datetime.datetime.now()
		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)

		# if the total number of frames has reached a sufficient
		# number to construct a reasonable background model, then
		# continue to process the frame
		if total > frameCount:
			# detect motion in the image
			motion = md.detect(gray)
			# check to see if motion was found in the frame
			if motion is not None:
				# unpack the tuple and draw the box surrounding the
				# "motion area" on the output frame
				(thresh, (minX, minY, maxX, maxY)) = motion
				cv2.rectangle(frame, (minX, minY), (maxX, maxY),
					(0, 0, 255), 2)
		
		# update the background model and increment the total number
		# of frames read thus far
		md.update(gray)
		total += 1
		# acquire the lock, set the output frame, and release the
		# lock
		with lock:
			outputFrame = frame.copy()

def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")


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
	t = threading.Thread(target=detect_motion, args=(
		args["frame_count"],))
	t.daemon = True
	t.start()

	#异步执行 每1分钟寸一次humidity_data_list和time_list
	load_data()
	t1 = threading.Thread(target=save_data, args=(delay,))
	t1.daemon = True
	t1.start()
	
	#异步执行
	t2 = threading.Thread(target=humidity, args=(delay/2,))
	t2.daemon = True
	t2.start()

	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)

	
	
# release the video stream pointer
vs.stop()