import asyncio
import signal

class Server:
    def __init__(self):
        self.client_count = 0
        self.connected_clients = {}  # Diccionario para mantener clientes conectados
        self.server_running = True

    async def handle_client(self, reader, writer):
        """Maneja la comunicación con un cliente específico de forma asíncrona"""
        self.client_count += 1
        client_id = self.client_count
        client_address = writer.get_extra_info('peername')
        
        # Agregar cliente a la lista de conectados
        self.connected_clients[client_id] = {
            'writer': writer,
            'address': client_address
        }
        
        print(f"Cliente {client_id} conectado desde: {client_address}")
        print(f"Total de clientes conectados: {len(self.connected_clients)}")
        
        try:
            while self.server_running:
                # Leer datos del cliente de forma asíncrona
                data = await reader.read(1024)
                if not data:
                    break
                
                recibi = data.decode("ascii").strip()
                if recibi == "fin":
                    break
                
                print(f"Cliente {client_id}: {recibi}")
                
                # Opcional: enviar respuesta al cliente
                response = f"Servidor recibió: {recibi}\n"
                writer.write(response.encode("ascii"))
                await writer.drain()  # Asegurar que se envíe
                
        except asyncio.CancelledError:
            # El servidor se está cerrando
            print(f"Cliente {client_id}: Conexión cancelada por cierre del servidor")
        except Exception as e:
            print(f"Error con cliente {client_id}: {e}")
        finally:
            # Remover cliente de la lista de conectados
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
            
            print(f"Cliente {client_id} desconectado")
            print(f"Clientes restantes: {len(self.connected_clients)}")
            
            if not writer.is_closing():
                writer.close()
                await writer.wait_closed()

    async def notify_clients_shutdown(self):
        """Notifica a todos los clientes conectados que el servidor se va a cerrar"""
        if not self.connected_clients:
            return
        
        print(f"\n📢 Notificando a {len(self.connected_clients)} clientes sobre el cierre del servidor...")
        
        shutdown_message = "🛑 SERVIDOR CERRANDO: El servidor se está apagando. Tu conexión será terminada.\n"
        
        # Enviar mensaje a todos los clientes conectados
        for client_id, client_info in list(self.connected_clients.items()):
            try:
                writer = client_info['writer']
                if not writer.is_closing():
                    writer.write(shutdown_message.encode("ascii"))
                    await writer.drain()
                    print(f"✅ Cliente {client_id} notificado")
            except Exception as e:
                print(f"❌ Error notificando cliente {client_id}: {e}")
        
        # Dar tiempo para que se envíen los mensajes
        await asyncio.sleep(1.0)
        
        # Cerrar todas las conexiones
        for client_id, client_info in list(self.connected_clients.items()):
            try:
                writer = client_info['writer']
                if not writer.is_closing():
                    writer.close()
                    await writer.wait_closed()
                    print(f"🔌 Cliente {client_id} desconectado")
            except Exception as e:
                print(f"❌ Error cerrando conexión con cliente {client_id}: {e}")
        
        self.connected_clients.clear()
        print("✅ Todas las conexiones de clientes cerradas")

    async def server(self):
        """Inicia el servidor asíncrono"""
        print("🚀 Iniciando servidor asíncrono...")
        
        server = None
        try:
            # Crear servidor asíncrono
            server = await asyncio.start_server(
                self.handle_client, 
                "127.0.0.1", 
                5000
            )
            
            addr = server.sockets[0].getsockname()
            print(f"🌐 Servidor escuchando en {addr[0]}:{addr[1]}")
            print("⏳ Esperando conexiones de clientes...")
            print("💡 Para detener: Ctrl+C")
            
            # Mantener el servidor corriendo
            async with server:
                await server.serve_forever()
                
        except asyncio.CancelledError:
            print("\n🛑 Servidor siendo cancelado...")
        finally:
            # Marcar que el servidor se está cerrando
            self.server_running = False
            
            # Notificar a todos los clientes
            await self.notify_clients_shutdown()
            
            # Cerrar el servidor si aún está abierto
            if server:
                server.close()
                await server.wait_closed()
            
            print("🔚 Servidor completamente cerrado")

async def main():
    """Función principal que maneja el cierre ordenado del servidor"""
    server = Server()
    
    try:
        await server.server()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupción detectada (Ctrl+C)")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        print("👋 ¡Adiós!")

# Ejecución directa
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🚨 Forzando cierre del servidor...")

