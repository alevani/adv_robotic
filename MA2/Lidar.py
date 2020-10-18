from adafruit_rplidar import RPLidar
import threading
from math import floor

NB_STOP = 10


class Lidar:
    def __init__(self, nb_stop=NB_STOP):
        self.nb_stop = nb_stop
        self.nb_samples = 360 / nb_stop

        PORT_NAME = '/dev/ttyUSB0'
        self.lidar = RPLidar(None, PORT_NAME)

        print('start lidar scan thread')
        self.scanner_thread = threading.Thread(target=self.lidarScan)
        self.scanner_thread.daemon = True
        self.scanner_thread.start()

    def lidarScan(self):
        #! while true?
        print("Starting background lidar scanning")
        for scan in self.lidar.iter_scans():
            for (_, angle, distance) in scan:
                self.scan_data[min([359, floor(angle)])] = distance

    def get_scan_data(self):
        return [self.scan_data[x] / 1000 for x in list(range(0, 360, self.nb_samples))]
