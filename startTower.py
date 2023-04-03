import time
from flask import Flask, request
import threading
from flask import render_template

import RPi.GPIO as GPIO

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO_PIN = 18
GPIO.setup(GPIO_PIN, GPIO.OUT)

countdown_timer = 180
timer_paused = True
timer_reset = False
start_points = {3: 180, 4: 240, 5: 300}
time_to_start_again = 600

def countdown():
    global countdown_timer, timer_paused, timer_reset, time_to_start_again
    while True:
        if not timer_paused:
            if countdown_timer > 0:
                time.sleep(1)
                countdown_timer -= 1
                minutes, seconds = divmod(countdown_timer, 60)
                if seconds == 0:
                    print("GPIO.HIGH")
                    GPIO.output(GPIO_PIN, GPIO.HIGH)
                    time.sleep(1)
                    print("GPIO.LOW")
                    GPIO.output(GPIO_PIN, GPIO.LOW)
            else:
                print("GPIO.HIGH")
                GPIO.output(GPIO_PIN, GPIO.HIGH)
                time.sleep(2)
                print("GPIO.LOW end!!!")
                GPIO.output(GPIO_PIN, GPIO.LOW)
                timer_reset = True
                time.sleep(time_to_start_again)
        else:
            time.sleep(1)

        if timer_reset:
            countdown_timer = start_points[3]
            timer_paused = True
            timer_reset = False

timer_thread = threading.Thread(target=countdown)
timer_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_timer():
    global timer_paused
    timer_paused = False
    return "Countdown started."

@app.route('/pause', methods=['POST'])
def pause_timer():
    global timer_paused
    timer_paused = True
    return "Countdown paused."

@app.route('/stop', methods=['POST'])
def stop_timer():
    global timer_paused, timer_reset
    timer_paused = True
    timer_reset = True
    return "Countdown stopped and reset."

@app.route('/format', methods=['GET'])
def set_format():
    global countdown_timer, timer_paused
    minutes = int(request.args.get('type', 3))
    if minutes in start_points:
        countdown_timer = start_points[minutes]
        timer_paused = True
        return f"Countdown format set to {minutes} minutes."
    else:
        return "Invalid format. Please use 3, 4, or 5 minutes.", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
