#! /usr/bin/env python3.7
import Thymio
from random import randint

def main():
    thymio = Thymio()
    while True:
        left = randint(-1000, 1000)
        right = randint(-1000, 1000)
        thymio.drive(left, right)

if __name__ == '__main__':
    main()

