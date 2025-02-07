#
# Thermostat - This is the Python code used to demonstrate
# the functionality of the thermostat that we have prototyped throughout
# the course.
#
# This code works with the test circuit that was built for module 7.
#
# Functionality:
#
# The thermostat has three states: off, heat, cool
#
# The lights will represent the state that the thermostat is in.
#
# If the thermostat is set to off, the lights will both be off.
#
# If the thermostat is set to heat, the Red LED will be fading in
# and out if the current temperature is below the set temperature;
# otherwise, the Red LED will be on solid.
#
# If the thermostat is set to cool, the Blue LED will be fading in
# and out if the current temperature is above the set temperature;
# otherwise, the Blue LED will be on solid.
#
# One button will cycle through the three states of the thermostat.
#
# One button will raise the setpoint by a degree.
#
# One button will lower the setpoint by a degree.
#
# The LCD display will display the date and time on one line and
# alternate the second line between the current temperature and
# the state of the thermostat along with its set temperature.
#
# The Thermostat will send a status update to the TemperatureServer
# over the serial port every 30 seconds in a comma delimited string
# including the state of the thermostat, the current temperature
# in degrees Fahrenheit, and the setpoint of the thermostat.
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1          Initial Development
#------------------------------------------------------------------

from datetime import datetime
from math import floor
from threading import Thread
from time import sleep

import adafruit_ahtx0
import adafruit_character_lcd.character_lcd as characterlcd
import board
import digitalio
import serial
from gpiozero import PWMLED, Button
from statemachine import State, StateMachine

DEBUG = True

# Setup I2C and temperature sensor
i2c = board.I2C()
thSensor = adafruit_ahtx0.AHTx0(i2c)

# Setup serial communication
ser = serial.Serial(
    port='/dev/ttyS0',       # For older Pis, this may be '/dev/ttyAMA0'
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# Setup our two LEDs on GPIO 18 (red) and GPIO 23 (blue)
redLight = PWMLED(18)
blueLight = PWMLED(23)

##
## ManagedDisplay - Class to manage the 16x2 LCD display.
##
class ManagedDisplay():
    def __init__(self):
        # Setup the six GPIO lines for the LCD.
        self.lcd_rs = digitalio.DigitalInOut(board.D17)
        self.lcd_en = digitalio.DigitalInOut(board.D27)
        self.lcd_d4 = digitalio.DigitalInOut(board.D5)
        self.lcd_d5 = digitalio.DigitalInOut(board.D6)
        self.lcd_d6 = digitalio.DigitalInOut(board.D13)
        self.lcd_d7 = digitalio.DigitalInOut(board.D26)

        # Set display size: 16 columns x 2 rows
        self.lcd_columns = 16
        self.lcd_rows = 2

        # Initialize the LCD class
        self.lcd = characterlcd.Character_LCD_Mono(
            self.lcd_rs, self.lcd_en,
            self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7,
            self.lcd_columns, self.lcd_rows
        )
        self.lcd.clear()

    def cleanupDisplay(self):
        self.lcd.clear()
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()

    def clear(self):
        self.lcd.clear()

    def updateScreen(self, message):
        # Clear the display and update with the new message.
        self.lcd.clear()
        self.lcd.message = message

# Initialize our display
screen = ManagedDisplay()

##
## TemperatureMachine - A state machine to manage the thermostat.
##
class TemperatureMachine(StateMachine):
    off = State(initial=True)
    heat = State()
    cool = State()

    # Default temperature setPoint (in °F)
    setPoint = 72

    # Define the event to cycle between states.
    cycle = (
        off.to(heat) |
        heat.to(cool) |
        cool.to(off)
    )

    def on_enter_heat(self):
        if DEBUG:
            print("* Changing state to heat")
        # When entering heat, update the LED behavior.
        self.updateLights()

    def on_exit_heat(self):
        # Turn off red LED when leaving heat state.
        redLight.off()

    def on_enter_cool(self):
        if DEBUG:
            print("* Changing state to cool")
        self.updateLights()

    def on_exit_cool(self):
        # Turn off blue LED when leaving cool state.
        blueLight.off()

    def on_enter_off(self):
        if DEBUG:
            print("* Changing state to off")
        # Turn off both LEDs.
        redLight.off()
        blueLight.off()

    def processTempStateButton(self):
        if DEBUG:
            print("Cycling Temperature State")
        # Trigger the state machine event to cycle to the next state.
        self.cycle()
        self.updateLights()

    def processTempIncButton(self):
        if DEBUG:
            print("Increasing Set Point")
        # Increase the setPoint by one degree.
        self.setPoint += 1
        self.updateLights()

    def processTempDecButton(self):
        if DEBUG:
            print("Decreasing Set Point")
        # Decrease the setPoint by one degree.
        self.setPoint -= 1
        self.updateLights()

    def updateLights(self):
        # Get the current temperature (rounded down to an integer).
        temp = floor(self.getFahrenheit())
        # Start by turning off both LEDs.
        redLight.off()
        blueLight.off()

        if DEBUG:
            print(f"State: {self.current_state.id}")
            print(f"SetPoint: {self.setPoint}")
            print(f"Temp: {temp}")

        # Update LED behavior based on state and temperature
        if self.current_state == self.heat:
            if temp < self.setPoint:
                # Temperature is below the setpoint; pulse the red LED.
                redLight.pulse()
            else:
                # Temperature meets/exceeds the setpoint; solid red LED.
                redLight.on()
        elif self.current_state == self.cool:
            if temp > self.setPoint:
                # Temperature is above the setpoint; pulse the blue LED.
                blueLight.pulse()
            else:
                blueLight.on()
        elif self.current_state == self.off:
            # Off state: make sure both LEDs remain off.
            redLight.off()
            blueLight.off()

    def run(self):
        # Start the display management in its own thread.
        myThread = Thread(target=self.manageMyDisplay)
        myThread.start()

    def getFahrenheit(self):
        # Convert sensor reading (°C) to °F.
        t = thSensor.temperature
        return ((9 / 5) * t) + 32

    def setupSerialOutput(self):
        # Create a comma-delimited string: state, current temp, and setPoint.
        state_str = self.current_state.id
        temp = floor(self.getFahrenheit())
        output = f"{state_str},{temp},{self.setPoint}"
        return output

    # Flag used to stop the display thread
    endDisplay = False

    def manageMyDisplay(self):
        counter = 1
        altCounter = 1
        while not self.endDisplay:
            if DEBUG:
                print("Processing Display Info...")

            current_time = datetime.now()
            # First line: current date and time (truncated to fit the display)
            lcd_line_1 = current_time.strftime("%Y-%m-%d %H:%M:%S")[:screen.lcd_columns]

            # Second line: alternate between current temperature and state info
            if altCounter < 6:
                temp = floor(self.getFahrenheit())
                lcd_line_2 = f"Temp: {temp}F"
            else:
                lcd_line_2 = f"State: {self.current_state.id} SP:{self.setPoint}"
            
            lcd_line_2 = lcd_line_2[:screen.lcd_columns]
            display_message = lcd_line_1 + "\n" + lcd_line_2

            screen.updateScreen(display_message)

            altCounter += 1
            if altCounter >= 11:
                self.updateLights()
                altCounter = 1

            if DEBUG:
                print(f"Counter: {counter}")
            # Every 30 seconds, send a status update over the serial port.
            if (counter % 30) == 0:
                serial_output = self.setupSerialOutput()
                ser.write(serial_output.encode())
                counter = 1
            else:
                counter += 1

            sleep(1)
        screen.cleanupDisplay()

# Create the state machine and start the display thread.
tsm = TemperatureMachine()
tsm.run()

# Configure the GPIO buttons and assign the respective functions.
greenButton = Button(24)
greenButton.when_pressed = tsm.processTempStateButton

redButton = Button(25)
redButton.when_pressed = tsm.processTempIncButton

blueButton = Button(12)
blueButton.when_pressed = tsm.processTempDecButton

# Main loop: run until a keyboard interrupt occurs.
repeat = True
while repeat:
    try:
        sleep(30)
    except KeyboardInterrupt:
        print("Cleaning up. Exiting...")
        repeat = False
        tsm.endDisplay = True
        sleep(1)
