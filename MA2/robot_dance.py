#!/usr/bin/python3
import dbus.mainloop.glib
import dbus
from threading import Thread
from time import sleep
from random import randint
import os

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
        asebaNetworkObject = bus.get_object("ch.epfl.mobots.Aseba", "/")

        asebaNetwork = dbus.Interface(
            asebaNetworkObject, dbus_interface="ch.epfl.mobots.AsebaNetwork"
        )
        # load the file which is run on the thymio
        asebaNetwork.LoadScripts(
            "thympi.aesl", reply_handler=self.dbusError, error_handler=self.dbusError
        )

        # scanning_thread = Process(target=robot.drive, args=(200,200,))
        return asebaNetwork

    def stopAsebamedulla(self):
        os.system("pkill -n asebamedulla")

    def dbusError(self, e):
        # dbus errors can be handled here.
        # Currently only the error is logged. Maybe interrupt the mainloop here
        print("dbus error: %s" % str(e))

# Randomly choose a color and attribute it to the thymio


def benchwarmer():
    color = 0 if randint(0, 1) else 1
    return color


if __name__ == '__main__':
    try:
        robot = Thymio()

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
