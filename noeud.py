import threading
import socket
import sys
from time import time
from random import random
from hashlib import sha256
import logging
import json


class Noeud():
    def __init__(self, ADDR_NOEUD, PORT_NOEUD, ADDR_INI=None, PORT_INI=None ):
        self.actif = True

        self.fil_ecoute = threading.Thread(target=self.ecouter) # , args=(self,))
        self.fil_minage = threading.Thread(target=self.miner)
        
        self.ADDR = ADDR_NOEUD #adresse du noeud
        self.PORT_SERVEUR = PORT_NOEUD #eventuellement fixe par lutilisateur, sinon auto
        self.PORT2 = None #auto

        #CONFIGURATION DU LOGGER
        self.logger = logging.getLogger(__name__)
        class AppFilter(logging.Filter):
            def filter(selff, record):
                record.addr = f'{self.ADDR}:{self.PORT_SERVEUR}'
                return True
        self.logger.addFilter(AppFilter())
        syslog = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(addr)s] %(message)s', "%H:%M:%S")
        syslog.setFormatter(formatter)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(syslog)

        self.sock_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket serveur
        try:
            self.sock_serveur.bind((self.ADDR, self.PORT_SERVEUR)) #association de ladresse et du socket. pour port=0, attribution automatique, on le recupere avec sock.getsockname()[1]
            self.PORT_SERVEUR = self.sock_serveur.getsockname()[1]
            self.logger.info('Socket serveur configure')
        except socket.error as msg:
            self.logger.error(f"Impossible de configurer ladresses/port du socket serveur : {msg}")
            sys.exit(0)
        
        self.noeuds = set()
        self.chaine = []

        if PORT_INI: #si non 1er (cad si port!=0)
            ok = self.message(ADDR_INI, PORT_INI, "nouveau")
            noeuds = self.message(ADDR_INI, PORT_INI, "noeuds")
            self.noeuds.update(noeuds)
            chaine = self.message(ADDR_INI, PORT_INI, "chaine")
            if self.test_chaine(chaine):
                self.chaine = chaine
            else:
                self.logger.error("Chaine recuperee non valide")

        else: #si prems creation de la bc
            self.chaine.append(
                {
                'index': 0,
                'timestamp': time(),
                'transactions': ["nop"],
                'proof': 0,
                'previous_hash': 0,
                }
            )



        self.fil_ecoute.start()
        self.fil_minage.start()

        self.logger.info("En cours dexecution")

    def message(self, ADDR_DIST, PORT_DIST, MESSAGE): #co du client a un serveur
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket client
        sock.bind((self.ADDR, 0)) #attribution du port automatique
        sock.connect((ADDR_DIST, PORT_DIST))
        data = MESSAGE.encode()
        sock.send(data)
        data = sock.recv(1024) #attention a la data qui depasse
        sock.close()
        return data.decode()

    def traiter_co(self, conn, addr):
        with conn:
            self.logger.info(f'Traitement de la demande de connexion de : {addr[0]}:{addr[1]}')
            data = conn.recv(1024)
            code = data.decode()
            match code:
                case "chaine":
                    data = json.dumps(self.chaine).encode()
                    conn.sendall(data)
                case "noeuds":
                    data = json.dumps(list(self.noeuds)).encode()
                    conn.sendall(data)
                case "nouveau":
                    self.noeuds.add(addr)
                    data = json.dumps("ok").encode()
                    conn.sendall(data)
                case "nouveau-bloc":
                    ...

    def ecouter(self): 
        fils = []
        self.sock_serveur.listen()
        while self.actif:
            conn, addr = self.sock_serveur.accept() # bloquant # the server does not sendall()/recv() on the socket it is listening on but on the new socket returned by accept().
            fil = threading.Thread(target=self.traiter_co, args=(conn, addr))
            fil.start()
            fils.append(fils)
        for fil in fils:
            fil.join()

    @staticmethod
    def hacher(block):
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return sha256(block_string).hexdigest()

    def nouveau_bloc(self, nonce):
        bloc = {
            'index': len(self.chaine) + 1,
            'timestamp': time(),
            'transactions': [],
            'proof': nonce,
            'previous_hash': self.hacher(self.chaine[-1]),
        }
        return bloc

    @staticmethod
    def test_chaine(chaine):
        ...
        return 1

    def miner(self):
        while self.actif:
            nv_bloc = self.nouveau_bloc(random())
            if self.hacher(nv_bloc)[:3] == "0000":
                self.logger.info("Nouveau bloc")
                self.chaine.append(nv_bloc)
                for pair in self.noeuds:
                    self.message(nv_bloc)


    


if __name__ == "__main__":
    noeud_1 = Noeud("127.0.0.1", 0, "127.0.0.1", 0)
    noeud_2 = Noeud("127.0.0.1", 0, noeud_1.ADDR, noeud_1.PORT_SERVEUR)

    
            


