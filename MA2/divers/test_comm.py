import dbus.mainloop.glib
import threading
import dbus
from random import randint

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
asebaNetworkObject = bus.get_object("ch.epfl.mobots.Aseba", "/")

gender = randint(1, 2)


asebaNetwork = dbus.Interface(
    asebaNetworkObject, dbus_interface="ch.epfl.mobots.AsebaNetwork"
)


asebaNetwork.LoadScripts(
    "thympi.aesl", reply_handler=dbusError, error_handler=dbusError
)

startCommunication()
sendInformation()
receiveInformation()


def dbusError(self, e):
    print("dbus error: %s" % str(e))


def startCommunication(self):
    asebaNetwork.SendEventName("prox.comm.enable", [1])
    asebaNetwork.SendEventName("prox.comm.rx", [0])


def sendInformation(self):
    asebaNetwork.SendEventName("prox.comm.tx", [gender])
    print("SENT : Gender")
    threading.Timer(.1, sendInformation).start()


def receiveInformation(self):
    rx = asebaNetwork.GetVariable("thymio-II", "prox.comm.rx")
    print("RECEIVED ", rx)
    threading.Timer(.1, receiveInformation).start()
