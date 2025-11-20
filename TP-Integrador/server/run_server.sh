#!/bin/bash

# Script para iniciar el servidor de Batalla Naval en VM Linux
# Autor: Batalla Naval Server
# Versión: 1.0

# Configuración de colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuración por defecto
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8888"
PYTHON_CMD="python3"

# Variables de configuración (pueden ser sobrescritas por variables de entorno)
SERVER_HOST=${SERVER_HOST:-$DEFAULT_HOST}
SERVER_PORT=${SERVER_PORT:-$DEFAULT_PORT}

# Función para mostrar el banner
show_banner() {
    clear
    echo -e "${CYAN}========================================================================"
    echo -e "               ${WHITE}BATALLA NAVAL - SERVIDOR EN VM LINUX${CYAN}"
    echo -e "========================================================================"
    echo -e "${NC}"
    echo -e "${BLUE}Este script iniciará el servidor en la VM de Linux${NC}"
    echo -e "${BLUE}Los jugadores podrán conectarse usando la IP pública de la VM${NC}"
    echo -e ""
    echo -e "${YELLOW}IMPORTANTE:${NC}"
    echo -e "${WHITE}- Asegúrate de que el puerto esté abierto en el firewall${NC}"
    echo -e "${WHITE}- Los jugadores se conectarán usando: <IP_PUBLICA_VM>:<PUERTO>${NC}"
    echo -e "${WHITE}- Mantén esta sesión activa mientras el servidor esté corriendo${NC}"
    echo -e ""
    echo -e "${CYAN}========================================================================${NC}"
    echo -e ""
}

# Función para mostrar la configuración actual
show_config() {
    echo -e "${PURPLE}📋 CONFIGURACIÓN DEL SERVIDOR:${NC}"
    echo -e "${CYAN}========================================================================${NC}"
    echo -e "${WHITE}🌐 Host: ${GREEN}$SERVER_HOST${NC}"
    echo -e "${WHITE}🔌 Puerto: ${GREEN}$SERVER_PORT${NC}"
    
    # Intentar obtener la IP pública
    echo -e "${WHITE}🌍 Detectando IP pública...${NC}"
    PUBLIC_IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || curl -s --max-time 5 ipinfo.io/ip 2>/dev/null || echo "No detectada")
    
    if [ "$PUBLIC_IP" != "No detectada" ]; then
        echo -e "${WHITE}📡 IP Pública detectada: ${GREEN}$PUBLIC_IP${NC}"
        echo -e "${WHITE}🔗 URL de conexión para clientes: ${YELLOW}$PUBLIC_IP:$SERVER_PORT${NC}"
    else
        echo -e "${YELLOW}⚠️  No se pudo detectar la IP pública automáticamente${NC}"
        echo -e "${WHITE}💡 Usa el comando: ${CYAN}curl ifconfig.me${NC} para obtenerla manualmente"
    fi
    
    echo -e "${CYAN}========================================================================${NC}"
    echo -e ""
}

# Función para verificar dependencias
check_dependencies() {
    echo -e "${BLUE}🔍 Verificando dependencias...${NC}"
    
    # Verificar Python 3
    if ! command -v $PYTHON_CMD &> /dev/null; then
        echo -e "${RED}❌ Error: Python 3 no está instalado${NC}"
        echo -e "${WHITE}💡 Instala Python 3:${NC}"
        echo -e "${CYAN}   Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip${NC}"
        echo -e "${CYAN}   CentOS/RHEL: sudo yum install python3 python3-pip${NC}"
        exit 1
    fi
    
    # Verificar pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${YELLOW}⚠️  pip3 no encontrado, intentando instalar...${NC}"
        sudo apt update && sudo apt install python3-pip -y 2>/dev/null || sudo yum install python3-pip -y 2>/dev/null
    fi
    
    echo -e "${GREEN}✅ Python 3 encontrado: $($PYTHON_CMD --version)${NC}"
    
    # Verificar e instalar dependencias de Python
    if [ -f "requirements.txt" ]; then
        echo -e "${BLUE}📦 Instalando dependencias de Python...${NC}"
        pip3 install -r requirements.txt --user --quiet
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Dependencias instaladas correctamente${NC}"
        else
            echo -e "${YELLOW}⚠️  Algunas dependencias podrían no haberse instalado correctamente${NC}"
        fi
    fi
    
    echo -e ""
}

# Función para verificar el firewall
check_firewall() {
    echo -e "${BLUE}🔥 Verificando configuración del firewall...${NC}"
    
    # Verificar si ufw está instalado y activo
    if command -v ufw &> /dev/null; then
        UFW_STATUS=$(sudo ufw status 2>/dev/null | grep "Status:" | awk '{print $2}')
        if [ "$UFW_STATUS" = "active" ]; then
            echo -e "${WHITE}🛡️  UFW está activo${NC}"
            
            # Verificar si el puerto está abierto
            UFW_RULE=$(sudo ufw status | grep "$SERVER_PORT" 2>/dev/null)
            if [ -z "$UFW_RULE" ]; then
                echo -e "${YELLOW}⚠️  Puerto $SERVER_PORT no está abierto en UFW${NC}"
                echo -e "${WHITE}💡 Para abrir el puerto ejecuta:${NC}"
                echo -e "${GREEN}   sudo ufw allow $SERVER_PORT${NC}"
                echo -e "${GREEN}   sudo ufw reload${NC}"
                echo -e ""
                read -p "¿Quieres abrir el puerto automáticamente? (s/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Ss]$ ]]; then
                    sudo ufw allow $SERVER_PORT
                    sudo ufw reload
                    echo -e "${GREEN}✅ Puerto abierto en UFW${NC}"
                fi
            else
                echo -e "${GREEN}✅ Puerto $SERVER_PORT está abierto en UFW${NC}"
            fi
        else
            echo -e "${BLUE}ℹ️  UFW no está activo${NC}"
        fi
    else
        echo -e "${BLUE}ℹ️  UFW no está instalado${NC}"
    fi
    
    # Verificar firewalld (CentOS/RHEL)
    if command -v firewall-cmd &> /dev/null; then
        if systemctl is-active --quiet firewalld; then
            echo -e "${WHITE}🛡️  FirewallD está activo${NC}"
            
            # Verificar si el puerto está abierto
            if ! sudo firewall-cmd --query-port=$SERVER_PORT/tcp --quiet 2>/dev/null; then
                echo -e "${YELLOW}⚠️  Puerto $SERVER_PORT no está abierto en FirewallD${NC}"
                echo -e "${WHITE}💡 Para abrir el puerto ejecuta:${NC}"
                echo -e "${GREEN}   sudo firewall-cmd --permanent --add-port=$SERVER_PORT/tcp${NC}"
                echo -e "${GREEN}   sudo firewall-cmd --reload${NC}"
                echo -e ""
                read -p "¿Quieres abrir el puerto automáticamente? (s/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Ss]$ ]]; then
                    sudo firewall-cmd --permanent --add-port=$SERVER_PORT/tcp
                    sudo firewall-cmd --reload
                    echo -e "${GREEN}✅ Puerto abierto en FirewallD${NC}"
                fi
            else
                echo -e "${GREEN}✅ Puerto $SERVER_PORT está abierto en FirewallD${NC}"
            fi
        else
            echo -e "${BLUE}ℹ️  FirewallD no está activo${NC}"
        fi
    fi
    
    echo -e ""
}

# Función para mostrar instrucciones para clientes
show_client_instructions() {
    echo -e "${PURPLE}📝 INSTRUCCIONES PARA LOS CLIENTES:${NC}"
    echo -e "${CYAN}========================================================================${NC}"
    echo -e "${WHITE}1. Los jugadores deben ejecutar el cliente de Batalla Naval${NC}"
    echo -e "${WHITE}2. En la pantalla de conexión, ingresar:${NC}"
    
    if [ "$PUBLIC_IP" != "No detectada" ] && [ "$PUBLIC_IP" != "" ]; then
        echo -e "${WHITE}   - Host/IP: ${YELLOW}$PUBLIC_IP${NC}"
    else
        echo -e "${WHITE}   - Host/IP: ${YELLOW}<IP_PUBLICA_DE_ESTA_VM>${NC}"
    fi
    
    echo -e "${WHITE}   - Puerto: ${YELLOW}$SERVER_PORT${NC}"
    echo -e "${WHITE}3. Hacer clic en 'Conectar'${NC}"
    echo -e "${WHITE}4. ¡A jugar!${NC}"
    echo -e ""
    echo -e "${BLUE}💡 Tip: Puedes obtener la IP pública con: ${CYAN}curl ifconfig.me${NC}"
    echo -e "${CYAN}========================================================================${NC}"
    echo -e ""
}

# Función para mostrar opciones de ejecución en background
show_background_options() {
    echo -e "${PURPLE}🔧 OPCIONES AVANZADAS:${NC}"
    echo -e "${CYAN}========================================================================${NC}"
    echo -e "${WHITE}Para ejecutar el servidor en background (recomendado para producción):${NC}"
    echo -e "${GREEN}   nohup ./run_server.sh > server.log 2>&1 &${NC}"
    echo -e ""
    echo -e "${WHITE}Para ver los logs en tiempo real:${NC}"
    echo -e "${GREEN}   tail -f server.log${NC}"
    echo -e ""
    echo -e "${WHITE}Para detener el servidor en background:${NC}"
    echo -e "${GREEN}   pkill -f start_server.py${NC}"
    echo -e "${CYAN}========================================================================${NC}"
    echo -e ""
}

# Función para verificar si el archivo del servidor existe
check_server_file() {
    if [ ! -f "start_server.py" ]; then
        echo -e "${RED}❌ Error: No se encontró el archivo start_server.py${NC}"
        echo -e "${WHITE}💡 Asegúrate de ejecutar este script desde el directorio del juego${NC}"
        exit 1
    fi
}

# Función principal
main() {
    # Mostrar banner
    show_banner
    
    # Verificar archivo del servidor
    check_server_file
    
    # Mostrar configuración
    show_config
    
    # Verificar dependencias
    check_dependencies
    
    # Verificar firewall
    check_firewall
    
    # Mostrar instrucciones
    show_client_instructions
    
    # Mostrar opciones avanzadas
    show_background_options
    
    # Pausa antes de iniciar
    echo -e "${CYAN}========================================================================${NC}"
    echo -e "${WHITE}⚡ Presiona Enter para iniciar el servidor...${NC}"
    echo -e "${RED}🛑 Usa Ctrl+C para detener el servidor${NC}"
    echo -e "${CYAN}========================================================================${NC}"
    read
    
    # Ejecutar el servidor de Python
    echo -e "${GREEN}🚀 Iniciando servidor...${NC}"
    echo -e ""
    
    # Ejecutar con los parámetros configurados
    $PYTHON_CMD start_server.py --host "$SERVER_HOST" --port "$SERVER_PORT"
    
    # El script llega aquí cuando el servidor se detiene
    echo -e ""
    echo -e "${YELLOW}🔔 Servidor detenido${NC}"
    echo -e "${WHITE}Presiona Enter para salir...${NC}"
    read
}

# Manejar señales para cierre limpio
cleanup() {
    echo -e ""
    echo -e "${YELLOW}🛑 Deteniendo servidor...${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Verificar si se está ejecutando como script principal
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi