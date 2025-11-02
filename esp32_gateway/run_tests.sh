#!/bin/bash
# Script para ejecutar tests del ESP32 Gateway
# Uso: ./run_tests.sh [test_name]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════╗"
echo "║     ESP32 Gateway - Test Runner                  ║"
echo "║     EdgeBox-Lite ESP32-S3                        ║"
echo "╚═══════════════════════════════════════════════════╝"
echo -e "${NC}"

# Detectar puerto ESP32
echo -e "${YELLOW}🔍 Detecting ESP32...${NC}"
PORT=$(ls /dev/cu.usbserial* 2>/dev/null | head -1)

if [ -z "$PORT" ]; then
    PORT=$(ls /dev/cu.SLAB* 2>/dev/null | head -1)
fi

if [ -z "$PORT" ]; then
    PORT=$(ls /dev/ttyUSB* 2>/dev/null | head -1)
fi

if [ -z "$PORT" ]; then
    echo -e "${RED}❌ No ESP32 detected!${NC}"
    echo "Please connect ESP32 via USB"
    exit 1
fi

echo -e "${GREEN}✅ ESP32 found at: $PORT${NC}"
echo ""

# Lista de tests disponibles
TESTS=(
    "test_auth_manager:Auth Manager:No hardware required"
    "test_config_manager:Config Manager:Optional SD card"
    "test_sd_logger:SD Logger:Requires SD card"
    "test_ota_manager:OTA Manager:No hardware required"
    "test_ethernet_manager:Ethernet Manager:Requires W5500 + cable + router"
    "test_web_server:Web Server:Requires Ethernet working"
    "test_can_bus_init:CAN Bus Init:No physical bus required"
    "test_w5500_spi_init:W5500 SPI:Requires W5500 module"
    "test_digital_io:Digital I/O:Optional LEDs/wires"
)

# Si no se especifica test, mostrar menú
if [ -z "$1" ]; then
    echo -e "${BLUE}📋 Available Tests:${NC}"
    echo ""
    
    for i in "${!TESTS[@]}"; do
        IFS=':' read -r test_file test_name requirements <<< "${TESTS[$i]}"
        printf "${GREEN}%2d.${NC} %-25s ${YELLOW}%s${NC}\n" $((i+1)) "$test_name" "($requirements)"
    done
    
    echo ""
    echo -e "${BLUE}Usage:${NC}"
    echo "  ./run_tests.sh [number]        # Run specific test"
    echo "  ./run_tests.sh all             # Run all tests (recommended order)"
    echo "  ./run_tests.sh auth            # Run test_auth_manager (shortcut)"
    echo ""
    echo -e "${YELLOW}💡 Recommended order:${NC}"
    echo "  1. Auth Manager (no hardware)"
    echo "  2. Config Manager (no hardware)"
    echo "  3. SD Logger (with SD card)"
    echo "  4. Ethernet (with W5500 + cable)"
    echo ""
    exit 0
fi

# Resolver nombre de test
TEST_NAME=""
TEST_FILE=""

# Si es un número
if [[ "$1" =~ ^[0-9]+$ ]]; then
    INDEX=$((1 - 1))
    if [ $INDEX -ge 0 ] && [ $INDEX -lt ${#TESTS[@]} ]; then
        IFS=':' read -r TEST_FILE TEST_NAME requirements <<< "${TESTS[$INDEX]}"
    else
        echo -e "${RED}❌ Invalid test number: $1${NC}"
        exit 1
    fi
# Si es "all"
elif [ "$1" == "all" ]; then
    echo -e "${BLUE}🚀 Running ALL tests in recommended order...${NC}"
    echo ""
    
    # Orden recomendado (menos a más hardware)
    RECOMMENDED_ORDER=(0 1 3 6 2 7 4 5 8)
    
    for INDEX in "${RECOMMENDED_ORDER[@]}"; do
        IFS=':' read -r test_file test_name requirements <<< "${TESTS[$INDEX]}"
        
        echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}▶ Running: $test_name${NC}"
        echo -e "${YELLOW}Requirements: $requirements${NC}"
        echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
        echo ""
        
        # Compilar y flashear
        echo -e "${YELLOW}📦 Building $test_file...${NC}"
        idf.py build -DTEST_COMPONENT=$test_file
        
        echo -e "${YELLOW}📤 Flashing to $PORT...${NC}"
        idf.py -p $PORT flash
        
        echo -e "${YELLOW}📊 Opening monitor (Ctrl+] to exit)...${NC}"
        echo -e "${YELLOW}Press Enter to continue to next test after viewing results${NC}"
        idf.py -p $PORT monitor || true
        
        echo ""
        read -p "Press Enter to continue to next test..."
        echo ""
    done
    
    echo -e "${GREEN}✅ All tests completed!${NC}"
    exit 0
# Atajos
elif [ "$1" == "auth" ]; then
    TEST_FILE="test_auth_manager"
    TEST_NAME="Auth Manager"
elif [ "$1" == "config" ]; then
    TEST_FILE="test_config_manager"
    TEST_NAME="Config Manager"
elif [ "$1" == "sd" ]; then
    TEST_FILE="test_sd_logger"
    TEST_NAME="SD Logger"
elif [ "$1" == "ota" ]; then
    TEST_FILE="test_ota_manager"
    TEST_NAME="OTA Manager"
elif [ "$1" == "eth" ] || [ "$1" == "ethernet" ]; then
    TEST_FILE="test_ethernet_manager"
    TEST_NAME="Ethernet Manager"
elif [ "$1" == "web" ]; then
    TEST_FILE="test_web_server"
    TEST_NAME="Web Server"
elif [ "$1" == "can" ]; then
    TEST_FILE="test_can_bus_init"
    TEST_NAME="CAN Bus Init"
else
    # Buscar por nombre completo
    for test in "${TESTS[@]}"; do
        IFS=':' read -r test_file test_name requirements <<< "$test"
        if [ "$test_file" == "$1" ]; then
            TEST_FILE="$test_file"
            TEST_NAME="$test_name"
            break
        fi
    done
    
    if [ -z "$TEST_FILE" ]; then
        echo -e "${RED}❌ Unknown test: $1${NC}"
        echo "Run without arguments to see available tests"
        exit 1
    fi
fi

# Ejecutar test específico
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}▶ Running: $TEST_NAME${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""

# Verificar que el archivo existe
TEST_PATH="test/device/${TEST_FILE}.cpp"
if [ ! -f "$TEST_PATH" ]; then
    echo -e "${RED}❌ Test file not found: $TEST_PATH${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Building $TEST_FILE...${NC}"
idf.py build -DTEST_COMPONENT=$TEST_FILE

echo ""
echo -e "${YELLOW}📤 Flashing to $PORT...${NC}"
idf.py -p $PORT flash

echo ""
echo -e "${GREEN}✅ Flash complete!${NC}"
echo -e "${YELLOW}📊 Opening monitor (Ctrl+] to exit)...${NC}"
echo ""
sleep 2

idf.py -p $PORT monitor

echo ""
echo -e "${GREEN}✅ Test execution completed!${NC}"
