"""Asynchronous client for Battleship Naval game
Handles network communication with server using asyncio"""

import asyncio
import sys
import os

# Importar constants desde la carpeta padre del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import *

# Constantes específicas del cliente
CLIENT_PROMPT = "> "
DISCONNECT_COMMAND = "fin"
EMPTY_DATA_SIZE = 0
DEFAULT_ENCODING = "ascii"

class Client:
    def __init__(self):
        self.connected = True
        self.reader = None
        self.writer = None

    async def listen_server(self):
        """Tarea asíncrona que escucha mensajes del servidor"""
        try:
            while self._should_continue_listening():
                await self._process_server_message()
        except asyncio.CancelledError:
            # Tarea cancelada normalmente
            pass
        except ConnectionResetError:
            self._handle_connection_reset()
        except Exception as e:
            self._handle_listen_error(e)
    
    def _should_continue_listening(self):
        """Verifica si debe continuar escuchando mensajes del servidor"""
        return self.connected and self.reader
    
    async def _process_server_message(self):
        """Procesa un mensaje individual del servidor"""
        data = await self.reader.read(NETWORK_BUFFER_SIZE)
        
        if not self._is_valid_data(data):
            self._handle_server_disconnect()
            return
            
        response = data.decode(DEFAULT_ENCODING).strip()
        self._display_server_response(response)
    
    def _is_valid_data(self, data):
        """Verifica si los datos recibidos son válidos"""
        return len(data) > EMPTY_DATA_SIZE
    
    def _handle_server_disconnect(self):
        """Maneja la desconexión del servidor"""
        print("\n🔌 El servidor cerró la conexión")
        self.connected = False
    
    def _display_server_response(self, response):
        """Muestra la respuesta del servidor en consola"""
        print(f"\n📨 {response}")
        print(CLIENT_PROMPT, end="", flush=True)
    
    def _handle_connection_reset(self):
        """Maneja error de conexión reiniciada"""
        print("\n🚨 Conexión perdida: El servidor se desconectó inesperadamente")
        self.connected = False
    
    def _handle_listen_error(self, error):
        """Maneja errores generales al escuchar"""
        print(f"\n❌ Error recibiendo datos: {error}")
        self.connected = False

    async def send_messages(self):
        """Tarea asíncrona para enviar mensajes al servidor"""
        try:
            while self._should_continue_sending():
                message = await self._get_user_input()
                
                if not self.connected:
                    break
                    
                await self._send_message_to_server(message)
                
                if self._is_disconnect_command(message):
                    self._handle_disconnect_request()
                    break
        except asyncio.CancelledError:
            # Tarea cancelada normalmente
            pass
        except KeyboardInterrupt:
            self._handle_keyboard_interrupt()
        except ConnectionResetError:
            self._handle_send_connection_error()
        except Exception as e:
            self._handle_send_error(e)
    
    def _should_continue_sending(self):
        """Verifica si debe continuar enviando mensajes"""
        return self.connected and self.writer
    
    async def _get_user_input(self):
        """Obtiene input del usuario de forma asíncrona"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, CLIENT_PROMPT)
    
    async def _send_message_to_server(self, message):
        """Envía un mensaje al servidor"""
        self.writer.write(message.encode(DEFAULT_ENCODING))
        await self.writer.drain()
    
    def _is_disconnect_command(self, message):
        """Verifica si el mensaje es un comando de desconexión"""
        return message == DISCONNECT_COMMAND
    
    def _handle_disconnect_request(self):
        """Maneja solicitud de desconexión del usuario"""
        print("🚪 Desconectando...")
    
    def _handle_keyboard_interrupt(self):
        """Maneja interrupción por teclado"""
        print("\n⚠️ Interrumpido por el usuario")
        self.connected = False
    
    def _handle_send_connection_error(self):
        """Maneja error de conexión al enviar"""
        print("\n🚨 Error: El servidor cerró la conexión")
        self.connected = False
    
    def _handle_send_error(self, error):
        """Maneja errores generales al enviar"""
        print(f"\n❌ Error enviando mensaje: {error}")
        self.connected = False

    async def client(self):
        """Cliente principal asíncrono"""
        try:
            await self._establish_connection()
            self._display_connection_info()
            await self._run_client_tasks()
        except ConnectionRefusedError:
            self._handle_connection_refused()
        except Exception as e:
            self._handle_client_error(e)
        finally:
            await self._cleanup_client()
    
    async def _establish_connection(self):
        """Establece la conexión con el servidor"""
        print("🔄 Conectando al servidor...")
        self.reader, self.writer = await asyncio.open_connection(
            DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT
        )
    
    def _display_connection_info(self):
        """Muestra información de la conexión establecida"""
        print(f"✅ Conectado al servidor en {DEFAULT_SERVER_HOST}:{DEFAULT_SERVER_PORT}")
        print(f"💡 Escribe '{DISCONNECT_COMMAND}' para desconectarte")
        print("💡 El cliente se cerrará automáticamente si el servidor se desconecta")
    
    async def _run_client_tasks(self):
        """Ejecuta las tareas principales del cliente"""
        listen_task = asyncio.create_task(self.listen_server())
        send_task = asyncio.create_task(self.send_messages())
        
        await self._wait_for_task_completion([listen_task, send_task])
    
    async def _wait_for_task_completion(self, tasks):
        """Espera que se complete alguna tarea y cancela las pendientes"""
        done, pending = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_COMPLETED
        )
        
        await self._cancel_pending_tasks(pending)
    
    async def _cancel_pending_tasks(self, pending_tasks):
        """Cancela las tareas pendientes"""
        for task in pending_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    def _handle_connection_refused(self):
        """Maneja error de conexión rechazada"""
        print("❌ Error: No se puede conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose")
    
    def _handle_client_error(self, error):
        """Maneja errores generales del cliente"""
        print(f"❌ Error de conexión: {error}")
    
    async def _cleanup_client(self):
        """Limpia recursos del cliente"""
        print("🔚 Cliente finalizado")
        self.connected = False
        await self._close_writer_safely()
    
    async def _close_writer_safely(self):
        """Cierra el writer de forma segura"""
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception as e:
                print(f"Error cerrando writer: {e}")

async def client_main():
    """Función principal del cliente"""
    client = Client()
    try:
        await client.client()
    except KeyboardInterrupt:
        _handle_keyboard_interrupt()
    except Exception as e:
        _handle_unexpected_error(e)
    finally:
        _display_goodbye_message()

def _handle_keyboard_interrupt():
    """Maneja interrupción por teclado en main"""
    print("\n⚠️ Cliente interrumpido por el usuario")

def _handle_unexpected_error(error):
    """Maneja errores inesperados en main"""
    print(f"❌ Error inesperado en el cliente: {error}")

def _display_goodbye_message():
    """Muestra mensaje de despedida"""
    print("👋 ¡Adiós!")