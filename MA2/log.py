from datetime import datetime


class Logger:

    def __init__(self):
        super().__init__()

    def time(self):
        now = datetime.now()
        return now.strftime("%H:%M:%S")

    def warn(self, msg):
        # print("[", self.time, "][WARN]> ", msg)
        print("[WARN]> ", msg)

    def robot(self, msg):
        print("> ", msg)

    def error(self, msg):
        # print("[", self.time, "][ERROR]> ", msg)
        print("[ERROR]> ", msg)

    def aseba(self, msg):
        # print("[", self.time, "][ASEBA]> ", msg)
        print("[ASEBA]> ", msg)

    def info(self, msg):
        # print("[", self.time, "][ASEBA]> ", msg)
        print("[INFO]> ", msg)
