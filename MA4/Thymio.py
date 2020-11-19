#!/usr/bin/python3
import dbus.mainloop.glib
import dbus
from time import sleep
import globals
import threading


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
        self.receiver = None
        self.ground_sensors = None

        sleep(3)
        self.sense()

        self.startCommunication()
        self.info_to_send = 1000
        self.sendInformation()
        self.receiveInformation()

    ######### COMMUNICATION #########
    def set_info_to_send(self, value):
        self.info_to_send = value

    def startCommunication(self):
        self.asebaNetwork.SendEventName("prox.comm.enable", [1])
        self.asebaNetwork.SendEventName("prox.comm.rx", [0])

    def sendInformation(self):
        self.asebaNetwork.SendEventName("prox.comm.tx", [self.info_to_send])
        threading.Timer(.1, self.sendInformation).start()

    def receiveInformation(self):
        self.rx = self.asebaNetwork.GetVariable("thymio-II", "prox.comm.rx")
        threading.Timer(.1, self.receiveInformation).start()

    def restart(self):
        threading.Timer(5, self.set_info_to_send, [2]).start()

   ###################################

    def sense(self):
        self.prox_horizontal = self.asebaNetwork.GetVariable(
            "thymio-II", "prox.horizontal")
        threading.Timer(.1, self.sense).start()

    def get_prox_state(self):
        self.SC = self.prox_horizontal[2]  # Sensor Central
        self.SL = self.prox_horizontal[0]  # Sensor Left
        self.SR = self.prox_horizontal[4]  # Sensor Right

        detect = 10

        if self.SL > detect and self.SR > detect:
            return (1, 0, 1)
        elif self.SR > detect:
            return (0, 0, 1)
        elif self.SL > detect:
            return (1, 0, 0)
        elif self.SC > detect:
            return (0, 1, 0)
        else:
            return (0, 0, 0)

        # elif self.SC > 0 and self.SR > 0:
        #     return (0, 1, 1)
        # elif self.SC > 0 and self.SL > 0:
        #     return (1, 1, 0)

    def dbusError(self, e):
        print("dbus error: %s" % str(e))

    def sense_ground(self):
        sensors = self.asebaNetwork.GetVariable(
            "thymio-II", "prox.ground.reflected")
        return sensors[0], sensors[1]

    def sense_ground_thread(self):
        self.ground_sensors = self.asebaNetwork.GetVariable(
            "thymio-II", "prox.ground.reflected")
        threading.Timer(.01, self.sense_ground_thread).start()

    def get_sensor_state(self):
        raw_left, raw_right = self.sense_ground()
        # print("raw_right", raw_right, "raw_left", raw_left)
        left_state = 0
        right_state = 0

        if raw_left > globals.wall_bot_limit and raw_left < globals.wall_top_limit:
            left_state = 1
        elif raw_left > globals.safe_zone_bot_limit and raw_left < globals.safe_zone_top_limit:
            left_state = 2
        if raw_right > globals.wall_bot_limit and raw_right < globals.wall_top_limit:
            right_state = 1
        elif raw_right > globals.safe_zone_bot_limit and raw_right < globals.safe_zone_top_limit:
            right_state = 2
        return (left_state, right_state)  # 0,1,2 == (nowall, wall, safezone)

    def drive(self, l, r, time=0):
        self.asebaNetwork.SendEventName('motor.target', [l, r])
        # sleep(time)

    def set_led(self, color):
        self.asebaNetwork.SendEventName("leds.bottom.right", color)
        self.asebaNetwork.SendEventName("leds.bottom.left", color)
        self.asebaNetwork.SendEventName("leds.top", color)
        self.asebaNetwork.SendEventName("leds.buttons", color)
        self.asebaNetwork.SendEventName("leds.color", color)

    def stop(self):
        left_wheel = 0
        right_wheel = 0
        self.asebaNetwork.SendEventName(
            "motor.target", [left_wheel, right_wheel])
