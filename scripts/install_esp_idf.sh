#!/bin/bash
# Script de instalación de ESP-IDF para macOS
# ESP-IDF v5.1 (stable)

set -e

echo "🚀 Instalando ESP-IDF v5.1..."
echo ""

# Directorio de instalación
ESP_DIR="$HOME/esp"
IDF_PATH="$ESP_DIR/esp-idf"

# 1. Instalar dependencias con Homebrew
echo "📦 Verificando dependencias..."
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew no encontrado. Instálalo desde: https://brew.sh"
    exit 1
fi

brew install cmake ninja dfu-util ccache

# 2. Crear directorio
mkdir -p "$ESP_DIR"
cd "$ESP_DIR"

# 3. Clonar ESP-IDF si no existe
if [ ! -d "$IDF_PATH" ]; then
    echo "📥 Clonando ESP-IDF v5.1..."
    git clone -b v5.1.5 --recursive https://github.com/espressif/esp-idf.git
else
    echo "✅ ESP-IDF ya existe en $IDF_PATH"
fi

# 4. Instalar herramientas
cd "$IDF_PATH"
echo "🔧 Instalando herramientas ESP32..."
./install.sh esp32,esp32s3

# 5. Configurar entorno
echo ""
echo "✅ ESP-IDF instalado correctamente!"
echo ""
echo "Para activar ESP-IDF en cada sesión, ejecuta:"
echo "  source $IDF_PATH/export.sh"
echo ""
echo "O agrégalo a tu ~/.zshrc:"
echo "  alias get_idf='. $IDF_PATH/export.sh'"
echo ""
