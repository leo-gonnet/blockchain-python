import threading
import socket
import sys
import time
import random

#self.sock.getsockname()[1]

class Noeud():
    def __init__(self, ADDR_INI):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind((ADDR_INI[0], ADDR_INI[1]))
            print('Socket configure')
        except:
            print("Impossible de configurer le socket")
            sys.exit()


        



if __name__ == "__main__":
    ADDR_INI = ["127.0.0.1", 8000]
    noeud_1 = Noeud(ADDR_INI)

    
            


