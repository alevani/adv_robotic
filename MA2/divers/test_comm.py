import dbus.mainloop.glib
import threading
import dbus
from random import randint
from time import sleep

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
asebaNetworkObject = bus.get_object("ch.epfl.mobots.Aseba", "/")

gender = randint(1, 2)
gender = 2


asebaNetwork = dbus.Interface(
    asebaNetworkObject, dbus_interface="ch.epfl.mobots.AsebaNetwork"
)


def dbusError(e):
    print("dbus error: %s" % str(e))


asebaNetwork.LoadScripts(
    "thympi.aesl", reply_handler=dbusError, error_handler=dbusError
)


def startCommunication():
    asebaNetwork.SendEventName("prox.comm.enable", [1])
    asebaNetwork.SendEventName("prox.comm.rx", [0])


def sendInformation():
    asebaNetwork.SendEventName("prox.comm.tx", [gender])
    print("SENT : Gender")
    threading.Timer(.1, sendInformation).start()


def receiveInformation():
    rx = asebaNetwork.GetVariable("thymio-II", "prox.comm.rx")
    print("RECEIVED ", rx)
    threading.Timer(.1, receiveInformation).start()


startCommunication()
sleep(1)
sendInformation()
receiveInformation()
