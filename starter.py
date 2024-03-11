import time
import RPi.GPIO as GPIO
import sys
import subprocess

GPIO.setwarnings(False)

def ignition_start():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)
    try:
        while True:
            GPIO.output(11, GPIO.LOW)  # Turn on ignition
            GPIO.output(15, GPIO.LOW)
            # Insert additional code here if needed
            time.sleep(1)  # Example: wait for 1 second
            break  # Exit the loop after some time
    finally:
        subprocess.call(['python', 'drowsiness.py'])  # Replace 'path_to_your_script.py' with the actual path to your file

ignition_start()
