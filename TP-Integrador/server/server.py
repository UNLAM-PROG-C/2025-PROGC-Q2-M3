import asyncio
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'classes'))

# Agregar el directorio actual al path para importar constants del servidor
sys.path.append(os.path.dirname(__file__))

from battleship_server import BattleshipServer
from constants import *

# Configurar logging
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

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