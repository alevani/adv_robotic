from adafruit_rplidar import RPLidar
import threading
from math import floor
from time import sleep

NB_STOP = 12


class Lidar:
    def __init__(self, nb_stop=NB_STOP):
        self.nb_stop = nb_stop
        self.nb_samples = int(360 / nb_stop)

        PORT_NAME = '/dev/ttyUSB0'
        self.lidar = RPLidar(None, PORT_NAME)

        self.scanner_thread = threading.Thread(target=self.lidarScan)
        self.scanner_thread.start()
        self.scan_data = [0]*360

    def lidarScan(self):
        while True:
            for scan in self.lidar.iter_scans():
                for (_, angle, distance) in scan:
                    self.scan_data[min([359, floor(angle)])] = distance

    def get_scan_data(self):
        return [self.scan_data[x] / 1000 for x in list(range(0, 360, self.nb_samples))]


l = Lidar()
while True:
    sleep(0.5)
    print(l.get_scan_data())
