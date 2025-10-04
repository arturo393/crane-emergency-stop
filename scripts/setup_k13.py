#!/usr/bin/env python3
"""
Script de configuración y diagnóstico para el dispositivo K13
"""

import os
import sys
import yaml
import serial.tools.list_ports
from pathlib import Path

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from k13_controller.main import K13Controller, K13Config
except ImportError as e:
    print(f"Error importando módulos K13: {e}")
    print("Asegúrate de que las dependencias estén instaladas")
    sys.exit(1)


def list_serial_ports():
    """Listar puertos serie disponibles"""
    print("=== Puertos Serie Disponibles ===")
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("No se encontraron puertos serie")
        return []
    
    port_list = []
    for i, port in enumerate(ports, 1):
        print(f"{i}. {port.device} - {port.description}")
        if port.hwid:
            print(f"   Hardware ID: {port.hwid}")
        port_list.append(port.device)
    
    return port_list


def load_config():
    """Cargar configuración desde archivo YAML"""
    config_path = Path(__file__).parent.parent / "config" / "k13_config.yaml"
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        print(f"Configuración cargada desde: {config_path}")
        return config_data
    except FileNotFoundError:
        print(f"Archivo de configuración no encontrado: {config_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parseando YAML: {e}")
        return None


def test_connection(port, baud_rate=9600):
    """Probar conexión con dispositivo K13"""
    print(f"\n=== Probando Conexión ===")
    print(f"Puerto: {port}")
    print(f"Baud Rate: {baud_rate}")
    
    try:
        config = K13Config(device_port=port, baud_rate=baud_rate)
        controller = K13Controller(config)
        
        print("Intentando conectar...")
        if controller.connect():
            print("✓ Conexión establecida exitosamente")
            
            # Obtener estado
            status = controller.get_status()
            print(f"Estado del dispositivo: {status}")
            
            # Desconectar
            controller.disconnect()
            print("✓ Desconexión exitosa")
            return True
        else:
            print("✗ Fallo en la conexión")
            return False
            
    except Exception as e:
        print(f"✗ Error durante la prueba: {e}")
        return False


def interactive_setup():
    """Configuración interactiva del sistema"""
    print("=== Configuración Interactiva K13 ===\n")
    
    # Listar puertos
    ports = list_serial_ports()
    
    if not ports:
        print("No hay puertos serie disponibles. Conecta el dispositivo K13 y reinicia.")
        return
    
    # Seleccionar puerto
    while True:
        try:
            selection = input(f"\nSelecciona puerto (1-{len(ports)}) o 'q' para salir: ")
            if selection.lower() == 'q':
                return
            
            port_index = int(selection) - 1
            if 0 <= port_index < len(ports):
                selected_port = ports[port_index]
                break
            else:
                print("Selección inválida")
        except ValueError:
            print("Por favor ingresa un número válido")
    
    # Seleccionar baud rate
    baud_rates = [9600, 19200, 38400, 57600, 115200]
    print("\nBaud rates disponibles:")
    for i, rate in enumerate(baud_rates, 1):
        print(f"{i}. {rate}")
    
    while True:
        try:
            selection = input(f"Selecciona baud rate (1-{len(baud_rates)}) [1]: ") or "1"
            rate_index = int(selection) - 1
            if 0 <= rate_index < len(baud_rates):
                selected_baud = baud_rates[rate_index]
                break
            else:
                print("Selección inválida")
        except ValueError:
            print("Por favor ingresa un número válido")
    
    # Probar conexión
    success = test_connection(selected_port, selected_baud)
    
    if success:
        # Generar configuración
        config_data = {
            'device': {
                'port': selected_port,
                'baud_rate': selected_baud,
                'timeout': 1.0,
                'retry_attempts': 3
            },
            'crane': {
                'max_speed': 100,
                'default_speed': 50,
                'acceleration_time': 2.0,
                'safety_timeout': 30.0
            },
            'safety': {
                'enable_emergency_stop': True,
                'max_continuous_operation': 300,
                'require_confirmation': True
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/k13_controller.log'
            }
        }
        
        # Guardar configuración
        config_path = Path(__file__).parent.parent / "config" / "k13_config.yaml"
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
        
        print(f"\n✓ Configuración guardada en: {config_path}")
    else:
        print("\n✗ Configuración no guardada debido a fallo en conexión")


def run_diagnostics():
    """Ejecutar diagnósticos del sistema"""
    print("=== Diagnósticos del Sistema K13 ===\n")
    
    # Verificar dependencias
    print("1. Verificando dependencias...")
    dependencies = ['serial', 'yaml', 'logging']
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"   ✓ {dep}")
        except ImportError:
            print(f"   ✗ {dep} - FALTANTE")
    
    # Verificar estructura de archivos
    print("\n2. Verificando estructura de archivos...")
    base_path = Path(__file__).parent.parent
    required_files = [
        'src/k13_controller/__init__.py',
        'src/k13_controller/main.py',
        'src/k13_controller/protocol.py',
        'src/k13_controller/serial_comm.py',
        'config/k13_config.yaml',
        'requirements.txt'
    ]
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"   ✓ {file_path}")
        else:
            print(f"   ✗ {file_path} - FALTANTE")
    
    # Cargar y verificar configuración
    print("\n3. Verificando configuración...")
    config = load_config()
    if config:
        print("   ✓ Archivo de configuración cargado")
        if 'device' in config and 'port' in config['device']:
            print(f"   ✓ Puerto configurado: {config['device']['port']}")
        else:
            print("   ✗ Puerto no configurado")
    else:
        print("   ✗ Error cargando configuración")
    
    # Probar conexión si hay configuración
    if config and 'device' in config:
        device_config = config['device']
        test_connection(
            device_config.get('port', '/dev/ttyUSB0'),
            device_config.get('baud_rate', 9600)
        )


def main():
    """Función principal del script"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'list-ports':
            list_serial_ports()
        elif command == 'test-connection':
            port = sys.argv[2] if len(sys.argv) > 2 else '/dev/ttyUSB0'
            baud = int(sys.argv[3]) if len(sys.argv) > 3 else 9600
            test_connection(port, baud)
        elif command == 'diagnostics':
            run_diagnostics()
        elif command == 'setup':
            interactive_setup()
        else:
            print("Comandos disponibles:")
            print("  list-ports    - Listar puertos serie")
            print("  test-connection [puerto] [baud] - Probar conexión")
            print("  diagnostics   - Ejecutar diagnósticos")
            print("  setup         - Configuración interactiva")
    else:
        interactive_setup()


if __name__ == "__main__":
    main()
