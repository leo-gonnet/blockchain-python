from noeud import Noeud()


if __name__ == "__main__":
    noeud_1 = Noeud("127.0.0.1", 0, "127.0.0.1", 0)
    noeud_2 = Noeud("127.0.0.1", 0, noeud_1.ADDR, noeud_1.PORT1)