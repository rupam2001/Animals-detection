
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
import time
class PhysicalOutput:
    def __init__(self, buzzer_pin=16, led_pin=8) -> None:
        self.buzzer = buzzer_pin
        self.led_pin = led_pin
        GPIO.setwarnings(False) 
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.led_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.buzzer, GPIO.OUT)
        self.duration = 5  # in seconds
        self.start_time = 0
        

    def start(self):
        self.start_time = time.time()
        self.startBuzzer()
        self.startLED()


    def stop(self):
        if self.start_time + self.duration < time.time():
            self.stopBuzzer()
            self.stopLED()


    def startBuzzer(self):
        GPIO.output(self.buzzer, GPIO.HIGH)
    def stopBuzzer(self):
        GPIO.output(self.buzzer, GPIO.LOW)
    
    def startLED(self):
        GPIO.output(self.led_pin, GPIO.HIGH)
    def stopLED(self):
        GPIO.output(self.led_pin, GPIO.LOW)


