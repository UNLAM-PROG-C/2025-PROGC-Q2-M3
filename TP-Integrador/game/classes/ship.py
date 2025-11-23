"""Módulo de la clase Ship unificada para Batalla Naval.

Este módulo contiene la implementación de la clase Ship que puede ser
utilizada tanto por el cliente como por el servidor para representar
barcos en el juego de Batalla Naval.
"""

import sys
import os
import logging
from typing import List, Tuple, Set, Union, Optional

# Importar constants desde la carpeta del cliente
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import SHIP_NAMES, ERROR_MESSAGES_SHIP, SHIP_INITIAL_HITS, SHIP_ORIENTATION_HORIZONTAL

logger = logging.getLogger(__name__)

class Ship:
    """Representa un barco en el juego de Batalla Naval.
    
    Esta clase puede ser utilizada tanto por el cliente como por el servidor.
    Permite dos formas de inicialización:
    1. Con un tamaño (para el cliente, antes de colocar)
    2. Con posiciones específicas (para el servidor o después de colocar)
    
    Attributes:
        size (int): Tamaño del barco en número de casillas.
        positions (List[Tuple[int, int]]): Lista de posiciones (x, y) del barco.
        ship_type (str): Tipo/nombre del barco.
        hits (Set[Tuple[int, int]]): Conjunto de posiciones golpeadas.
        sunk (bool): Indica si el barco está hundido.
        horizontal (bool): Orientación del barco (True=horizontal, False=vertical).
        name (str): Alias del ship_type para compatibilidad.
    """
    def __init__(self, size: Optional[int] = None, ship_type: Optional[str] = None, 
                 positions: Optional[List[Tuple[int, int]]] = None):
        """Inicializar barco con tamaño o posiciones.
        
        Args:
            size (Optional[int]): Tamaño del barco - usado por el cliente.
            ship_type (Optional[str]): Tipo de barco (opcional).
            positions (Optional[List[Tuple[int, int]]]): Coordenadas del barco - usado por el servidor.
            
        Raises:
            ValueError: Si no se proporcionan parámetros válidos o si las posiciones están vacías.
        """
        self._initialize_common_attributes()
        
        if positions is not None:
            self._initialize_from_positions(positions, ship_type)
        elif size is not None:
            self._initialize_from_size(size, ship_type)
        else:
            raise ValueError(ERROR_MESSAGES_SHIP['MISSING_INIT_PARAMS'])
            
    def _initialize_common_attributes(self) -> None:
        """Inicializar atributos comunes del barco."""
        self.hits = set()
        self.sunk = False
        self.horizontal = SHIP_ORIENTATION_HORIZONTAL
        
    def _initialize_from_positions(self, positions: List[Tuple[int, int]], ship_type: Optional[str]) -> None:
        """Inicializar barco a partir de posiciones (modo servidor).
        
        Args:
            positions (List[Tuple[int, int]]): Lista de posiciones del barco.
            ship_type (Optional[str]): Tipo de barco.
            
        Raises:
            ValueError: Si las posiciones están vacías.
        """
        if not positions:
            raise ValueError(ERROR_MESSAGES_SHIP['EMPTY_POSITIONS'])
            
        self.positions = list(positions)
        self.size = len(positions)
        self.ship_type = ship_type or self.get_ship_name_by_size(self.size)
        self.name = self.ship_type
        
        logger.debug(f"Ship creado con posiciones: {self.ship_type} en {self.positions}")
        
    def _initialize_from_size(self, size: int, ship_type: Optional[str]) -> None:
        """Inicializar barco a partir de tamaño (modo cliente).
        
        Args:
            size (int): Tamaño del barco.
            ship_type (Optional[str]): Tipo de barco.
        """
        self.size = size
        self.positions = []
        self.ship_type = ship_type or self.get_ship_name_by_size(size)
        self.name = self.ship_type
    def get_ship_name_by_size(self, size: int) -> str:
        """Obtener el nombre del barco según su tamaño.
        
        Args:
            size (int): Tamaño del barco.
            
        Returns:
            str: Nombre del barco correspondiente al tamaño.
        """
        return SHIP_NAMES.get(size, f"Barco de {size} casillas")
    def contains_position(self, x: int, y: int) -> bool:
        """Verificar si el barco contiene la posición especificada.
        
        Args:
            x (int): Coordenada x.
            y (int): Coordenada y.
            
        Returns:
            bool: True si el barco contiene la posición, False en caso contrario.
        """
        return (x, y) in self.positions
    def hit(self, x: int, y: int) -> bool:
        """Marcar una posición como golpeada si pertenece al barco.
        
        Args:
            x (int): Coordenada x del golpe.
            y (int): Coordenada y del golpe.
        
        Returns:
            bool: True si la posición pertenece al barco y fue golpeada,
                  False si la posición no pertenece al barco.
        """
        if not self.contains_position(x, y):
            return False
            
        self._register_hit(x, y)
        self._update_sunk_status()
        return True
        
    def _register_hit(self, x: int, y: int) -> None:
        """Registrar un golpe en las coordenadas especificadas.
        
        Args:
            x (int): Coordenada x del golpe.
            y (int): Coordenada y del golpe.
        """
        self.hits.add((x, y))
        logger.debug(f"Golpe registrado en {self.ship_type} en posición ({x}, {y})")
        
    def _update_sunk_status(self) -> None:
        """Actualizar el estado de hundido del barco."""
        if self.is_sunk():
            self.sunk = True
            logger.debug(f"{self.ship_type} está hundido")
    def is_sunk(self) -> bool:
        """Verificar si el barco está hundido.
        
        Un barco está hundido cuando todas sus posiciones han sido golpeadas.
        
        Returns:
            bool: True si el barco está hundido, False en caso contrario.
        """
        return bool(self.positions) and len(self.hits) >= len(self.positions)
    def get_remaining_positions(self) -> Set[Tuple[int, int]]:
        """Obtener las posiciones del barco que aún no han sido golpeadas.
        
        Returns:
            Set[Tuple[int, int]]: Conjunto de posiciones no golpeadas.
        """
        return set(self.positions) - self.hits
    def get_hit_positions(self) -> Set[Tuple[int, int]]:
        """Obtener las posiciones del barco que han sido golpeadas.
        
        Returns:
            Set[Tuple[int, int]]: Conjunto de posiciones golpeadas.
        """
        return self.hits.copy()
    # Métodos adicionales para el cliente
    def set_positions(self, positions: List[Tuple[int, int]]) -> None:
        """Establecer las posiciones del barco.
        
        Usado por el cliente al colocar barcos en el tablero.
        
        Args:
            positions (List[Tuple[int, int]]): Lista de posiciones del barco.
        """
        self.positions = positions
        
    def add_position(self, x: int, y: int) -> None:
        """Agregar una posición al barco.
        
        Args:
            x (int): Coordenada x.
            y (int): Coordenada y.
        """
        if (x, y) not in self.positions:
            self.positions.append((x, y))
    
    def set_horizontal(self, horizontal: bool) -> None:
        """Establecer orientación del barco.
        
        Args:
            horizontal (bool): True para horizontal, False para vertical.
        """
        self.horizontal = horizontal
    def __str__(self) -> str:
        """Representación en string del barco.
        
        Returns:
            str: Descripción del barco con su estado actual.
        """
        status = self._get_ship_status_string()
        return f"{self.ship_type} [{status}]"
        
    def _get_ship_status_string(self) -> str:
        """Obtener string del estado del barco.
        
        Returns:
            str: Estado del barco (hundido o parcialmente golpeado).
        """
        if self.sunk or self.is_sunk():
            return "Hundido"
        return f"{len(self.hits)}/{len(self.positions)} golpeado"
    
    def __repr__(self) -> str:
        """Representación para debugging.
        
        Returns:
            str: Representación detallada del objeto Ship.
        """
        return (f"Ship(size={self.size}, type={self.ship_type}, "
                f"positions={self.positions}, hits={list(self.hits)})")