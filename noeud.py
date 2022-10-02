import threading
import socket
import sys
import time
import random


class Noeud():
    def __init__(self, ADDR, PORT_SERVEUR, ADDR_INI, PORT_INI ):
        self.actif = True

        self.ADDR = ADDR #adresse du noeud
        self.PORT1 = PORT_SERVEUR #eventuellement fixe par lutilisateur, sinon auto
        self.PORT2 = None #auto
        self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket serveur
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket client
        try:
            self.sock1.bind((self.ADDR, self.PORT1)) #association de ladresse et du socket. pour port=0, attribution automatique, on le recupere avec sock.getsockname()[1]
            self.sock2.bind((self.ADDR, 0))
            print('Sockets configure')
            self.PORT1 = self.sock1.getsockname()[1]
            self.PORT2 = self.sock2.getsockname()[1]
        except:
            print("Impossible de configurer les adresses/ports des sockets")
            sys.exit()
        self.reseau = set()
        self.chaine = []

        if PORT_INI: #si non 1er (cad si port!=0)
            fil = threading.Thread(target=self.recuperer_chaine, args=(self,))
            fil.start()
            self.sock2.connect((ADDR_INI, PORT_INI))
            self.sock2.send("reseau".encode())

            # vraiment besoin de 2 sockets pour ca ? https://docs.python.org/3/library/socket.html#example

        else:
            ...

    def recuperer_chaine(self):
        self.sock1.listen()
        conn, addr = self.sock1.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data: break
                conn.sendall(data)


    def ecoute(self): 
        self.sock.listen()
    

        



if __name__ == "__main__":
    noeud_1 = Noeud(["127.0.0.1", 0], ["127.0.0.1", 0])
    noeud_2 = Noeud(["127.0.0.1", 0], noeud_1.addr)

    
            


