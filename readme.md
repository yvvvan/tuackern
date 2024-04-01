## TU Stadt Ackern

#### introduce
This is a remote plant care/monitoring project for [TU Stadt ackern](https://moseskonto.tu-berlin.de/moses/verzeichnis/veranstaltungen/veranstaltung.html?veranstaltung=162942) [(Project Workshop)](https://www.tu.berlin/b-nerle/studium-lehre/unser-lehrangebot/ernaehrung-lebensmittelwissenschaft-med/tu-stadt-ackern). It utilizes Python as the backend, Flask for frontend-backend interaction, Raspberry Pi (with camera) and Arduino (with servomotor) as hardware components. 


#### project pages
[Project Manage Page (Notion)](https://gnomeoffice.notion.site/6b3ba5e4e5ee420fad3575e2c5b49d9d?v=779020b5c65d4395a5f65172c7562c2d)

[Project GUI demo (Figma)](https://www.figma.com/proto/xlAXgHyfcqfX7uP4QoJbRc/Gnomeoffice?node-id=8-534&mode=design&t=TJQZ9CMQKE2iicXW-1)

[Project Presentation Page](https://docs.google.com/presentation/d/e/2PACX-1vT7LtkdsemulWmi9v0XBv_Wha8pltVuZP4rhv1q94XMeM143lzYzRkXp3O-83mNx-91wXBiwaGIRCCr/embed?start=false&loop=false&delayms=30000)


#### install
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
