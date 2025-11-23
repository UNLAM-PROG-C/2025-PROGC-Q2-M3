"""Módulo del servidor de Batalla Naval.

Este módulo contiene la implementación del servidor principal que maneja
las conexiones de clientes, el estado del juego y la lógica de combate.
"""

import asyncio
import json
import logging
import random
import uuid
import sys
import os
from typing import Dict, Optional, Any

# Importar constantes del servidor
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import *
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from classes.enums import GameState, MessageType
from classes.player import Player

logger = logging.getLogger(__name__)

class BattleshipServer:
    """Servidor principal del juego Batalla Naval.
    
    Esta clase maneja las conexiones de clientes, el estado del juego,
    la lógica de batalla y la comunicación entre jugadores.
    
    Attributes:
        host (str): Dirección IP del servidor.
        port (int): Puerto del servidor.
        players (Dict[str, Player]): Diccionario de jugadores conectados.
        max_players (int): Máximo número de jugadores permitidos.
        game_state (GameState): Estado actual del juego.
        current_turn (Optional[str]): ID del jugador que tiene el turno actual.
    """
    
    def __init__(self, host: str = DEFAULT_HOST_ALL_INTERFACES, port: int = DEFAULT_SERVER_PORT):
        """Inicializar servidor de Batalla Naval.
        
        Args:
            host (str): Dirección IP. '0.0.0.0' permite conexiones desde cualquier IP,
                       'localhost' solo permite conexiones locales.
            port (int): Puerto en el que escuchará el servidor.
        """
        self.host = host
        self.port = port
        self.players: Dict[str, Player] = {}
        self.max_players = MAX_PLAYERS
        self.game_state = GameState.WAITING_PLAYERS
        self.current_turn: Optional[str] = None
        
    async def start_server(self) -> None:
        """Iniciar el servidor y comenzar a escuchar conexiones."""
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        
        self._log_server_startup()
        
        async with server:
            await server.serve_forever()
            
    def _log_server_startup(self) -> None:
        """Registrar información de inicio del servidor."""
        logger.info(f"✅ Servidor iniciado en {self.host}:{self.port}")
        logger.info("🎯 Esperando conexiones de clientes...")

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Manejar conexión de un cliente.
        
        Args:
            reader (asyncio.StreamReader): Lector de datos del cliente.
            writer (asyncio.StreamWriter): Escritor de datos al cliente.
        """
        client_addr = writer.get_extra_info('peername')
        player_id = self._generate_player_id()
        
        logger.info(f"Nuevo cliente conectado desde {client_addr}, ID: {player_id}")
        
        if not await self._validate_new_connection(writer):
            return
            
        player = await self._create_and_register_player(player_id, writer)
        await self._handle_client_communication(player_id, reader)
        
    def _generate_player_id(self) -> str:
        """Generar ID único para el jugador.
        
        Returns:
            str: ID único del jugador.
        """
        return str(uuid.uuid4())[:UUID_SHORT_LENGTH]
        
    async def _validate_new_connection(self, writer: asyncio.StreamWriter) -> bool:
        """Validar si se puede aceptar una nueva conexión.
        
        Args:
            writer (asyncio.StreamWriter): Escritor del cliente.
            
        Returns:
            bool: True si se puede aceptar la conexión, False en caso contrario.
        """
        if len(self.players) >= self.max_players:
            await self.send_error(writer, CONNECTION_ERROR_MESSAGES['SERVER_FULL'])
            writer.close()
            await writer.wait_closed()
            return False
        return True
        
    async def _create_and_register_player(self, player_id: str, writer: asyncio.StreamWriter) -> Player:
        """Crear y registrar un nuevo jugador.
        
        Args:
            player_id (str): ID del jugador.
            writer (asyncio.StreamWriter): Escritor del cliente.
            
        Returns:
            Player: Objeto jugador creado.
        """
        player = Player(player_id, writer)
        self.players[player_id] = player
        
        await player.send_message(MessageType.PLAYER_CONNECT, {'player_id': player_id})
        await self.broadcast_players_status()
        
        return player
        
    async def _handle_client_communication(self, player_id: str, reader: asyncio.StreamReader) -> None:
        """Manejar la comunicación continua con el cliente.
        
        Args:
            player_id (str): ID del jugador.
            reader (asyncio.StreamReader): Lector de datos del cliente.
        """
        try:
            await self._client_message_loop(player_id, reader)
        except asyncio.CancelledError:
            logger.info(f"🔌 Conexión con {player_id} cancelada")
        except Exception as e:
            logger.error(f"❌ Error en conexión con {player_id}: {e}")
        finally:
            await self._cleanup_client_connection(player_id)
            
    async def _client_message_loop(self, player_id: str, reader: asyncio.StreamReader) -> None:
        """Bucle principal para procesar mensajes del cliente.
        
        Args:
            player_id (str): ID del jugador.
            reader (asyncio.StreamReader): Lector de datos del cliente.
        """
        while self.players.get(player_id) is not None:
            try:
                line = await asyncio.wait_for(reader.readline(), timeout=SERVER_READ_TIMEOUT)
                
                if not line:
                    logger.info(f"🔌 Cliente {player_id} desconectado - no hay más datos")
                    break
                    
                await self._process_client_message(player_id, line)
                
            except asyncio.TimeoutError:
                continue
            except ConnectionResetError:
                logger.info(f"🔌 Cliente {player_id} cerró la conexión inesperadamente")
                break
            except Exception as e:
                logger.error(f"❌ Error leyendo de {player_id}: {e}")
                break
                
    async def _process_client_message(self, player_id: str, line: bytes) -> None:
        """Procesar un mensaje recibido del cliente.
        
        Args:
            player_id (str): ID del jugador.
            line (bytes): Línea de datos recibida.
        """
        raw_data = line.decode(UTF8_ENCODING).strip()
        logger.info(f"📨 Datos recibidos de {player_id}: '{raw_data}'")
        
        if not raw_data:
            logger.warning(f"⚠️ Línea vacía recibida de {player_id}")
            return
            
        try:
            message = json.loads(raw_data)
            logger.info(f"✅ Mensaje JSON válido de {player_id}: {message}")
            await self.process_message(player_id, message)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Mensaje JSON inválido de {player_id}: '{raw_data}' - Error: {e}")
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje de {player_id}: {e}")
            
    async def _cleanup_client_connection(self, player_id: str) -> None:
        """Limpiar recursos cuando el cliente se desconecta.
        
        Args:
            player_id (str): ID del jugador a limpiar.
        """
        logger.info(f"🧹 Limpiando conexión de {player_id}")
        await self.disconnect_player(player_id)
        
        if player_id in self.players:
            try:
                writer = self.players[player_id].writer
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                logger.error(f"Error cerrando conexión: {e}")

    async def send_error(self, writer: asyncio.StreamWriter, error_message: str) -> None:
        """Enviar mensaje de error al cliente.
        
        Args:
            writer (asyncio.StreamWriter): Escritor del cliente.
            error_message (str): Mensaje de error a enviar.
        """
        try:
            message = self._create_error_message(error_message)
            await self._send_raw_error_message(writer, message)
        except Exception as e:
            logger.error(f"Error enviando mensaje de error: {e}")
            
    def _create_error_message(self, error_message: str) -> str:
        """Crear mensaje de error en formato JSON.
        
        Args:
            error_message (str): Mensaje de error.
            
        Returns:
            str: Mensaje JSON formateado.
        """
        message = {
            'type': MessageType.ERROR.value,
            'data': {'error': error_message}
        }
        return json.dumps(message) + JSON_MESSAGE_DELIMITER
        
    async def _send_raw_error_message(self, writer: asyncio.StreamWriter, message: str) -> None:
        """Enviar mensaje de error crudo.
        
        Args:
            writer (asyncio.StreamWriter): Escritor del cliente.
            message (str): Mensaje a enviar.
        """
        writer.write(message.encode(UTF8_ENCODING))
        await writer.drain()

    async def disconnect_player(self, player_id: str) -> None:
        """Desconectar jugador y limpiar recursos.
        
        Args:
            player_id (str): ID del jugador a desconectar.
        """
        if player_id not in self.players:
            return
            
        self._log_disconnection_info(player_id)
        
        if self._should_notify_opponent(player_id):
            await self._notify_opponent_disconnection(player_id)
        else:
            logger.info(f"📝 No se requiere notificación - estado: {self.game_state}, jugadores: {len(self.players)}")
            
        self._remove_player_and_reset_game(player_id)
        await self.broadcast_players_status()
        
    def _log_disconnection_info(self, player_id: str) -> None:
        """Registrar información de desconexión.
        
        Args:
            player_id (str): ID del jugador que se desconecta.
        """
        logger.info(f"🔌 DESCONECTANDO JUGADOR {player_id}")
        logger.info(f"📊 Estado actual del juego: {self.game_state}")
        logger.info(f"👥 Jugadores antes de desconexión: {list(self.players.keys())}")
        
    def _should_notify_opponent(self, player_id: str) -> bool:
        """Determinar si se debe notificar al oponente sobre la desconexión.
        
        Args:
            player_id (str): ID del jugador que se desconecta.
            
        Returns:
            bool: True si se debe notificar, False en caso contrario.
        """
        active_game_states = [GameState.PLACEMENT_PHASE, GameState.BATTLE_PHASE]
        return (self.game_state in active_game_states and 
                len(self.players) == MAX_PLAYERS)
                
    async def _notify_opponent_disconnection(self, player_id: str) -> None:
        """Notificar al oponente sobre la desconexión.
        
        Args:
            player_id (str): ID del jugador que se desconectó.
        """
        logger.info(f"🎮 Juego activo detectado - notificando al otro jugador")
        
        opponent_id = self._find_opponent_id(player_id)
        if opponent_id:
            await self._send_disconnection_message(opponent_id, player_id)
        else:
            logger.warning(f"⚠️ No se encontró otro jugador para notificar")
            
    def _find_opponent_id(self, player_id: str) -> Optional[str]:
        """Encontrar ID del oponente.
        
        Args:
            player_id (str): ID del jugador actual.
            
        Returns:
            Optional[str]: ID del oponente o None si no se encuentra.
        """
        for pid in self.players:
            if pid != player_id:
                return pid
        return None
        
    async def _send_disconnection_message(self, opponent_id: str, disconnected_player_id: str) -> None:
        """Enviar mensaje de desconexión al oponente.
        
        Args:
            opponent_id (str): ID del oponente.
            disconnected_player_id (str): ID del jugador desconectado.
        """
        opponent = self.players[opponent_id]
        logger.info(f"📤 Enviando notificación de desconexión a {opponent_id}")
        
        success = await opponent.send_message(MessageType.PLAYER_DISCONNECT, {
            'disconnected_player': disconnected_player_id,
            'message': CONNECTION_ERROR_MESSAGES['OPPONENT_DISCONNECTED'],
            'return_to_menu': True
        })
        
        if success:
            logger.info(f"✅ Notificación enviada exitosamente a {opponent_id}")
        else:
            logger.error(f"❌ Error enviando notificación a {opponent_id}")
            
    def _remove_player_and_reset_game(self, player_id: str) -> None:
        """Remover jugador y resetear el juego si es necesario.
        
        Args:
            player_id (str): ID del jugador a remover.
        """
        del self.players[player_id]
        logger.info(f"👥 Jugadores después de desconexión: {list(self.players.keys())}")
        
        if len(self.players) < MAX_PLAYERS:
            logger.info(f"🔄 Reseteando estado del juego - jugadores insuficientes")
            self.game_state = GameState.WAITING_PLAYERS
            self.current_turn = None

    async def broadcast_players_status(self) -> None:
        """Enviar estado de jugadores conectados a todos los clientes."""
        message_data = self._create_players_status_message()
        
        for player in self.players.values():
            await player.send_message(MessageType.PLAYERS_READY, message_data)
            
    def _create_players_status_message(self) -> Dict[str, Any]:
        """Crear mensaje con el estado de los jugadores.
        
        Returns:
            Dict[str, Any]: Datos del estado de los jugadores.
        """
        players_ready = len(self.players) >= MAX_PLAYERS
        return {
            'connected_players': len(self.players),
            'max_players': self.max_players,
            'players_ready': players_ready,
            'game_state': self.game_state.value
        }

    async def process_message(self, player_id: str, message: Dict[str, Any]) -> None:
        """Procesar mensaje de un cliente.
        
        Args:
            player_id (str): ID del jugador que envió el mensaje.
            message (Dict[str, Any]): Mensaje recibido del cliente.
        """
        message_type = message.get('type')
        data = message.get('data', {})
        
        logger.info(f"Mensaje recibido de {player_id}: {message_type}")

        if player_id not in self.players:
            return
        
        player = self.players[player_id]
        
        message_handlers = {
            'place_ships': lambda: self.handle_place_ships(player, data),
            'shot': lambda: self.handle_shot(player_id, data),
            'start_game': lambda: self.handle_start_game()
        }
        
        handler = message_handlers.get(message_type)
        if handler:
            await handler()
        else:
            logger.warning(f"Tipo de mensaje desconocido: {message_type}")

    async def handle_place_ships(self, player: Player, data: Dict[str, Any]) -> None:
        """Manejar colocación de barcos.
        
        Args:
            player (Player): Jugador que coloca los barcos.
            data (Dict[str, Any]): Datos de los barcos a colocar.
        """
        try:
            ships_data = data.get('ships', [])
            self._clear_player_ships(player)
            self._place_player_ships(player, ships_data)
            
            player.ships_placed = True
            logger.info(f"🚢 Jugador {player.player_id} ha colocado {len(player.ships)} barcos")
            
            await self._check_and_start_battle_if_ready()
            
        except Exception as e:
            logger.error(f"Error en colocación de barcos: {e}")
            await player.send_message(MessageType.ERROR, 
                                    {'error': CONNECTION_ERROR_MESSAGES['SHIPS_PLACEMENT_ERROR']})
            
    def _clear_player_ships(self, player: Player) -> None:
        """Limpiar barcos anteriores del jugador.
        
        Args:
            player (Player): Jugador del cual limpiar los barcos.
        """
        player.ships = []
        player.grid = [[CELL_EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
    def _place_player_ships(self, player: Player, ships_data: list) -> None:
        """Colocar barcos del jugador.
        
        Args:
            player (Player): Jugador que coloca los barcos.
            ships_data (list): Datos de los barcos a colocar.
        """
        for ship_positions in ships_data:
            if isinstance(ship_positions, list) and len(ship_positions) > 0:
                player.place_ship(ship_positions)
            else:
                logger.warning(f"Datos de barco inválidos: {ship_positions}")
                
    async def _check_and_start_battle_if_ready(self) -> None:
        """Verificar si todos los jugadores están listos e iniciar batalla."""
        players_ready = self.all_players_ready()
        logger.info(f"📊 Estado de preparación - Jugadores listos: {players_ready}")
        logger.info(f"👥 Jugadores conectados: {len(self.players)}")
        
        for pid, p in self.players.items():
            logger.info(f"   - {pid}: {'✅' if p.ships_placed else '❌'} barcos colocados")
        
        if players_ready:
            logger.info("🎮 Todos los jugadores listos - iniciando fase de batalla")
            await self.start_battle_phase()
        else:
            logger.info("⏳ Esperando a que todos los jugadores coloquen sus barcos")

    async def handle_shot(self, shooter_id: str, data: Dict[str, Any]) -> None:
        """Manejar disparo.
        
        Args:
            shooter_id (str): ID del jugador que dispara.
            data (Dict[str, Any]): Datos del disparo.
        """
        if not self._validate_shot_conditions(shooter_id):
            return
            
        x, y = data.get('x'), data.get('y')
        
        if not self._validate_shot_coordinates(x, y):
            return
        
        opponent_id = self._find_opponent_id(shooter_id)
        if not opponent_id:
            return
            
        await self._process_shot_result(shooter_id, opponent_id, x, y)
        
    def _validate_shot_conditions(self, shooter_id: str) -> bool:
        """Validar condiciones para realizar un disparo.
        
        Args:
            shooter_id (str): ID del jugador que dispara.
            
        Returns:
            bool: True si el disparo es válido, False en caso contrario.
        """
        if self.game_state != GameState.BATTLE_PHASE:
            return False
            
        if self.current_turn != shooter_id:
            asyncio.create_task(self.players[shooter_id].send_message(
                MessageType.ERROR, {'error': CONNECTION_ERROR_MESSAGES['NOT_YOUR_TURN']}
            ))
            return False
            
        return True
        
    def _validate_shot_coordinates(self, x: Any, y: Any) -> bool:
        """Validar coordenadas del disparo.
        
        Args:
            x (Any): Coordenada x.
            y (Any): Coordenada y.
            
        Returns:
            bool: True si las coordenadas son válidas, False en caso contrario.
        """
        return isinstance(x, int) and isinstance(y, int)
        
    async def _process_shot_result(self, shooter_id: str, opponent_id: str, x: int, y: int) -> None:
        """Procesar el resultado de un disparo.
        
        Args:
            shooter_id (str): ID del jugador que dispara.
            opponent_id (str): ID del oponente.
            x (int): Coordenada x del disparo.
            y (int): Coordenada y del disparo.
        """
        opponent = self.players[opponent_id]
        shot_result = opponent.receive_shot(x, y)
        result = shot_result['result']
        
        shot_data = self._create_shot_data(x, y, result, shooter_id, opponent_id, shot_result)
        
        await self._broadcast_shot_result(shot_data)
        
        if opponent.all_ships_sunk():
            await self.end_game(shooter_id)
        else:
            await self._handle_turn_change(result, opponent_id)
            
    def _create_shot_data(self, x: int, y: int, result: str, shooter_id: str, 
                         opponent_id: str, shot_result: Dict[str, Any]) -> Dict[str, Any]:
        """Crear datos del disparo para enviar a los jugadores.
        
        Args:
            x (int): Coordenada x.
            y (int): Coordenada y.
            result (str): Resultado del disparo.
            shooter_id (str): ID del tirador.
            opponent_id (str): ID del oponente.
            shot_result (Dict[str, Any]): Resultado completo del disparo.
            
        Returns:
            Dict[str, Any]: Datos del disparo formateados.
        """
        shot_data = {
            'x': x, 'y': y, 'result': result,
            'shooter': shooter_id, 'target': opponent_id
        }
        
        if result == SHOT_RESULT_SUNK and 'ship_info' in shot_result:
            shot_data['ship_info'] = shot_result['ship_info']
            
        return shot_data
        
    async def _broadcast_shot_result(self, shot_data: Dict[str, Any]) -> None:
        """Enviar resultado del disparo a todos los jugadores.
        
        Args:
            shot_data (Dict[str, Any]): Datos del disparo.
        """
        for player in self.players.values():
            await player.send_message(MessageType.SHOT_RESULT, shot_data)
            
    async def _handle_turn_change(self, result: str, opponent_id: str) -> None:
        """Manejar cambio de turno según el resultado del disparo.
        
        Args:
            result (str): Resultado del disparo.
            opponent_id (str): ID del oponente.
        """
        if result == SHOT_RESULT_MISS:
            self.current_turn = opponent_id
        await self.broadcast_game_state()

    async def handle_start_game(self) -> None:
        """Iniciar el juego cuando cualquier jugador lo solicite."""
        logger.info(f"🎮 SOLICITUD DE INICIO DE JUEGO - Jugadores conectados: {len(self.players)}")
        
        if len(self.players) == MAX_PLAYERS:
            await self._start_game_for_all_players()
        else:
            logger.warning(f"❌ No se puede iniciar: solo hay {len(self.players)} jugadores (se requieren {MAX_PLAYERS})")
            
    async def _start_game_for_all_players(self) -> None:
        """Iniciar el juego para todos los jugadores conectados."""
        self.game_state = GameState.PLACEMENT_PHASE
        logger.info("🚀 INICIANDO JUEGO - Enviando señal a AMBOS clientes")
        
        start_message = self._create_game_start_message()
        
        for player_id, player in self.players.items():
            await self._send_game_start_to_player(player_id, player, start_message)
        
        logger.info("🎯 Proceso de inicio completado - Ambos clientes deberían cambiar de pantalla")
        
    def _create_game_start_message(self) -> Dict[str, Any]:
        """Crear mensaje de inicio de juego.
        
        Returns:
            Dict[str, Any]: Datos del mensaje de inicio.
        """
        return {
            'phase': 'placement',
            'message': GAME_MESSAGES['GAME_STARTED'],
            'redirect_to_game': True
        }
        
    async def _send_game_start_to_player(self, player_id: str, player: Player, 
                                       start_message: Dict[str, Any]) -> None:
        """Enviar mensaje de inicio de juego a un jugador específico.
        
        Args:
            player_id (str): ID del jugador.
            player (Player): Objeto jugador.
            start_message (Dict[str, Any]): Mensaje de inicio.
        """
        logger.info(f"📤 Enviando GAME_START a jugador {player_id}")
        success = await player.send_message(MessageType.GAME_START, start_message)
        if success:
            logger.info(f"✅ Mensaje enviado exitosamente a {player_id}")
        else:
            logger.error(f"❌ Error enviando mensaje a {player_id}")

    async def start_battle_phase(self) -> None:
        """Iniciar fase de batalla."""
        self.game_state = GameState.BATTLE_PHASE
        
        player_ids = list(self.players.keys())
        
        if not self._validate_battle_start(player_ids):
            return
            
        self.current_turn = self._choose_starting_player(player_ids)
        
        self._log_battle_start_info(player_ids)
        await self.broadcast_game_state()
        
    def _validate_battle_start(self, player_ids: list) -> bool:
        """Validar que se puede iniciar la batalla.
        
        Args:
            player_ids (list): Lista de IDs de jugadores.
            
        Returns:
            bool: True si se puede iniciar, False en caso contrario.
        """
        if len(player_ids) < MAX_PLAYERS:
            logger.error(f"❌ No se puede iniciar batalla: solo {len(player_ids)} jugadores")
            return False
        return True
        
    def _choose_starting_player(self, player_ids: list) -> str:
        """Elegir jugador que iniciará la batalla.
        
        Args:
            player_ids (list): Lista de IDs de jugadores.
            
        Returns:
            str: ID del jugador que inicia.
        """
        return random.choice(player_ids)
        
    def _log_battle_start_info(self, player_ids: list) -> None:
        """Registrar información del inicio de batalla.
        
        Args:
            player_ids (list): Lista de IDs de jugadores.
        """
        logger.info(f"🚀 Fase de batalla iniciada!")
        logger.info(f"👥 Jugadores: {player_ids}")
        logger.info(f"🎯 Turno inicial de: {self.current_turn}")

    async def broadcast_game_state(self) -> None:
        """Enviar estado del juego a todos los jugadores."""
        game_data = self._create_game_state_data()
        
        logger.info(f"📤 Enviando estado del juego: {game_data}")
        
        for player_id, player in self.players.items():
            await self._send_game_state_to_player(player_id, player, game_data)
            
    def _create_game_state_data(self) -> Dict[str, Any]:
        """Crear datos del estado del juego.
        
        Returns:
            Dict[str, Any]: Datos del estado del juego.
        """
        return {
            'phase': self.game_state.value,
            'current_turn': self.current_turn,
            'players': {pid: {'ready': p.ships_placed} for pid, p in self.players.items()}
        }
        
    async def _send_game_state_to_player(self, player_id: str, player: Player, 
                                       game_data: Dict[str, Any]) -> None:
        """Enviar estado del juego a un jugador específico.
        
        Args:
            player_id (str): ID del jugador.
            player (Player): Objeto jugador.
            game_data (Dict[str, Any]): Datos del estado del juego.
        """
        success = await player.send_message(MessageType.GAME_UPDATE, game_data)
        if success:
            logger.info(f"✅ Estado enviado exitosamente a {player_id}")
        else:
            logger.error(f"❌ Error enviando estado a {player_id}")

    async def end_game(self, winner_id: str) -> None:
        """Finalizar el juego.
        
        Args:
            winner_id (str): ID del jugador ganador.
        """
        self.game_state = GameState.GAME_OVER
        logger.info(f"Juego terminado. Ganador: {winner_id}")
        
        for player_id, player in self.players.items():
            await self._send_game_over_message(player_id, player, winner_id)
            
    async def _send_game_over_message(self, player_id: str, player: Player, winner_id: str) -> None:
        """Enviar mensaje de fin de juego a un jugador.
        
        Args:
            player_id (str): ID del jugador.
            player (Player): Objeto jugador.
            winner_id (str): ID del ganador.
        """
        is_winner = player_id == winner_id
        message = GAME_MESSAGES['WINNER'] if is_winner else GAME_MESSAGES['LOSER']
        
        await player.send_message(MessageType.GAME_OVER, {
            'winner': winner_id,
            'is_winner': is_winner,
            'message': message
        })

    def all_players_ready(self) -> bool:
        """Verificar si todos los jugadores están listos.
        
        Returns:
            bool: True si todos están listos, False en caso contrario.
        """
        return (len(self.players) == MAX_PLAYERS and 
                all(player.ships_placed for player in self.players.values()))