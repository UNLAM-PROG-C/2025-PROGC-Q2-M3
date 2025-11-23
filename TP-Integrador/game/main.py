import sys
import os

sys.path.append(os.path.dirname(__file__))

from classes import BattleshipClient
from constants import *

if __name__ == "__main__":
    client = BattleshipClient()
    client.run()