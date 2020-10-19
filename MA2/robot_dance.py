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
from Lidar import *
from log import Logger

#! close unused thread?

os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")

ERROR_ANGLE = 2
ERROR_DISTANCE = 3
PURPLE = [(255, 0, 255)]
RED = [(255, 0, 0)]
BLUE = [(0, 0, 255)]

log = Logger()


@dataclass
class Position:
    x: float
    y: float


class Thymio:
    def __init__(self, particle_filter):

        log.warn("Initialisation")
        log.warn("bus initialisation..")

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        self.asebaNetworkObject = bus.get_object("ch.epfl.mobots.Aseba", "/")

        log.aseba("Network object init..")
        self.asebaNetwork = dbus.Interface(
            self.asebaNetworkObject, dbus_interface="ch.epfl.mobots.AsebaNetwork"
        )

        log.aseba("Load file")
        self.asebaNetwork.LoadScripts(
            "thympi.aesl", reply_handler=self.dbusError, error_handler=self.dbusError
        )

        self.pf = particle_filter

        log.warn("Gender attribution")
        self.gender = randint(1, 2)
        # self.set_color(RED if self.gender else BLUE)

        log.warn("Start Growing confidence...")
        self.confidence = 0
        self.growConfidence()

        log.warn('Start sensing thread')
        self.threadSense = Thread(target=self.sense)
        self.threadSense.start()

        log.warn("Start communication")
        self.startCommunication()
        self.sendInformation()
        self.receiveInformation()

        self.hasPartner = False

        self.dancefloor = [Position(.4, .3), Position(.4, -.3), Position(-.4, .3),
                           Position(-.4, -.3)]  # dancefloor position

        self.markers = [Position(.98, -.60), Position(.98, .60),
                        Position(-.98, .60), Position(-.98, -.60)]

        self.aseba = self.asebaNetwork

        self.benchwarm()

    def set_color(self, color):
        self.asebaNetwork.SendEventName("led.top", color)

    def setup(self):
        return self.asebaNetwork

    def stopAsebamedulla(self):
        os.system("pkill -n asebamedulla")

    def dbusError(self, e):
        log.error("dbus error: %s" % str(e))

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

    def sense(self):
        while True:
            self.prox_horizontal = self.aseba.GetVariable(
                "thymio-II", "prox.horizontal")

    def is_there_an_obstacle_ahead(self):
          # adapt values depending on distance we want to keep from robots and light
        if(self.prox_horizontal[2] >= 2900 and self.prox_horizontal[1] >= 1500) or (self.prox_horizontal[2] >= 2900 and self.prox_horizontal[3] >= 1500) or (self.prox_horizontal[2] >= 2900 and self.prox_horizontal[1] >= 1500 and self.prox_horizontal[3] >= 1500):
            log.warn("Obstacle encountered")
            return True
        else:
            return False

    # Stop the robot's motion
    def stop(self):
        left_wheel = 0
        right_wheel = 0
        self.aseba.SendEventName("motor.target", [left_wheel, right_wheel])

    def benchwarm(self):
        log.warn("Benchwarm..")
        while self.confidence <= 10:
            if(self.rx > 2):
                self.set_color(PURPLE)
                self.dance(self.rx)
        self.wander()

    def mate(self):
        log.warn("Mate process started.")
        while not self.hasPartner:
            sleep(0.1)
            #! might be very sketchy (the sense thread)
            if self.is_there_an_obstacle_ahead():
                if self.rx < 3 and not self.gender:
                    log.warn("Partner found")
                    log.robot("T'as de beaux yeux tu sais")
                    log.robot("*Pokemon battle music intensifies*")
                    danceFloor = randint(3, 6)
                    for _ in range(5):
                        self.sendInformation(danceFloor)
                    log.warn("Dance floor sent to partner (5x)")
                    self.set_color(PURPLE)
                    self.hasPartner = True

    def wander(self):
        log.warn("Enough confidence, now wandering.")
        self.thread = Thread(target=self.mate)
        self.thread.start()
        while not self.hasPartner:
            for marker in self.markers:
                self.goto(marker)
        self.dance(dancefloor)

    def rotate(self):
        step = 1
        self.aseba.SendEventName("motor.target", [200, 200])
        sleep(10)  # ! depends on how much speeds and time it needs to rotate 1 degree + IT HAS TO MOVE ON A SPECIFIC SIDE, IT DEPENDS ON HOW WE CALULCATE THE ANGLE
        self.stop()
        # TODO move robot physically from 1 degree
        self.pf.set_delta(0, 0, step)

    def forward(self):
        # TODO forward physically from 1 centimeter
        self.aseba.SendEventName("motor.target", [200, 200])
        sleep(10)  # ! depends on how much speeds and time it needs to move 1cm
        self.stop()
        step = 0.01

        #! is that correct?
        dx, dy = polarToCart(step, robot.angle)
        self.pf.set_delta(dx, dy,  0)

    def is_close_to_position(self, robot, pos):
        return True if abs(robot.x - pos.x) < ERROR_DISTANCE and abs(robot.y - pos.y) < ERROR_DISTANCE else False

    def is_close_to_angle(self, robot, angle):
        return True if abs(robot.angle - angle) < ERROR_ANGLE else False

    def goto(self, position):
        robot = self.pf.position

        log.warn("From ", robot.x, robot.y, robot.angle,
                 " go to ", position.x, " ", position.y)

        rotation = caculate_angle_to_dest(
            robot.x, robot.y, robot.angle, position.x, position.y)

        while not self.is_close_to_angle(robot, rotation) and not self.hasPartner and not self.is_there_an_obstacle_ahead():
            self.rotate()

        while not self.is_close_to_position(robot, position) and not self.hasPartner and not self.is_there_an_obstacle_ahead():
            self.forward()

        # if robot in front, sleep for 2sec, the mating thread is still going and does its job.
        if self.is_there_an_obstacle_ahead():
            sleep(2)
            if not self.hasPartner:
                # TODO hardcode avoidence position
                #  Recall function to keep moving to the same marker / position
                self.goto(position)

    def dance(self, df):
        log.robot("Yaaah, let's go dance to ", df, "!")

        #! Has to set it to false
        self.hasPartner = False
        goto(self.dancefloor[df-3])
        # dance
        self.rest()

    def rest(self):
        log.robot("Whoo, I am exhausted, I will rest for now.")
        # goes to the wall and remain still
        self.stop()
        pass


if __name__ == '__main__':
    rest = False
    try:
        log.warn("Setting up lidar")
        lidar = Lidar()
        log.warn("Setting up ParticleFiltering")
        pf = ParticleFiltering(lidar)
        robot = Thymio(pf)

        # # Benchwarm
        # log.warn("Benchwarm..")
        # while robot.confidence <= 10:
        #     comm_value = robot.rx
        #     if(comm_value > 2):
        #         robot.dance(comm_value)
        # self.wander()

    except KeyboardInterrupt:
        log.error("Keyboard interrupt")
        log.error("Stopping robot")
        exit_now = True
        sleep(1)
        os.system("pkill -n asebamedulla")
        log.error("asebamodulla killed")
