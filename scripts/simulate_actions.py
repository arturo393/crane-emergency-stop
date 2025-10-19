#!/usr/bin/env python3
"""
Script local para simular GitHub Actions - EDS Progress Tracker
Ejecutar antes de hacer push para verificar el comportamiento
"""

import os
import sys
from pathlib import Path

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def check_file(path, name):
    """Verificar si un archivo existe"""
    exists = Path(path).exists()
    icon = f"{Colors.GREEN}✅{Colors.END}" if exists else f"{Colors.RED}❌{Colors.END}"
    print(f"{icon} {name}: {path}")
    return exists

def analyze_implementation():
    """Analizar el estado de la implementación"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 Analizando Implementación...{Colors.END}\n")
    
    checklist = {}
    
    # 1. EDS file created
    checklist['EDS File Created'] = check_file(
        'config/danfoss_r13f_minimal.eds',
        'EDS File'
    )
    
    # 2. Gateway loads EDS
    checklist['Gateway Loads EDS'] = False
    try:
        with open('src/bl335_gateway/main.py', 'r') as f:
            content = f.read()
            if 'danfoss_r13f' in content and 'add_node' in content:
                checklist['Gateway Loads EDS'] = True
                print(f"{Colors.GREEN}✅{Colors.END} Gateway Loads EDS: True")
            else:
                print(f"{Colors.RED}❌{Colors.END} Gateway Loads EDS: False")
    except Exception as e:
        print(f"{Colors.RED}❌{Colors.END} Gateway Loads EDS: Error - {e}")
    
    # 3. SDO Implemented
    checklist['SDO Implemented'] = False
    try:
        with open('src/bl335_gateway/main.py', 'r') as f:
            content = f.read()
            if '0x6040' in content and '0x6041' in content and 'sdo' in content:
                checklist['SDO Implemented'] = True
                print(f"{Colors.GREEN}✅{Colors.END} SDO Implemented: True")
            else:
                print(f"{Colors.RED}❌{Colors.END} SDO Implemented: False")
    except Exception as e:
        print(f"{Colors.RED}❌{Colors.END} SDO Implemented: Error - {e}")
    
    # 4. PDO Configured
    checklist['PDO Configured'] = False
    try:
        with open('config/danfoss_r13f_minimal.eds', 'r') as f:
            content = f.read()
            if all(x in content for x in ['[1400]', '[1600]', '[1800]', '[1A00]']):
                checklist['PDO Configured'] = True
                print(f"{Colors.GREEN}✅{Colors.END} PDO Configured: True")
            else:
                print(f"{Colors.RED}❌{Colors.END} PDO Configured: False")
    except Exception as e:
        print(f"{Colors.RED}❌{Colors.END} PDO Configured: Error - {e}")
    
    # 5. CiA 402 Objects
    checklist['CiA 402 Objects'] = False
    try:
        with open('config/danfoss_r13f_minimal.eds', 'r') as f:
            content = f.read()
            if all(x in content for x in ['[6040]', '[6041]', '[606C]', '[6064]']):
                checklist['CiA 402 Objects'] = True
                print(f"{Colors.GREEN}✅{Colors.END} CiA 402 Objects: True")
            else:
                print(f"{Colors.RED}❌{Colors.END} CiA 402 Objects: False")
    except Exception as e:
        print(f"{Colors.RED}❌{Colors.END} CiA 402 Objects: Error - {e}")
    
    # 6. Tests Created
    checklist['Tests Created'] = check_file(
        'tests/e2e/test_integrated_system.py',
        'E2E Tests'
    )
    
    return checklist

def calculate_progress(checklist):
    """Calcular porcentaje de progreso"""
    completed = sum(1 for v in checklist.values() if v)
    total = len(checklist)
    percentage = (completed * 100) // total
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}📊 Progreso de Implementación{Colors.END}\n")
    print(f"Completado: {completed}/{total} tareas")
    print(f"Porcentaje: {percentage}%")
    
    # Barra de progreso
    bar_length = 20
    filled = int((percentage / 100) * bar_length)
    bar = '█' * filled + '░' * (bar_length - filled)
    
    if percentage >= 80:
        color = Colors.GREEN
    elif percentage >= 60:
        color = Colors.YELLOW
    else:
        color = Colors.RED
    
    print(f"Progress: [{color}{bar}{Colors.END}] {percentage}%")
    
    return percentage

def validate_eds():
    """Validar sintaxis del EDS"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🔬 Validando EDS...{Colors.END}\n")
    
    try:
        import configparser
        
        config = configparser.ConfigParser()
        config.read('config/danfoss_r13f_minimal.eds')
        
        # Secciones obligatorias
        required = {
            'DeviceInfo': 'Información del dispositivo',
            '1000': 'Device Type',
            '1001': 'Error Register',
            '1018': 'Identity Object',
            '6040': 'Control Word',
            '6041': 'Status Word'
        }
        
        all_valid = True
        for section, description in required.items():
            if section in config.sections():
                print(f"{Colors.GREEN}✅{Colors.END} [{section}] {description}")
            else:
                print(f"{Colors.RED}❌{Colors.END} [{section}] {description} - MISSING")
                all_valid = False
        
        if all_valid:
            print(f"\n{Colors.GREEN}✅ EDS syntax is valid{Colors.END}")
        else:
            print(f"\n{Colors.RED}❌ EDS has missing sections{Colors.END}")
        
        return all_valid
        
    except Exception as e:
        print(f"{Colors.RED}❌ EDS validation failed: {e}{Colors.END}")
        return False

def generate_markdown_checklist(checklist):
    """Generar checklist en formato Markdown"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}📋 Checklist Markdown{Colors.END}\n")
    
    md = "### 📋 Implementation Checklist\n\n"
    for task, completed in checklist.items():
        icon = "✅" if completed else "⬜"
        md += f"{icon} {task}\n"
    
    print(md)
    return md

def main():
    """Función principal"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("🤖 EDS Progress Tracker - Local Simulation")
    print("=" * 60)
    print(f"{Colors.END}")
    
    # Verificar que estamos en el directorio correcto
    if not Path('.git').exists():
        print(f"{Colors.RED}❌ Error: No estás en el directorio raíz del repositorio{Colors.END}")
        sys.exit(1)
    
    # Analizar implementación
    checklist = analyze_implementation()
    
    # Validar EDS
    eds_valid = validate_eds()
    
    # Calcular progreso
    percentage = calculate_progress(checklist)
    
    # Generar checklist
    markdown = generate_markdown_checklist(checklist)
    
    # Resumen final
    print(f"\n{Colors.BOLD}{Colors.BLUE}📝 Resumen{Colors.END}\n")
    print(f"EDS válido: {'✅ Sí' if eds_valid else '❌ No'}")
    print(f"Progreso: {percentage}%")
    print(f"Estado: {'🎉 Casi completo!' if percentage >= 80 else '🚧 En progreso' if percentage >= 50 else '🔨 Comenzando'}")
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}✅ Simulación completada{Colors.END}")
    print(f"\n{Colors.YELLOW}💡 Tip: Haz push para activar las GitHub Actions reales{Colors.END}\n")

if __name__ == '__main__':
    main()
