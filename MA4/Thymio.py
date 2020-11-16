#!/usr/bin/python3
import dbus.mainloop.glib
import dbus
from time import sleep

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

        sleep(3)

    def dbusError(self, e):
        print("dbus error: %s" % str(e))

    def sense_floor(self):
        return 0,0

    def drive(self, l, r):
        self.asebaNetwork.SendEventName('motor.target', [l, r])
        sleep(.2)

    def stop(self):
        left_wheel = 0
        right_wheel = 0
        self.asebaNetwork.SendEventName(
            "motor.target", [left_wheel, right_wheel])



