import sys
import os

sys.dont_write_bytecode = True

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(__file__))

from classes import BattleshipClient
from constants import *

if __name__ == "__main__":
    client = BattleshipClient()
    client.run()