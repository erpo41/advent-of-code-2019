#!/usr/bin/python3

class asciifb:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.screenmap = {} #element = (0,0): "#"
    def receiveint(self, n):
        if type(n) != type(int()):
            print("wrong type passed to receiveint")
            exit(1)
        self.screenmap[(self.x,self.y)] = chr(n)
        if n == 10:
            self.y += 1
            self.x = 0
            return
        self.x += 1
    def render(self):
        rx = 0
        ry = 0
        while True: #iterate over lines
            while True: #iterate over line
                try:
                    print(self.screenmap[(rx,ry)],end="")
                except KeyError:
                    break
                rx += 1
            ry += 1
            rx = 0
            if (rx,ry) not in self.screenmap:
                break
