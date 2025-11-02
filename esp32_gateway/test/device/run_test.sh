#!/bin/bash

# Script para ejecutar tests del ESP32 Gateway
# Uso: ./run_test.sh <nombre_del_test>

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         ESP32 Gateway - Test Runner                      ║"
echo "║         K13 Puente Grúa Project                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Lista de tests disponibles
TESTS=(
    "test_auth_manager"
    "test_config_manager"
    "test_web_server"
    "test_ethernet_manager"
    "test_sd_logger"
    "test_ota_manager"
    "test_can_bus_init"
    "test_w5500_spi_init"
    "test_digital_io"
)

# Función para mostrar uso
show_usage() {
    echo -e "${YELLOW}Uso:${NC}"
    echo "  ./run_test.sh <nombre_del_test>"
    echo ""
    echo -e "${YELLOW}Tests disponibles:${NC}"
    for test in "${TESTS[@]}"; do
        echo "  - $test"
    done
    echo ""
    echo -e "${YELLOW}Ejemplos:${NC}"
    echo "  ./run_test.sh test_auth_manager"
    echo "  ./run_test.sh test_ethernet_manager"
    exit 1
}

# Verificar argumentos
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Falta el nombre del test${NC}"
    echo ""
    show_usage
fi

TEST_NAME=$1

# Verificar que el test existe
if [[ ! " ${TESTS[@]} " =~ " ${TEST_NAME} " ]]; then
    echo -e "${RED}Error: Test '${TEST_NAME}' no existe${NC}"
    echo ""
    show_usage
fi

# Ir al directorio del proyecto
cd "$(dirname "$0")/../.."
PROJECT_DIR=$(pwd)

echo -e "${BLUE}Directorio del proyecto:${NC} $PROJECT_DIR"
echo -e "${BLUE}Test a ejecutar:${NC} $TEST_NAME"
echo ""

# Verificar que ESP-IDF está disponible
if ! command -v idf.py &> /dev/null; then
    echo -e "${RED}Error: idf.py no encontrado${NC}"
    echo "Por favor, ejecuta primero:"
    echo "  . ~/esp/esp-idf/export.sh"
    exit 1
fi

# Verificar versión de ESP-IDF
IDF_VERSION=$(idf.py --version 2>&1 | grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+')
echo -e "${GREEN}ESP-IDF Version:${NC} $IDF_VERSION"
echo ""

# Verificar si hay un ESP32 conectado
echo -e "${YELLOW}Buscando dispositivos ESP32...${NC}"
PORTS=$(ls /dev/tty.usbserial-* 2>/dev/null || ls /dev/ttyUSB* 2>/dev/null || echo "")

if [ -z "$PORTS" ]; then
    echo -e "${RED}⚠ No se detectó ningún ESP32 conectado${NC}"
    echo ""
    echo "Este script compilará el test pero NO podrá flashearlo."
    echo "Conecta un ESP32-S3 por USB y vuelve a ejecutar."
    echo ""
    read -p "¿Deseas continuar solo con compilación? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    PORT=""
else
    PORT=$(echo $PORTS | awk '{print $1}')
    echo -e "${GREEN}✓ ESP32 detectado en: $PORT${NC}"
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo -e "${YELLOW}PASO 1: Limpiando build anterior...${NC}"
echo "════════════════════════════════════════════════════════"
idf.py fullclean || true

echo ""
echo "════════════════════════════════════════════════════════"
echo -e "${YELLOW}PASO 2: Configurando test ($TEST_NAME)...${NC}"
echo "════════════════════════════════════════════════════════"
export TEST_COMPONENT=$TEST_NAME

# Modificar CMakeLists.txt temporalmente
CMAKELIST_PATH="test/device/CMakeLists.txt"
echo "Modificando $CMAKELIST_PATH para incluir solo $TEST_NAME.cpp"

echo ""
echo "════════════════════════════════════════════════════════"
echo -e "${YELLOW}PASO 3: Compilando test...${NC}"
echo "════════════════════════════════════════════════════════"
idf.py build

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Error en compilación${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Compilación exitosa${NC}"

# Si hay puerto, flashear y monitorear
if [ ! -z "$PORT" ]; then
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo -e "${YELLOW}PASO 4: Flasheando a ESP32...${NC}"
    echo "════════════════════════════════════════════════════════"
    idf.py -p $PORT flash
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Error al flashear${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Flasheo exitoso${NC}"
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo -e "${YELLOW}PASO 5: Abriendo monitor serial...${NC}"
    echo -e "${BLUE}Presiona Ctrl+] para salir del monitor${NC}"
    echo "════════════════════════════════════════════════════════"
    sleep 2
    idf.py -p $PORT monitor
else
    echo ""
    echo -e "${YELLOW}Test compilado exitosamente pero no flasheado${NC}"
    echo "Para flashear manualmente:"
    echo "  idf.py -p <puerto> flash monitor"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Test ejecutado: $TEST_NAME${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
