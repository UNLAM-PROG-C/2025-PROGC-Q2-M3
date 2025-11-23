"""
Paquete de clases para el juego de Batalla Naval
"""

from .ship import Ship
from .game_board import GameBoard
# Colors integrados en constants.py - ya no se necesita importar
from .connection_dialog import ConnectionDialog
from .game_screen import GameScreen
from .menu_screen import MenuScreen
from .network_manager import NetworkManager
from .game_over_screen import GameOverScreen
from .client import Client
from .battleship_client import BattleshipClient

__all__ = [
    'Ship', 
    'GameBoard', 
    'Colors', 
    'ConnectionDialog', 
    'GameScreen',
    'MenuScreen',
    'NetworkManager',
    'GameOverScreen',
    'Client',
    'BattleshipClient'
]