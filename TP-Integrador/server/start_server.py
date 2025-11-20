#!/usr/bin/env python3

import asyncio
import argparse
import sys
import os
import signal

# Agregar el directorio actual al path para importar constants del servidor
sys.path.append(os.path.dirname(__file__))

from server import main as server_main
from constants import *

# Constantes específicas para el servidor
BANNER_WIDTH = 80
FIREWALL_TCP_PROTOCOL = '/tcp'
DEFAULT_HOST_ALL_INTERFACES = '0.0.0.0'
DEFAULT_HOST_LOCALHOST = 'localhost'
DEFAULT_HOST_LOOPBACK = '127.0.0.1'
MAX_METHOD_LINES = 15
ARG_VALIDATION_EXIT_SUCCESS = 0
ARG_VALIDATION_EXIT_ERROR = 1
SIGNAL_SIGINT = signal.SIGINT
SIGNAL_SIGTERM = signal.SIGTERM
USER_INPUT_YES = 's'
USER_INPUT_NO = 'n'

class SimpleServer:
    def __init__(self, host='0.0.0.0', port=DEFAULT_SERVER_PORT):
        self.host = host
        self.port = port
        self.running = False
        
    def print_banner(self):
        """Mostrar banner del servidor."""
        separator = "=" * BANNER_WIDTH
        print(f"\n{separator}")
        print("🚢 BATALLA NAVAL - SERVIDOR DIRECTO")
        print(separator)
        print("Servidor configurado para recibir conexiones directas")
        print("Sin dependencias de ngrok - ideal para VM/VPS")
        print(f"{separator}\n")

    def print_server_info(self):
        """Mostrar información completa del servidor."""
        self._print_basic_server_config()
        self._print_public_access_info()
        self._print_client_instructions()
        
    def _print_basic_server_config(self):
        """Mostrar configuración básica del servidor."""
        separator = "=" * BANNER_WIDTH
        print("📋 CONFIGURACIÓN DEL SERVIDOR:")
        print(separator)
        print(f"🌐 Host: {self.host}")
        print(f"🔌 Puerto: {self.port}")
        print(f"🔗 URL de conexión: {self.host}:{self.port}")
        
    def _print_public_access_info(self):
        """Mostrar información sobre acceso público si aplica."""
        if self.host == DEFAULT_HOST_ALL_INTERFACES:
            print("\n🌍 ACCESO PÚBLICO:")
            print("   - El servidor escucha en TODAS las interfaces de red")
            print("   - Los clientes pueden conectarse desde cualquier IP")
            print("   - Asegúrate de que el puerto esté abierto en el firewall")
            
    def _print_client_instructions(self):
        """Mostrar instrucciones para los clientes."""
        separator = "=" * BANNER_WIDTH
        print("\n📝 INSTRUCCIONES PARA CLIENTES:")
        print("   1. Los jugadores deben usar la IP pública de esta máquina")
        print(f"   2. Puerto a configurar en el cliente: {self.port}")
        print("   3. Formato de conexión: <IP_PUBLICA>:<PUERTO>")
        print(f"{separator}\n")

    def print_firewall_instructions(self):
        """Mostrar instrucciones de firewall para diferentes sistemas."""
        self._print_linux_firewall_config()
        self._print_rhel_firewall_config()
        
    def _print_linux_firewall_config(self):
        """Mostrar configuración de firewall para Linux/Ubuntu."""
        separator = "=" * BANNER_WIDTH
        print("🔥 CONFIGURACIÓN DE FIREWALL (Linux):")
        print(separator)
        print(f"sudo ufw allow {self.port}")
        print("sudo ufw reload")
        print()
        
    def _print_rhel_firewall_config(self):
        """Mostrar configuración de firewall para CentOS/RHEL."""
        separator = "=" * BANNER_WIDTH
        print("🔥 CONFIGURACIÓN DE FIREWALL (CentOS/RHEL):")
        print(f"sudo firewall-cmd --permanent --add-port={self.port}{FIREWALL_TCP_PROTOCOL}")
        print("sudo firewall-cmd --reload")
        print(f"{separator}\n")

    async def start(self):
        """Iniciar el servidor con manejo completo de errores."""
        self._print_startup_info()
        self.running = True
        
        try:
            await self._start_battleship_server()
        except OSError as e:
            self._handle_os_error(e)
        except KeyboardInterrupt:
            self._handle_keyboard_interrupt()
        except Exception as e:
            self._handle_unexpected_error(e)
        finally:
            self._cleanup_server()
            
    def _print_startup_info(self):
        """Mostrar información de inicio del servidor."""
        self.print_banner()
        self.print_server_info()
        self.print_firewall_instructions()
        separator = "=" * BANNER_WIDTH
        print("🚀 INICIANDO SERVIDOR...")
        print(separator)
        print("⏸️  Presiona Ctrl+C para detener el servidor")
        print("💡 Mantén esta ventana abierta mientras el servidor esté activo")
        print(f"{separator}\n")
            
    async def _start_battleship_server(self):
        """Crear e iniciar el servidor de batalla naval."""
        from server import BattleshipServer
        server = BattleshipServer(host=self.host, port=self.port)
        await server.start_server()
        
    def _handle_os_error(self, error):
        """Manejar errores del sistema operativo."""
        if "Address already in use" in str(error):
            self._print_port_in_use_error()
        else:
            print(f"❌ ERROR de red: {error}")
        sys.exit(ARG_VALIDATION_EXIT_ERROR)
        
    def _print_port_in_use_error(self):
        """Mostrar información sobre error de puerto en uso."""
        print(f"❌ ERROR: El puerto {self.port} ya está en uso")
        print("💡 Soluciones:")
        print("   1. Usar un puerto diferente: --port OTRO_PUERTO")
        print("   2. Detener el proceso que usa el puerto")
        print(f"   3. Encontrar proceso: sudo lsof -i :{self.port}")
        
    def _handle_keyboard_interrupt(self):
        """Manejar interrupción por teclado."""
        print("\n\n🛑 Servidor detenido por el usuario")
        
    def _handle_unexpected_error(self, error):
        """Manejar errores inesperados."""
        print(f"\n❌ Error inesperado: {error}")
        sys.exit(ARG_VALIDATION_EXIT_ERROR)
        
    def _cleanup_server(self):
        """Limpiar recursos del servidor."""
        self.running = False
        print("\n👋 Servidor cerrado correctamente")

def setup_signal_handlers(server_instance):
    """Configurar manejadores de señales para cierre limpio."""
    def signal_handler(signum, frame):
        _handle_shutdown_signal(signum, server_instance)
    
    signal.signal(SIGNAL_SIGINT, signal_handler)
    signal.signal(SIGNAL_SIGTERM, signal_handler)
    
def _handle_shutdown_signal(signal_number, server_instance):
    """Manejar señal de apagado del servidor."""
    print(f"\n🔔 Señal recibida: {signal_number}")
    print("🛑 Deteniendo servidor...")
    server_instance.running = False
    sys.exit(ARG_VALIDATION_EXIT_SUCCESS)

def validate_args(args):
    """Validar argumentos de línea de comandos."""
    _validate_port_range(args.port)
    _validate_host_format(args.host)
    
def _validate_port_range(port):
    """Validar que el puerto esté en el rango válido."""
    if not (MIN_PORT_NUMBER <= port <= MAX_PORT_NUMBER):
        print(f"❌ Error: Puerto {port} fuera de rango válido ({MIN_PORT_NUMBER}-{MAX_PORT_NUMBER})")
        sys.exit(ARG_VALIDATION_EXIT_ERROR)
        
def _validate_host_format(host):
    """Validar formato del host y pedir confirmación si es necesario."""
    valid_hosts = [DEFAULT_HOST_ALL_INTERFACES, DEFAULT_HOST_LOCALHOST, DEFAULT_HOST_LOOPBACK]
    if host not in valid_hosts and not _is_valid_ip_format(host):
        _prompt_host_confirmation(host)
        
def _is_valid_ip_format(host):
    """Verificar si el host tiene formato de IP válido."""
    return host.replace('.', '').isdigit()
    
def _prompt_host_confirmation(host):
    """Solicitar confirmación para host con formato inválido."""
    print(f"⚠️  Advertencia: Host '{host}' podría no ser válido")
    response = input("¿Continuar de todos modos? (s/N): ").strip().lower()
    if response != USER_INPUT_YES:
        sys.exit(ARG_VALIDATION_EXIT_SUCCESS)

def main():
    """Función principal del servidor."""
    parser = _create_argument_parser()
    args = parser.parse_args()
    
    validate_args(args)
    server = SimpleServer(host=args.host, port=args.port)
    setup_signal_handlers(server)
    
    _run_server_with_error_handling(server)
    
def _create_argument_parser():
    """Crear y configurar el parser de argumentos."""
    parser = argparse.ArgumentParser(
        description='Servidor de Batalla Naval sin ngrok',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_get_parser_epilog()
    )
    _add_parser_arguments(parser)
    return parser
    
def _get_parser_epilog():
    """Obtener texto de ayuda extendida para el parser."""
    return f"""
Ejemplos de uso:
  %(prog)s                          # Usar configuración por defecto
  %(prog)s --port 9000              # Usar puerto específico
  %(prog)s --host 192.168.1.100     # Usar IP específica
  %(prog)s --host 0.0.0.0 --port 8080 # Configuración para VPS/VM

Configuración por defecto:
  Host: {DEFAULT_HOST_ALL_INTERFACES} (todas las interfaces)
  Puerto: {DEFAULT_SERVER_PORT}"""
  
def _add_parser_arguments(parser):
    """Agregar argumentos al parser."""
    parser.add_argument(
        '--host', 
        default=DEFAULT_HOST_ALL_INTERFACES,
        help=f'Host/IP en la que escuchar (default: {DEFAULT_HOST_ALL_INTERFACES} para todas las interfaces)'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=DEFAULT_SERVER_PORT,
        help=f'Puerto en el que escuchar (default: {DEFAULT_SERVER_PORT})'
    )
    parser.add_argument(
        '--version', 
        action='version', 
        version='Batalla Naval Server v1.0'
    )
    
def _run_server_with_error_handling(server):
    """Ejecutar el servidor con manejo de errores."""
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n👋 Servidor interrumpido")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(ARG_VALIDATION_EXIT_ERROR)

if __name__ == "__main__":
    main()