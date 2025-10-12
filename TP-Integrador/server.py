import asyncio
import json
import logging
from typing import Dict, List, Optional, Set
from enum import Enum
import uuid

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GameState(Enum):
    WAITING_PLAYERS = "waiting_players"
    PLACEMENT_PHASE = "placement_phase"
    BATTLE_PHASE = "battle_phase" 
    GAME_OVER = "game_over"

class MessageType(Enum):
    PLAYER_CONNECT = "player_connect"
    PLAYER_DISCONNECT = "player_disconnect"
    PLAYERS_READY = "players_ready"
    PLACE_SHIPS = "place_ships"
    SHOT = "shot"
    SHOT_RESULT = "shot_result"
    GAME_START = "game_start"
    GAME_UPDATE = "game_update"
    GAME_OVER = "game_over"
    ERROR = "error"

class Player:
    def __init__(self, player_id: str, writer: asyncio.StreamWriter):
        self.player_id = player_id
        self.writer = writer
        self.ships_placed = False
        self.ready = False
        self.grid = [[0 for _ in range(10)] for _ in range(10)]  # 0 = agua, 1 = barco, 2 = golpeado, 3 = agua golpeada
        self.ships = []  # Lista de posiciones de barcos
        self.hits_received = set()  # Posiciones donde fue golpeado
        
    async def send_message(self, message_type: MessageType, data=None):
        """Enviar mensaje al cliente"""
        try:
            message = {
                'type': message_type.value,
                'data': data
            }
            message_json = json.dumps(message) + '\n'
            self.writer.write(message_json.encode('utf-8'))
            await self.writer.drain()
            return True
        except Exception as e:
            logger.error(f"Error enviando mensaje a {self.player_id}: {e}")
            return False
    
    def place_ship(self, positions: List[tuple]):
        """Colocar un barco en el grid"""
        for x, y in positions:
            if 0 <= x < 10 and 0 <= y < 10:
                self.grid[y][x] = 1
        self.ships.append(positions)
    
    def receive_shot(self, x: int, y: int) -> str:
        """Procesar disparo recibido. Retorna 'hit', 'miss', o 'sunk'"""
        if not (0 <= x < 10 and 0 <= y < 10):
            return 'miss'
        
        if self.grid[y][x] == 1:  # Barco
            self.grid[y][x] = 2  # Marcar como golpeado
            self.hits_received.add((x, y))
            
            # Verificar si el barco fue hundido
            for ship_positions in self.ships:
                if (x, y) in ship_positions:
                    # Verificar si todas las posiciones del barco fueron golpeadas
                    if all((sx, sy) in self.hits_received for sx, sy in ship_positions):
                        return 'sunk'
                    break
            return 'hit'
        else:
            if self.grid[y][x] == 0:  # Agua
                self.grid[y][x] = 3  # Marcar agua como golpeada
            return 'miss'
    
    def all_ships_sunk(self) -> bool:
        """Verificar si todos los barcos fueron hundidos"""
        total_ship_positions = sum(len(ship) for ship in self.ships)
        return len(self.hits_received) == total_ship_positions

class BattleshipServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.players: Dict[str, Player] = {}
        self.max_players = 2
        self.game_state = GameState.WAITING_PLAYERS
        self.current_turn = None  # ID del jugador que tiene el turno
        
    async def start_server(self):
        """Iniciar el servidor"""
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        
        logger.info(f"✅ Servidor iniciado en {self.host}:{self.port}")
        logger.info("🎯 Esperando conexiones de clientes...")
        
        async with server:
            await server.serve_forever()
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Manejar conexión de un cliente"""
        client_addr = writer.get_extra_info('peername')
        player_id = str(uuid.uuid4())[:8]
        
        logger.info(f"Nuevo cliente conectado desde {client_addr}, ID: {player_id}")
        
        # Verificar si ya hay 2 jugadores
        if len(self.players) >= self.max_players:
            await self.send_error(writer, "Servidor lleno. Máximo 2 jugadores.")
            writer.close()
            await writer.wait_closed()
            return
        
        # Crear nuevo jugador
        player = Player(player_id, writer)
        self.players[player_id] = player
        
        # Notificar al jugador su ID
        await player.send_message(MessageType.PLAYER_CONNECT, {'player_id': player_id})
        
        # Notificar a todos los jugadores sobre el estado
        await self.broadcast_players_status()
        
        try:
            # Manejar mensajes del cliente
            async for line in reader:
                raw_data = line.decode('utf-8').strip()
                logger.info(f"📨 Datos recibidos de {player_id}: '{raw_data}'")
                
                if not raw_data:
                    logger.warning(f"⚠️ Línea vacía recibida de {player_id}")
                    continue
                try:
                    message = json.loads(raw_data)
                    logger.info(f"✅ Mensaje JSON válido de {player_id}: {message}")
                    await self.process_message(player_id, message)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Mensaje JSON inválido de {player_id}: '{raw_data}' - Error: {e}")
                except Exception as e:
                    logger.error(f"❌ Error procesando mensaje de {player_id}: {e}")
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error en conexión con {player_id}: {e}")
        finally:
            # Limpiar cuando el cliente se desconecta
            await self.disconnect_player(player_id)
            writer.close()
    
    async def send_error(self, writer: asyncio.StreamWriter, error_message: str):
        """Enviar mensaje de error"""
        try:
            message = {
                'type': MessageType.ERROR.value,
                'data': {'error': error_message}
            }
            message_json = json.dumps(message) + '\n'
            writer.write(message_json.encode('utf-8'))
            await writer.drain()
        except Exception as e:
            logger.error(f"Error enviando mensaje de error: {e}")
    
    async def disconnect_player(self, player_id: str):
        """Desconectar jugador"""
        if player_id in self.players:
            logger.info(f"Jugador {player_id} desconectado")
            del self.players[player_id]
            
            # Resetear estado del juego si no hay suficientes jugadores
            if len(self.players) < 2:
                self.game_state = GameState.WAITING_PLAYERS
                self.current_turn = None
            
            # Notificar a jugadores restantes
            await self.broadcast_players_status()
    
    async def broadcast_players_status(self):
        """Enviar estado de jugadores conectados a todos los clientes"""
        players_ready = len(self.players) >= 2
        message_data = {
            'connected_players': len(self.players),
            'max_players': self.max_players,
            'players_ready': players_ready,
            'game_state': self.game_state.value
        }
        
        for player in self.players.values():
            await player.send_message(MessageType.PLAYERS_READY, message_data)
    
    async def process_message(self, player_id: str, message: dict):
        """Procesar mensaje de un cliente"""
        message_type = message.get('type')
        data = message.get('data', {})
        
        logger.info(f"Mensaje recibido de {player_id}: {message_type}")

        if player_id not in self.players:
            return
        
        player = self.players[player_id]

        if message_type == 'place_ships':
            await self.handle_place_ships(player, data)
        elif message_type == 'shot':
            await self.handle_shot(player_id, data)
        elif message_type == 'start_game':
            await self.handle_start_game()
        else:
            logger.warning(f"Tipo de mensaje desconocido: {message_type}")
    
    async def handle_place_ships(self, player: Player, data: dict):
        """Manejar colocación de barcos"""
        try:
            ships_data = data.get('ships', [])
            
            # Limpiar barcos anteriores
            player.ships = []
            player.grid = [[0 for _ in range(10)] for _ in range(10)]
            
            # Colocar cada barco
            for ship_positions in ships_data:
                player.place_ship(ship_positions)
            
            player.ships_placed = True
            logger.info(f"Jugador {player.player_id} ha colocado sus barcos")
            
            # Verificar si ambos jugadores han colocado sus barcos
            if self.all_players_ready():
                await self.start_battle_phase()
            
        except Exception as e:
            logger.error(f"Error en colocación de barcos: {e}")
            await player.send_message(MessageType.ERROR, {'error': 'Error colocando barcos'})
    
    async def handle_shot(self, shooter_id: str, data: dict):
        """Manejar disparo"""
        if self.game_state != GameState.BATTLE_PHASE:
            return
        
        if self.current_turn != shooter_id:
            await self.players[shooter_id].send_message(
                MessageType.ERROR, {'error': 'No es tu turno'}
            )
            return
        
        x = data.get('x')
        y = data.get('y')
        
        if not (isinstance(x, int) and isinstance(y, int)):
            return
        
        # Encontrar al oponente
        opponent_id = None
        for pid in self.players:
            if pid != shooter_id:
                opponent_id = pid
                break
        
        if not opponent_id:
            return
        
        opponent = self.players[opponent_id]
        result = opponent.receive_shot(x, y)
        
        # Enviar resultado del disparo
        shot_data = {
            'x': x, 'y': y, 'result': result,
            'shooter': shooter_id, 'target': opponent_id
        }
        
        for player in self.players.values():
            await player.send_message(MessageType.SHOT_RESULT, shot_data)
        
        # Verificar fin del juego
        if opponent.all_ships_sunk():
            await self.end_game(shooter_id)
        else:
            # Cambiar turno solo si fue miss, si fue hit o sunk mantiene el turno
            if result == 'miss':
                self.current_turn = opponent_id
            # Enviar actualización del estado del juego siempre para mantener sincronizado
            await self.broadcast_game_state()
    
    async def handle_start_game(self):
        """Iniciar el juego cuando cualquier jugador lo solicite"""
        logger.info(f"🎮 SOLICITUD DE INICIO DE JUEGO - Jugadores conectados: {len(self.players)}")
        
        if len(self.players) == 2:
            self.game_state = GameState.PLACEMENT_PHASE
            logger.info("🚀 INICIANDO JUEGO - Enviando señal a AMBOS clientes")
            
            # Mensaje simple de inicio para redirigir a pantalla de juego
            start_message = {
                'phase': 'placement',
                'message': 'El juego ha comenzado - Pantalla de juego activa',
                'redirect_to_game': True
            }
            
            # Enviar a TODOS los jugadores conectados
            for player_id, player in self.players.items():
                logger.info(f"📤 Enviando GAME_START a jugador {player_id}")
                success = await player.send_message(MessageType.GAME_START, start_message)
                if success:
                    logger.info(f"✅ Mensaje enviado exitosamente a {player_id}")
                else:
                    logger.error(f"❌ Error enviando mensaje a {player_id}")
            
            logger.info("🎯 Proceso de inicio completado - Ambos clientes deberían cambiar de pantalla")
        else:
            logger.warning(f"❌ No se puede iniciar: solo hay {len(self.players)} jugadores (se requieren 2)")
    
    async def start_battle_phase(self):
        """Iniciar fase de batalla"""
        self.game_state = GameState.BATTLE_PHASE
        # Elegir jugador que empieza aleatoriamente
        import random
        player_ids = list(self.players.keys())
        self.current_turn = random.choice(player_ids)
        
        logger.info(f"Fase de batalla iniciada. Turno de: {self.current_turn}")
        
        await self.broadcast_game_state()
    
    async def broadcast_game_state(self):
        """Enviar estado del juego a todos los jugadores"""
        game_data = {
            'phase': self.game_state.value,
            'current_turn': self.current_turn,
            'players': {pid: {'ready': p.ships_placed} for pid, p in self.players.items()}
        }
        
        for player in self.players.values():
            await player.send_message(MessageType.GAME_UPDATE, game_data)
    
    async def end_game(self, winner_id: str):
        """Finalizar el juego"""
        self.game_state = GameState.GAME_OVER
        logger.info(f"Juego terminado. Ganador: {winner_id}")
        
        for player_id, player in self.players.items():
            is_winner = player_id == winner_id
            await player.send_message(MessageType.GAME_OVER, {
                'winner': winner_id,
                'is_winner': is_winner,
                'message': '¡Ganaste!' if is_winner else 'Perdiste'
            })
    
    def all_players_ready(self) -> bool:
        """Verificar si todos los jugadores están listos"""
        return (len(self.players) == 2 and 
                all(player.ships_placed for player in self.players.values()))

async def main():
    server = BattleshipServer()
    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error en el servidor: {e}")

if __name__ == "__main__":
    asyncio.run(main())