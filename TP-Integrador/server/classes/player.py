"""Módulo para la clase Player del servidor de Batalla Naval.

Este módulo contiene la implementación de la clase Player que maneja
la información del jugador, sus barcos y las interacciones del juego.
"""

import asyncio
import json
import logging
import sys
import os
from typing import List, Dict, Optional, Any

# Importar Ship desde el cliente (ahora es una clase unificada)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'game', 'classes'))
from ship import Ship

# Importar constantes del servidor
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import *
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from classes.enums import MessageType

logger = logging.getLogger(__name__)

class Player:
    """Representa un jugador en el juego de Batalla Naval.
    
    Esta clase maneja la información del jugador, incluyendo su grid de juego,
    barcos, estado de preparación y comunicación con el cliente.
    
    Attributes:
        player_id (str): Identificador único del jugador.
        writer (asyncio.StreamWriter): Escritor para comunicación con el cliente.
        ships_placed (bool): Indica si todos los barcos han sido colocados.
        ready (bool): Indica si el jugador está listo para comenzar.
        grid (List[List[int]]): Grid del tablero de juego del jugador.
        ships (List[Ship]): Lista de objetos Ship del jugador.
    """
    
    def __init__(self, player_id: str, writer: asyncio.StreamWriter):
        """Inicializar un nuevo jugador.
        
        Args:
            player_id (str): Identificador único del jugador.
            writer (asyncio.StreamWriter): Escritor para comunicación con el cliente.
        """
        self.player_id = player_id
        self.writer = writer
        self.ships_placed = False
        self.ready = False
        self.grid = self._initialize_grid()
        self.ships = []
        
    def _initialize_grid(self) -> List[List[int]]:
        """Inicializar el grid del tablero de juego.
        
        Returns:
            List[List[int]]: Grid inicializado con celdas vacías.
        """
        return [[CELL_EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    async def send_message(self, message_type: MessageType, data: Optional[Any] = None) -> bool:
        """Enviar mensaje al cliente.
        
        Args:
            message_type (MessageType): Tipo del mensaje a enviar.
            data (Optional[Any]): Datos adicionales del mensaje.
            
        Returns:
            bool: True si el mensaje fue enviado exitosamente, False en caso contrario.
        """
        try:
            message = self._create_message(message_type, data)
            await self._send_raw_message(message)
            return True
        except (ConnectionResetError, BrokenPipeError):
            self._log_connection_error()
            return False
        except Exception as e:
            self._log_send_error(e)
            return False
            
    def _create_message(self, message_type: MessageType, data: Optional[Any]) -> str:
        """Crear mensaje JSON para enviar al cliente.
        
        Args:
            message_type (MessageType): Tipo del mensaje.
            data (Optional[Any]): Datos del mensaje.
            
        Returns:
            str: Mensaje JSON formateado.
        """
        message = {
            'type': message_type.value,
            'data': data
        }
        return json.dumps(message) + JSON_MESSAGE_DELIMITER
        
    async def _send_raw_message(self, message: str) -> None:
        """Enviar mensaje crudo al cliente.
        
        Args:
            message (str): Mensaje a enviar.
        """
        self.writer.write(message.encode(UTF8_ENCODING))
        await self.writer.drain()
        
    def _log_connection_error(self) -> None:
        """Registrar error de conexión."""
        logger.error(f"🔌 Cliente {self.player_id} desconectado durante envío")
        
    def _log_send_error(self, error: Exception) -> None:
        """Registrar error general de envío.
        
        Args:
            error (Exception): Excepción ocurrida.
        """
        logger.error(f"❌ Error enviando mensaje a {self.player_id}: {error}")
    def place_ship(self, positions: List[tuple]) -> None:
        """Colocar un barco en el grid.
        
        Args:
            positions (List[tuple]): Lista de posiciones (x, y) del barco.
        """
        valid_positions = self._validate_ship_positions(positions)
        
        if valid_positions:
            self._create_and_add_ship(valid_positions)
        else:
            logger.error("No se pudieron colocar posiciones válidas para el barco")
            
    def _validate_ship_positions(self, positions: List[tuple]) -> List[tuple]:
        """Validar y filtrar posiciones válidas del barco.
        
        Args:
            positions (List[tuple]): Posiciones propuestas para el barco.
            
        Returns:
            List[tuple]: Lista de posiciones válidas.
        """
        valid_positions = []
        for x, y in positions:
            if self._is_valid_position(x, y):
                self.grid[y][x] = CELL_SHIP
                valid_positions.append((x, y))
            else:
                logger.warning(f"Posición fuera del tablero ignorada: ({x}, {y})")
        return valid_positions
        
    def _is_valid_position(self, x: int, y: int) -> bool:
        """Verificar si una posición es válida en el tablero.
        
        Args:
            x (int): Coordenada x.
            y (int): Coordenada y.
            
        Returns:
            bool: True si la posición es válida, False en caso contrario.
        """
        return MIN_COORDINATE <= x < GRID_SIZE and MIN_COORDINATE <= y < GRID_SIZE
        
    def _create_and_add_ship(self, positions: List[tuple]) -> None:
        """Crear y agregar un nuevo barco a la lista.
        
        Args:
            positions (List[tuple]): Posiciones válidas del barco.
        """
        ship = Ship(positions=positions)
        self.ships.append(ship)
        logger.info(f"Barco colocado: {ship.ship_type} en posiciones {positions}")
    def find_ship_containing(self, x: int, y: int) -> Optional[Ship]:
        """Encontrar el barco que contiene las coordenadas especificadas.
        
        Args:
            x (int): Coordenada x.
            y (int): Coordenada y.
            
        Returns:
            Optional[Ship]: El barco que contiene la coordenada o None si no existe.
        """
        for ship in self.ships:
            if ship.contains_position(x, y):
                return ship
        return None
    def receive_shot(self, x: int, y: int) -> Dict[str, Any]:
        """Procesar disparo recibido.
        
        Args:
            x (int): Coordenada x del disparo.
            y (int): Coordenada y del disparo.
            
        Returns:
            Dict[str, Any]: Resultado del disparo con 'result' y opcionalmente 'ship_info'.
        """
        if not self._is_valid_position(x, y):
            logger.warning(f"Disparo fuera del tablero: ({x}, {y})")
            return {'result': SHOT_RESULT_MISS}
            
        current_cell = self.grid[y][x]
        
        if current_cell == CELL_EMPTY:
            return self._process_water_hit(x, y)
        elif current_cell == CELL_SHIP:
            return self._process_ship_hit(x, y)
        else:
            return self._process_already_hit(x, y)
            
    def _process_water_hit(self, x: int, y: int) -> Dict[str, str]:
        """Procesar disparo al agua.
        
        Args:
            x (int): Coordenada x.
            y (int): Coordenada y.
            
        Returns:
            Dict[str, str]: Resultado del disparo al agua.
        """
        self.grid[y][x] = CELL_WATER_HIT
        logger.info(f"Disparo al agua en ({x}, {y})")
        return {'result': SHOT_RESULT_MISS}
        
    def _process_ship_hit(self, x: int, y: int) -> Dict[str, Any]:
        """Procesar disparo que impacta un barco.
        
        Args:
            x (int): Coordenada x.
            y (int): Coordenada y.
            
        Returns:
            Dict[str, Any]: Resultado del impacto al barco.
        """
        self.grid[y][x] = CELL_HIT
        ship = self.find_ship_containing(x, y)
        
        if ship is None:
            logger.error(f"ERROR: No se encontró barco en posición ({x}, {y}) que debería tener uno")
            return {'result': SHOT_RESULT_HIT}
            
        ship.hit(x, y)
        logger.info(f"Golpe en {ship.ship_type} en posición ({x}, {y})")
        
        if ship.is_sunk():
            return self._create_sunk_ship_result(ship)
        else:
            return {'result': SHOT_RESULT_HIT}
            
    def _create_sunk_ship_result(self, ship: Ship) -> Dict[str, Any]:
        """Crear resultado para barco hundido.
        
        Args:
            ship (Ship): Barco hundido.
            
        Returns:
            Dict[str, Any]: Información completa del barco hundido.
        """
        logger.info(f"¡{ship.ship_type} hundido!")
        return {
            'result': SHOT_RESULT_SUNK,
            'ship_info': {
                'name': ship.ship_type,
                'size': ship.size,
                'positions': list(ship.positions)
            }
        }
        
    def _process_already_hit(self, x: int, y: int) -> Dict[str, str]:
        """Procesar disparo a posición ya golpeada.
        
        Args:
            x (int): Coordenada x.
            y (int): Coordenada y.
            
        Returns:
            Dict[str, str]: Resultado del disparo repetido.
        """
        logger.info(f"Disparo a posición ya golpeada: ({x}, {y})")
        return {'result': SHOT_RESULT_MISS}
    def all_ships_sunk(self) -> bool:
        """Verificar si todos los barcos han sido hundidos.
        
        Returns:
            bool: True si todos los barcos están hundidos, False en caso contrario.
                 Retorna False si no hay barcos colocados.
        """
        if not self.ships:
            return False
        return all(ship.is_sunk() for ship in self.ships)