#!/usr/bin/python3
from threading import Thread
from random import randint
import dbus.mainloop.glib
from numpy import arctan
from time import sleep
from mtcarlo import *
from time import time
from utils import *
import threading
import dbus
import os

#! close unused thread?

os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")


class Thymio:
    def __init__(self):
        print("Thymio init...")

        print("[ASEBA] bus init..")
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        self.asebaNetworkObject = bus.get_object("ch.epfl.mobots.Aseba", "/")

        print("[ASEBA] Network object init..")
        self.asebaNetwork = dbus.Interface(
            self.asebaNetworkObject, dbus_interface="ch.epfl.mobots.AsebaNetwork"
        )

        print("[ASEBA] Load file")
        self.asebaNetwork.LoadScripts(
            "thympi.aesl", reply_handler=self.dbusError, error_handler=self.dbusError
        )

        print("Gender attribution")
        self.gender = randint(1, 2)
        # self.asebaNetwork.SendEventName(
        #     "led.top", (255, 0, 0) if self.gender else (0, 0, 255))

        print("Start Growing confidence...")
        self.confidence = 0
        self.growConfidence()

        print("Particle filtering init..")
        self.particleFilter = ParticleFiltering()
        self.particleFilter.set_xya(0, 0, 0)

        print('Start particle filtering thread')
        self.thread = Thread(target=self.particleFilter.Localize)
        self.thread.daemon = True
        self.thread.start()

        print('Start sensing thread')
        self.threadSense = Thread(target=self.sense)
        self.threadSense.daemon = True
        self.threadSense.start()

        print("Start communication")
        self.startCommunication()
        self.sendInformation()
        self.receiveInformation()

        self.hasPartner = False

        self.dancefloor = [(.4, .3), (.4, -.3), (-.4, .3),
                           (-.4, -.3)]  # dancefloor position

        self.markers = [(.98, -.60), (.98, .60), (-.98, .60), (-.98, -.60)]
        self.aseba = self.asebaNetwork

    def setup(self):
        return self.asebaNetwork

    def stopAsebamedulla(self):
        os.system("pkill -n asebamedulla")

    def dbusError(self, e):
        print("dbus error: %s" % str(e))

    # Periodically increase confidence
    def growConfidence(self):
        self.confidence += 1
        threading.Timer(2, self.growConfidence).start()

    def resetConfidence(self):
        self.confidence = 0

    def startCommunication(self):
        self.asebaNetwork.SendEventName("prox.comm.enable", [1])
        self.asebaNetwork.SendEventName("prox.comm.rx", [0])

    # ? Remeber to change tx number when finding a partner -> wuat?
    def sendInformation(self):
        self.asebaNetwork.SendEventName("prox.comm.tx", [self.gender])
        threading.Timer(.1, self.sendInformation).start()

    # Remeber to change rx number after confirming a partner. This can be done the same way as the tx :)
    def receiveInformation(self):
        self.rx = asebaNetwork.GetVariable("thymio-II", "prox.comm.rx")
        threading.Timer(.1, self.receiveInformation).start()

    # TODO do something with it
    def sense(self):
        while True:
            self.prox_horizontal = self.aseba.GetVariable(
                "thymio-II", "prox.horizontal")
            # adapt values depending on distance we want to keep from robots and light
            if(self.prox_horizontal[2] >= 2900 and self.prox_horizontal[1] >= 1500) or (self.prox_horizontal[2] >= 2900 and self.prox_horizontal[3] >= 1500) or (self.prox_horizontal[2] >= 2900 and self.prox_horizontal[1] >= 1500 and self.prox_horizontal[3] >= 1500):
                self.stop()

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

    def benchwarm(self):
        while self.confidence <= 10:
            if(self.rx > 2):
                self.dance(self.rx)
        self.wander()

    def mate(self):
        while not self.hasPartner:
            sleep(0.1)
            if self.rx < 3 and not self.gender:
                danceFloor = randint(3, 6)
                for _ in range(5):
                    self.sendInformation(danceFloor)
                self.hasPartner = True

    def wander(self):
        self.thread = Thread(target=self.mate)
        self.thread.daemon = True
        self.thread.start()
        while not self.hasPartner:
            for marker in self.markers:
                self.goto(marker)
        self.dance(dancefloor)

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
        rotation = caculate_angle_to_dest(pos[2], pos[1], pos[0], x, y)

        # TODO add +-5/10 angle degree
        while pos[2] != rotation and not self.hasPartner:
            pos = self.particleFilter.position
            self.rotate()

        # TODO add +-5cm d'erreur
        while (pos[0], pos[1]) != (x, y) and not self.hasPartner:
            pos = self.particleFilter.position
            self.forward()

    def dance(self, df):
        self.hasPartner = False
        goto(self.dancefloor[df-3])
        # dance
        self.rest()

    def rest(self):
        # goes to the wall and remain still
        pass


if __name__ == '__main__':
    rest = False
    try:
        robot = Thymio()
    except KeyboardInterrupt:
        print("Stopping robot")
        exit_now = True
        sleep(1)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")
