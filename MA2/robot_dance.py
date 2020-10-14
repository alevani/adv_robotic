#!/usr/bin/python3
import dbus.mainloop.glib
import dbus
from threading import Thread
from time import sleep
import threading
from random import randint
from numpy import arctan
import os
from mtcarlo import *

# initialize asebamedulla in background and wait 0.3s to let
# asebamedulla startup
os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")


class Thymio:
    def __init__(self):
        print("Setting up")
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        self.asebaNetworkObject = bus.get_object("ch.epfl.mobots.Aseba", "/")

        self.asebaNetwork = dbus.Interface(
            self.asebaNetworkObject, dbus_interface="ch.epfl.mobots.AsebaNetwork"
        )
        # load the file which is run on the thymio
        self.asebaNetwork.LoadScripts(
            "thympi.aesl", reply_handler=self.dbusError, error_handler=self.dbusError
        )

        # give th robot a gender, a change its color accordingly
        self.gender = self.selectGender()
        self.asebaNetwork.SendEventName(
            "led.top", (255, 0, 0) if self.gender else (0, 0, 255))

        self.confidence = 0
        self.growConfidence()

        self.particleFilter = ParticleFiltering()
        self.particleFilter.set_xya(0, 0, 0)

        print('start particle filtering thread')
        self.thread = Thread(target=self.particleFilter.Localize)
        self.thread.daemon = True
        self.thread.start()

        self.dancefloor = [(.4, .3), (.4, -.3), (-.4, .3),
                           (-.4, -.3)]  # dancefloor position
        self.aseba = self.asebaNetwork

    def setup(self):
        return self.asebaNetwork

    def stopAsebamedulla(self):
        os.system("pkill -n asebamedulla")

    def dbusError(self, e):
        # dbus errors can be handled here.
        # Currently only the error is logged. Maybe interrupt the mainloop here
        print("dbus error: %s" % str(e))

    def selectGender(self):
        return randint(0, 1)

    # Periodically increase confidence
    def growConfidence(self):
        self.confidence += 1
        # rx = self.receiveInformation()
        rx = 1
        if not rx == 0:  # ! change on depending what RX receive
            threading.Timer(2, self.growConfidence).start()
        else:
            self.dance(rx)

    def getConfidence(self):
        return self.confidence

    def resetConfidence(self):
        self.confidence = 0

    # def startCommunication(self):
    #     # this enables the prox.com communication channels
    #     self.asebaNetwork.SendEventName("prox.comm.enable", [1])
    #     # This enables the prox.comm rx value to zero, gets overwritten when receiving a value
    #     self.asebaNetwork.SendEventName("prox.comm.rx", [0])

    # # Remeber to change tx number when finding a partner
    # def sendInformation(self, number):
    #     self.asebaNetwork.SendEventName("prox.comm.tx", [number])

    # # Remeber to change rx number after confirming a partner. This can be done the same way as the tx :)
    # def receiveInformation(self):
    #     self.rx = asebaNetwork.GetVariable("thymio-II", "prox.comm.rx")
    #     return rx[0]

    # Move the robot
    def step(self, left, right, angle):
        # self.particleFilter.set_xya(left, right, angle)
        self.aseba.SendEventName("motor.target", [left, right])
        sleep(10)
        self.stop()

    # Stop the robot's motion
    def stop(self):
        left_wheel = 0
        right_wheel = 0
        self.aseba.SendEventName("motor.target", [left_wheel, right_wheel])

    def wander(self):
        pos = self.particleFilter.position
        lidar = self.particleFilter.get_lidar_values
        #     # self.rest()

    def dance(self, d):
        #! goto dancefloor
        dfPos = self.dancefloor[d]
        self.stop()
        pass

    def find_angle(self, pos1, pos2):
        dy = abs(pos2[1] - pos1[1])
        dx = abs(pos2[0] - pos1[0])
        alpha = arctan(dy/dx)
        return 180 - alpha - pos1[2]

    def rotate(self):
        # TODO move robot from 1 degree
        pos = self.particleFilter.position
        pos[2] += 1
        self.particleFilter.set_xya(pos)

    def forward(self):
        # TODO forward from .5 centimeter?
        pos = self.particleFilter.position
        pos[0] += 1  # TODO calculate with angle, +1 is wrong
        pos[1] += 1  # TODO calculate with angle, +1 is wrong
        self.particleFilter.set_xya(pos)

    def goto(self, x, y):
        pos = self.particleFilter.position
        rotation = self.find_angle(pos, (x, y))

        while pos[2] != rotation:
            pos = self.particleFilter.position
            self.rotate()
        while (pos[0], pos[1]) != (x, y):
            pos = self.particleFilter.position
            self.forward()


def dance(self):
        # Robot become purple
    self.aseba.SendEventName(
        "led.top", (255, 0, 255))


if __name__ == '__main__':
    rest = False
    try:
        robot = Thymio()
        robot.step(200, 200, 0)
        while not rest:
            pass
            # if robot.getConfidence() > 10:
            #     robot.resetConfidence()
            #     # robot.wander()
            #     rest = True

    except KeyboardInterrupt:
        print("Stopping robot")
        exit_now = True
        sleep(1)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")
