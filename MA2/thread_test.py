from threading import Thread


def sprint():
    while True:
        print("A")


def aprint():
    while True:
        print("B")


thread = Thread(target=sprint)
thread.start()


thread = Thread(target=aprint)
thread.start()
