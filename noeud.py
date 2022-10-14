import threading
import socket
import sys
from time import time
from random import random
from hashlib import sha256
import logging
import json


class Noeud():
    def __init__(self, IP_NOEUD, PORT_NOEUD, IP_INI=None, PORT_INI=None ):
        self.actif = True

        self.noeuds = set()
        self.chaine = []
        self.difficulte = 5

        self.fil_ecoute = threading.Thread(target=self.ecouter) # , args=(self,))
        self.fil_minage = threading.Thread(target=self.miner)
        
        self.IP = IP_NOEUD #adresse du noeud
        self.PORT_SERVEUR = PORT_NOEUD #eventuellement fixe par lutilisateur, sinon auto

        #CONFIGURATION DU LOGGER
        self.logger = logging.getLogger(__name__)
        class AppFilter(logging.Filter):
            def filter(selff, record):
                record.addr = f'{self.IP}:{self.PORT_SERVEUR}'
                return True
        self.logger.addFilter(AppFilter())
        syslog = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(addr)s] %(message)s', "%H:%M:%S")
        syslog.setFormatter(formatter)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(syslog)

        self.sock_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket serveur
        try:
            self.sock_serveur.bind((self.IP, self.PORT_SERVEUR)) #association de ladresse et du socket. pour port=0, attribution automatique, on le recupere avec sock.getsockname()[1]
            self.PORT_SERVEUR = self.sock_serveur.getsockname()[1]
            self.logger.info('Socket serveur configure')
        except socket.error as msg:
            self.logger.error(f"Impossible de configurer ladresses/port du socket serveur : {msg}")
            sys.exit(0)
        


        if PORT_INI: #si non 1er (cad si port!=0)
            self.logger.info("Connexion au reseau")

            #recuperer les addr des noeuds du reseau
            noeuds = self.message(IP_INI, PORT_INI, "noeuds")
            for addr in noeuds:
                ip = addr[0]
                port = addr[1]
                self.noeuds.add((ip,port))
            self.logger.info(f"Adrr noeuds recup : nombre = {len(self.noeuds)}")

            #notifier les noeuds que je suis nouveau et qu ils doivent m enregistrer
            self.noeuds.add((IP_INI, PORT_INI)) #on ajoute notre pair dinitialisation 
            for pair in self.noeuds:
                self.message(pair[0], pair[1], "nouveau", (self.IP, self.PORT_SERVEUR))
                ...#traiter les erreurs types echec de co
            self.logger.info(f"Noeuds avertis")
            
            #recuperer la chaine en cours
            chaine = self.message(IP_INI, PORT_INI, "chaine")
            self.logger.info(f"Chaine recuperee : taille = {len(chaine)}")
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
            self.logger.info("Premier noeud : blockchain initialisee")



        self.fil_ecoute.start()
        self.fil_minage.start()

        self.logger.info("En cours dexecution")

    @staticmethod
    def recvall(sock):
        BUFF_SIZE = 1024 # 1 KiB
        data = b''
        while True:
            part = sock.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE: #soit 0 soit fin de la data
                break
        return data

    def message(self, IP_DIST, PORT_DIST, ID_MESSAGE, CORPS = ""): #co du client a un serveur
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket client
        sock.bind((self.IP, 0)) #attribution du port automatique
        sock.connect((IP_DIST, PORT_DIST))
        o = {"id": ID_MESSAGE, "corps" : CORPS}
        data = json.dumps(o).encode()
        sock.sendall(data)
        data = self.recvall(sock)
        sock.close()
        data_decodee = data.decode()
        if data_decodee != "":
            donnees = eval(data.decode())
            return donnees["corps"]
        else :
            return None

    def traiter_message(self, conn, addr):
        with conn:
            data = self.recvall(conn)
            donnees = eval(data.decode())
            id = donnees["id"]
            self.logger.info(f'Message entrant : {addr[0]}:{addr[1]}. Code : {id}')
            match id:
                case "chaine":
                    o = {"id": "chaineR", "corps" : self.chaine}
                    data = json.dumps(o).encode()
                    conn.sendall(data)
                case "noeuds":
                    o = {"id": "noeudsR", "corps" : list(self.noeuds)}
                    data = json.dumps(o).encode()
                    conn.sendall(data)
                case "nouveau":
                    corps = donnees["corps"]
                    addr = (corps[0], corps[1])
                    self.noeuds.add(addr)
                    o = {"id": "nouveauR", "corps" : "ok"}
                    data = json.dumps(o).encode()
                    conn.sendall(data)
                case "nouveau-bloc":
                    ...# traitement du nv bloc
                    o = {"id": "nouveau-blocR", "corps" : "ok2"}
                    
                    ...

    def ecouter(self):
        fils = []
        self.sock_serveur.listen()
        while self.actif:
            conn, addr = self.sock_serveur.accept() # bloquant # the server does not sendall()/recv() on the socket it is listening on but on the new socket returned by accept().
            fil = threading.Thread(target=self.traiter_message, args=(conn, addr))
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
            if self.hacher(nv_bloc)[:self.difficulte] == "0"*self.difficulte:
                self.logger.info("Nouveau bloc")
                self.chaine.append(nv_bloc)
                for pair in self.noeuds:
                    reponse = self.message(pair[0], pair[1], "nouveau-bloc", nv_bloc)


    


if __name__ == "__main__":
    noeud = Noeud("127.0.0.1", 0, "127.0.0.1", 63444)

    
            


