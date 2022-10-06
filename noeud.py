import threading
import socket
import sys
from time import time
from random import random
from hashlib import sha256
import logging
import json


class Noeud():
    def __init__(self, ADDR, PORT_SERVEUR, ADDR_INI, PORT_INI ):
        self.actif = True

        self.fil_ecoute = threading.Thread(target=self.ecouter) # , args=(self,))
        self.fil_minage = threading.Thread(target=self.miner)
        
        self.ADDR = ADDR #adresse du noeud
        self.PORT1 = PORT_SERVEUR #eventuellement fixe par lutilisateur, sinon auto
        self.PORT2 = None #auto

        #CONFIGURATION DU LOGGER
        self.logger = logging.getLogger(__name__)
        class AppFilter(logging.Filter):
            def filter(selff, record):
                record.addr = f'{self.ADDR}:{self.PORT1}'
                return True
        self.logger.addFilter(AppFilter())
        syslog = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(addr)s] %(message)s', "%H:%M:%S")
        syslog.setFormatter(formatter)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(syslog)

        self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket serveur
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket client
        try:
            self.sock1.bind((self.ADDR, self.PORT1)) #association de ladresse et du socket. pour port=0, attribution automatique, on le recupere avec sock.getsockname()[1]
            self.sock2.bind((self.ADDR, 0))
            self.PORT1 = self.sock1.getsockname()[1]
            self.PORT2 = self.sock2.getsockname()[1]
            self.logger.info('Sockets configure')
        except:
            self.logger.error("Impossible de configurer les adresses/ports des sockets")
            sys.exit(0)
        
        self.noeuds = set()
        self.chaine = []

        if PORT_INI: #si non 1er (cad si port!=0)
            noeuds = self.recuperer_noeuds(ADDR_INI, PORT_INI)
            self.noeuds.update(noeuds)
            chaine = self.recuperer_chaine(ADDR_INI, PORT_INI)
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


    def recuperer_noeuds(self, addr, port):
        self.sock2.connect((addr, port))
        self.sock2.send("noeuds".encode())
        data = self.sock2.recv(1024) #attention a la data qui depasse en cas de gros reseau
        #self.sock2.close()
        return data.decode()

    def recuperer_chaine(self, addr, port):
        self.sock2.connect((addr, port))
        self.sock2.send("chaine".encode())
        data = self.sock2.recv(1024) #attention a la data qui depasse en cas de grosse chaine
        #self.sock2.close()
        return


    def traiter_co(self, conn, addr):
        with conn:
            self.logger.info(f'Traitement de la demande de connexion de : {self.ADDR}:{self.PORT1}')
            data = conn.recv(1024)
            code = data.decode()
            match code:
                case "chaine":
                    data = json.dumps(self.chaine).encode()
                    conn.sendall(data)
                case "noeuds":
                    data = json.dumps(list(self.noeuds)).encode()
                    conn.sendall(data)
                case "nouveau-bloc":
                    ...

    def ecouter(self): 
        fils = []
        self.sock1.listen()
        while self.actif:
            conn, addr = self.sock1.accept() # bloquant # the server does not sendall()/recv() on the socket it is listening on but on the new socket returned by accept().
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

    def test_chaine(chaine):
        ...
        return 1

    def miner(self):
        while self.actif:
            nv_bloc = self.nouveau_bloc(random())
            if self.hacher(nv_bloc)[:3] == "000":
                self.chaine.append(nv_bloc)
                #prevenir les autres


    


if __name__ == "__main__":
    noeud_1 = Noeud("127.0.0.1", 0, "127.0.0.1", 0)
    noeud_2 = Noeud("127.0.0.1", 0, noeud_1.ADDR, noeud_1.PORT1)

    
            


