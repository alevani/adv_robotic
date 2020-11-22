from adafruit_rplidar import RPLidar
import threading
from math import floor
from time import sleep
import numpy as np
#! if that change i need to change at other places
NB_STOP = 360


class Lidar:
    def __init__(self, nb_stop=NB_STOP):
        self.nb_stop = nb_stop
        self.nb_samples = int(360 / nb_stop)

        PORT_NAME = '/dev/ttyUSB0'
        self.lidar = RPLidar(None, PORT_NAME)
        sleep(2)
        self.scanner_thread = threading.Thread(target=self.lidarScan)
        self.scanner_thread.start()
        self.scan_data = [0]*360

    def lidarScan(self):
        while True:
            for scan in self.lidar.iter_scans():
                for (_, angle, distance) in scan:
                    self.scan_data[min([359, floor(angle)])] = distance

    def get_scan_data(self):
        return [self.scan_data[x] / 1000 if self.scan_data[x] != 0.0 else 5000 for x in list(range(0, 360, self.nb_samples))]


# l = Lidar()


# while True:
#     sleep(.5)
#     data = l.get_scan_data()

#     print(data)
#     index = np.argmin(data)
#     print("index of rotation: ", index)
#     if index < 180:
#         print("LEFT")
#         new_index = 180 - index
#         print("index after ratio: ", new_index)
#         print("speed left: ", 1000 - (new_index * 1000 / 180))
#     elif index > 179:
#         print("RIGHT")
#         new_index = index - 180
#         print("index after ratio: ", new_index)
#         print("speed right: ", 1000 - (new_index * 1000 / 180))
