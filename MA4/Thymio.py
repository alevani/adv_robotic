#!/usr/bin/python3
import dbus.mainloop.glib
import dbus
from time import sleep
import globals

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
        left_state = 0
        right_state = 0

        if raw_left > globals.wall_bot_limit and raw_left < globals.wall_top_limit:
            left_state = 1
        # elif raw_left > globals.safe_zone_bot_limit and raw_left < globals.safe_zone_top_limit:
        #     left_state = 2
        if raw_right > globals.wall_bot_limit and raw_right < globals.wall_top_limit:
            right_state = 1
        # elif raw_right > globals.safe_zone_bot_limit and raw_right < globals.safe_zone_top_limit:
        #     right_state = 2
        return (left_state, right_state) # 0,1,2 == (nowall, wall, safezone)

    def drive(self, l, r, time=0):
        self.asebaNetwork.SendEventName('motor.target', [l, r])
        sleep(time)

    def set_led(self, color: str):
        # TODO
        pass

    def stop_transmission_thread(second: int):
        # TODO with thread
        pass

    def receiver_thread(self):
        # TODO
        # self.reveiver = aseba..
        pass

    def wait_in_safe_zone(self):
        # stop transmiting 2
        # wait for sense 2
        # if 2: drive forward( 5 sec )
        # retrasnmit 2
        pass

    def stop(self):
        left_wheel = 0
        right_wheel = 0
        self.asebaNetwork.SendEventName(
            "motor.target", [left_wheel, right_wheel])



