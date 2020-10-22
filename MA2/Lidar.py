from adafruit_rplidar import RPLidar
import threading
from math import floor
from log import Logger

NB_STOP = 12


class Lidar:
    def __init__(self, nb_stop=NB_STOP):
        self.log = Logger()
        self.nb_stop = nb_stop
        self.nb_samples = int(360 / nb_stop)

        PORT_NAME = '/dev/ttyUSB0'
        self.lidar = RPLidar(None, PORT_NAME)

        self.log.warn('start lidar scan thread')
        self.scanner_thread = threading.Thread(target=self.lidarScan)
        self.scanner_thread.start()
        self.scan_data = [0]*360

    def lidarScan(self):
        self.log.warn("Starting background lidar scanning")
        while True:
            for scan in self.lidar.iter_scans():
                for (_, angle, distance) in scan:
                    self.scan_data[min([359, floor(angle)])] = distance

    def get_scan_data(self):
        return [self.scan_data[x] / 1000 for x in list(range(0, 360, self.nb_samples))]


class FakeLidar:
    def __init__(self, fake_robot):
        self.fake_robot = fake_robot

    def get_scan_data(self):
        return self.fake_robot.get_simulated_lidar_values()
