#!/usr/bin/python3
import dbus.mainloop.glib
import dbus
from threading import Thread
from time import sleep
import threading
from random import randint
import os
from mtcarlo import *

# initialize asebamedulla in background and wait 0.3s to let
# asebamedulla startup
os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")


class Thymio:
    def __init__(self):
        self.aseba = self.setup()

    def setup(self):
        print("Setting up")
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        self.asebaNetworkObject = bus.get_object("ch.epfl.mobots.Aseba", "/")

        self.asebaNetwork = dbus.Interface(
            asebaNetworkObject, dbus_interface="ch.epfl.mobots.AsebaNetwork"
        )
        # load the file which is run on the thymio
        self.asebaNetwork.LoadScripts(
            "thympi.aesl", reply_handler=self.dbusError, error_handler=self.dbusError
        )

        # give th robot a gender, a change its color accordingly
        self.gender = self.selectGender()
        self.aseba.SendEventName(
            "led.top", (255, 0, 0) if gender else (0, 0, 255))

        self.confidence = 0
        self.confidence()

        # scanning_thread = Process(target=robot.drive, args=(200,200,))
        return asebaNetwork

    def stopAsebamedulla(self):
        os.system("pkill -n asebamedulla")

    def dbusError(self, e):
        # dbus errors can be handled here.
        # Currently only the error is logged. Maybe interrupt the mainloop here
        print("dbus error: %s" % str(e))

    def selectGender(self):
        return randint(0, 1)

    # Periodically increase confidence
    def confidence(self):
        self.confidence += 1
        threading.Timer(2, confidence).start()

    def getConfidence(self):
        return self.confidence

    def resetConfidence(self):
        self.confidence = 0

    def startCommunication(self):
        # this enables the prox.com communication channels
        self.asebaNetwork.SendEventName("prox.comm.enable", [1])
        # This enables the prox.comm rx value to zero, gets overwritten when receiving a value
        self.asebaNetwork.SendEventName("prox.comm.rx", [0])

    # Remeber to change tx number when finding a partner
    def sendInformation(self, number):
        self.asebaNetwork.SendEventName("prox.comm.tx", [number])

    # Remeber to change rx number after confirming a partner. This can be done the same way as the tx :)
    def receiveInformation(self):
        self.rx = asebaNetwork.GetVariable("thymio-II", "prox.comm.rx")
        print(rx[0])

    # Move the robot
    def step(self, left, right):
        self.aseba.SendEventName("motor.target", [left, right])

    # Stop the robot's motion
    def stop(self):
        left_wheel = 0
        right_wheel = 0
        self.aseba.SendEventName("motor.target", [left_wheel, right_wheel])

    def wander(self):
        pass

    def dance(self):
        self.aseba.SendEventName(
            "led.top", (255, 0, 255))


if __name__ == '__main__':
    rest = False
    try:
        l = ParticleFiltering()
        pos = l.get_x_y_alpha()
        robot = Thymio()
        while not rest:
            if robot.getConfidence() > 10:
                robot.resetConfidence()
                robot.wander()
                robot.dance()
                robot.rest()
                rest = True

        # Put the sens method in a thread and run it
        # thread = Thread(target=robot.sens)
        # thread.daemon = True
        # thread.start()

    except KeyboardInterrupt:
        print("Stopping robot")
        exit_now = True
        sleep(1)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")
