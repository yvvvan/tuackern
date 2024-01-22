import subprocess

# determine desired usb device

# to disable
subprocess.run(['echo', '0', '>' '/sys/bus/usb/devices/usbX/power/autosuspend_delay_ms']) 
subprocess.run(['echo', 'auto', '>' '/sys/bus/usb/devices/usbX/power/control']) 
# to enable
subprocess.run(['echo', 'on', '>' '/sys/bus/usb/devices/usbX/power/control']) 
