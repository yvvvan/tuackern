## TU Stadt Ackern
```

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip

sudo apt install python3-venv
python3 -m venv ackern
source ackern/bin/activate

deactive

pip install opencv-python
pip install flask imutils

## Python Script (Camera)
python3 webstreaming.py --ip 0.0.0.0 --port 5323
lsof /dev/video0
sudo kill -9 $(lsof -t /dev/video0)

## Arduino CLI installieren
$ sudo adduser <username> dialout
$ sudo chmod a+rw /dev/ttyACM0
$ sudo udevadm trigger

## Arduino Script
arduino-cli compile -b arduino:avr:uno -p /dev/ttyACM0 -u
arduino-cli monitor -p /dev/ttyACM0
lsof /dev/ttyACM0
sudo kill -9 $(lsof -t /dev/ttyACM0)

## Python Script Background
nohup python3 -u webstreaming.py --ip 0.0.0.0 --port 5323 > python.log 2>&1 &
kill -9 [pid]
```