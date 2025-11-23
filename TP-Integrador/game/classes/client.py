import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import *

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
        try:
            while self._should_continue_listening():
                await self._process_server_message()
        except asyncio.CancelledError:
            pass
        except ConnectionResetError:
            self._handle_connection_reset()
        except Exception as e:
            self._handle_listen_error(e)
    
    def _should_continue_listening(self):
        return self.connected and self.reader
    
    async def _process_server_message(self):
        data = await self.reader.read(NETWORK_BUFFER_SIZE)
        
        if not self._is_valid_data(data):
            self._handle_server_disconnect()
            return
            
        response = data.decode(DEFAULT_ENCODING).strip()
        self._display_server_response(response)
    
    def _is_valid_data(self, data):
        return len(data) > EMPTY_DATA_SIZE
    
    def _handle_server_disconnect(self):
        print("\n🔌 El servidor cerró la conexión")
        self.connected = False
    
    def _display_server_response(self, response):
        print(f"\n📨 {response}")
        print(CLIENT_PROMPT, end="", flush=True)
    
    def _handle_connection_reset(self):
        print("\n🚨 Conexión perdida: El servidor se desconectó inesperadamente")
        self.connected = False
    
    def _handle_listen_error(self, error):
        print(f"\n❌ Error recibiendo datos: {error}")
        self.connected = False

    async def send_messages(self):
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
            pass
        except KeyboardInterrupt:
            self._handle_keyboard_interrupt()
        except ConnectionResetError:
            self._handle_send_connection_error()
        except Exception as e:
            self._handle_send_error(e)
    
    def _should_continue_sending(self):
        return self.connected and self.writer
    
    async def _get_user_input(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, CLIENT_PROMPT)
    
    async def _send_message_to_server(self, message):
        self.writer.write(message.encode(DEFAULT_ENCODING))
        await self.writer.drain()
    
    def _is_disconnect_command(self, message):
        return message == DISCONNECT_COMMAND
    
    def _handle_disconnect_request(self):
        print("🚪 Desconectando...")
    
    def _handle_keyboard_interrupt(self):
        print("\n⚠️ Interrumpido por el usuario")
        self.connected = False
    
    def _handle_send_connection_error(self):
        print("\n🚨 Error: El servidor cerró la conexión")
        self.connected = False
    
    def _handle_send_error(self, error):
        print(f"\n❌ Error enviando mensaje: {error}")
        self.connected = False

    async def client(self):
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
        print("🔄 Conectando al servidor...")
        self.reader, self.writer = await asyncio.open_connection(
            DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT
        )
    
    def _display_connection_info(self):
        print(f"✅ Conectado al servidor en {DEFAULT_SERVER_HOST}:{DEFAULT_SERVER_PORT}")
        print(f"💡 Escribe '{DISCONNECT_COMMAND}' para desconectarte")
        print("💡 El cliente se cerrará automáticamente si el servidor se desconecta")
    
    async def _run_client_tasks(self):
        listen_task = asyncio.create_task(self.listen_server())
        send_task = asyncio.create_task(self.send_messages())
        
        await self._wait_for_task_completion([listen_task, send_task])
    
    async def _wait_for_task_completion(self, tasks):
        done, pending = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_COMPLETED
        )
        
        await self._cancel_pending_tasks(pending)
    
    async def _cancel_pending_tasks(self, pending_tasks):
        for task in pending_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    def _handle_connection_refused(self):
        print("❌ Error: No se puede conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose")
    
    def _handle_client_error(self, error):
        print(f"❌ Error de conexión: {error}")
    
    async def _cleanup_client(self):
        print("🔚 Cliente finalizado")
        self.connected = False
        await self._close_writer_safely()
    
    async def _close_writer_safely(self):
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception as e:
                print(f"Error cerrando writer: {e}")

async def client_main():
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
    print("\n⚠️ Cliente interrumpido por el usuario")

def _handle_unexpected_error(error):
    print(f"❌ Error inesperado en el cliente: {error}")

def _display_goodbye_message():
    print("👋 ¡Adiós!")