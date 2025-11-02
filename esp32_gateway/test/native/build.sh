#!/bin/bash

# --- build.sh para Tests Nativos ---

# Colores para la salida
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Crear directorio de build si no existe
mkdir -p build
cd build

# 2. Ejecutar CMake para configurar el proyecto
echo -e "${GREEN}--- Configurando con CMake... ---${NC}"
cmake ..
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error en la configuración de CMake.${NC}"
    exit 1
fi

# 3. Compilar el proyecto con make
echo -e "${GREEN}--- Compilando con make... ---${NC}"
make
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error durante la compilación.${NC}"
    exit 1
fi

# 4. Ejecutar el ejecutable de tests
echo -e "${GREEN}--- Ejecutando tests... ---${NC}"
./native_tests
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Uno o más tests fallaron.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Todos los tests pasaron exitosamente.${NC}"
exit 0
