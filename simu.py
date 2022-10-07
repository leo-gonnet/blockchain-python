from noeud import Noeud
import sys

if __name__ == "__main__":
    if sys.argv[1]=="1":
        noeud_1 = Noeud("127.0.0.1", 65100)
    else:
        noeud_2 = Noeud("127.0.0.1", 0, "127.0.0.1", 65100)