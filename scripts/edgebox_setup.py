#!/usr/bin/env python3
"""
Script de Configuración para EdgeBox Lite WiFi
Configuración automática del gateway para proyecto puente grúa
"""

import os
import subprocess
import yaml
from pathlib import Path

class EdgeBoxConfigurator:
    """Configurador para EdgeBox Lite WiFi"""

    def __init__(self, config_file="config/edgebox_config.yaml"):
        self.config_file = Path(config_file)
        self.config = self.load_config()

    def load_config(self):
        """Cargar configuración desde archivo YAML"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            return self.get_default_config()

    def get_default_config(self):
        """Configuración por defecto para puente grúa"""
        return {
            'device': {
                'name': 'EdgeBox-Lite-WiFi',
                'model': 'Advantech EdgeBox Lite WiFi',
                'role': 'CAN-Ethernet-Gateway'
            },
            'network': {
                'ethernet': {
                    'interface': 'eth0',
                    'ip': '192.168.1.100',
                    'netmask': '255.255.255.0',
                    'gateway': '192.168.1.1',
                    'dns': ['8.8.8.8', '1.1.1.1']
                },
                'wifi': {
                    'interface': 'wlan0',
                    'ssid': 'Crane-Control-WiFi',
                    'password': 'secure-password-2025',
                    'mode': 'AP',  # Access Point
                    'channel': 6,
                    'country': 'CL'
                }
            },
            'can_bus': {
                'interface': 'can0',
                'bitrate': 500000,  # 500kbps para CANopen
                'protocol': 'CANopen',
                'node_id': 1,
                'target_nodes': [2],  # ID del receptor R13
                'termination': True  # Terminador 120 ohm
            },
            'services': [
                {
                    'name': 'r13-controller',
                    'protocol': 'CANopen',
                    'target_node': 2,
                    'functions': ['emergency_stop', 'status_monitor']
                },
                {
                    'name': 'emergency-stop',
                    'trigger': 'GPIO_17',
                    'action': 'stop-all-motors',
                    'debounce_ms': 50
                }
            ],
            'logging': {
                'level': 'INFO',
                'file': '/var/log/crane-gateway.log',
                'max_size': '10MB',
                'backup_count': 5
            }
        }

    def run_command(self, command, description=""):
        """Ejecutar comando del sistema"""
        try:
            print(f"🔧 {description}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {description} - OK")
                return True
            else:
                print(f"❌ {description} - ERROR: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ {description} - EXCEPTION: {str(e)}")
            return False

    def configure_network(self):
        """Configurar red Ethernet y WiFi"""
        print("\n🌐 Configurando red...")

        # Configurar Ethernet estático
        eth_config = self.config['network']['ethernet']
        netplan_config = f"""
network:
  version: 2
  ethernets:
    {eth_config['interface']}:
      addresses:
        - {eth_config['ip']}/{self.netmask_to_cidr(eth_config['netmask'])}
      routes:
        - to: default
          via: {eth_config['gateway']}
      nameservers:
        addresses: {eth_config['dns']}
"""

        # Aplicar configuración de red
        with open('/etc/netplan/01-netcfg.yaml', 'w') as f:
            f.write(netplan_config)

        self.run_command("sudo netplan apply", "Aplicando configuración de red")

        # Configurar WiFi como Access Point
        wifi_config = self.config['network']['wifi']
        if wifi_config['mode'] == 'AP':
            self.setup_wifi_ap(wifi_config)

    def setup_wifi_ap(self, wifi_config):
        """Configurar WiFi como Access Point"""
        print("📶 Configurando WiFi Access Point...")

        # Instalar hostapd y dnsmasq
        self.run_command("sudo apt update", "Actualizando paquetes")
        self.run_command("sudo apt install -y hostapd dnsmasq", "Instalando hostapd y dnsmasq")

        # Configurar hostapd
        hostapd_config = f"""
interface={wifi_config['interface']}
driver=nl80211
ssid={wifi_config['ssid']}
hw_mode=g
channel={wifi_config['channel']}
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={wifi_config['password']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
country_code={wifi_config['country']}
"""

        with open('/etc/hostapd/hostapd.conf', 'w') as f:
            f.write(hostapd_config)

        # Configurar dnsmasq
        dnsmasq_config = """
interface=wlan0
dhcp-range=192.168.4.10,192.168.4.20,255.255.255.0,24h
"""

        with open('/etc/dnsmasq.conf', 'w') as f:
            f.write(dnsmasq_config)

        # Habilitar servicios
        self.run_command("sudo systemctl unmask hostapd", "Habilitando hostapd")
        self.run_command("sudo systemctl enable hostapd", "Activando hostapd")
        self.run_command("sudo systemctl enable dnsmasq", "Activando dnsmasq")

    def configure_can_bus(self):
        """Configurar interfaz CAN Bus"""
        print("\n🚗 Configurando CAN Bus...")

        can_config = self.config['can_bus']

        # Instalar herramientas CAN
        self.run_command("sudo apt install -y can-utils", "Instalando herramientas CAN")

        # Configurar interfaz CAN
        can_setup = f"""
# Configuración CAN Bus para puente grúa
sudo ip link set {can_config['interface']} type can bitrate {can_config['bitrate']}
sudo ip link set {can_config['interface']} up
"""

        # Crear script de configuración CAN
        with open('/usr/local/bin/setup-can.sh', 'w') as f:
            f.write(can_setup)

        os.chmod('/usr/local/bin/setup-can.sh', 0o755)

        # Ejecutar configuración
        self.run_command("sudo /usr/local/bin/setup-can.sh", "Configurando interfaz CAN")

        # Verificar configuración
        self.run_command(f"candump {can_config['interface']} & sleep 2; kill %1", "Verificando CAN Bus")

    def install_dependencies(self):
        """Instalar dependencias del proyecto"""
        print("\n📦 Instalando dependencias...")

        dependencies = [
            "python3-pip",
            "python3-can",
            "python3-yaml",
            "python3-socketcan",
            "git"
        ]

        self.run_command(f"sudo apt install -y {' '.join(dependencies)}", "Instalando dependencias del sistema")

        # Instalar python-can y otras librerías
        self.run_command("pip3 install python-can pyyaml", "Instalando librerías Python")

    def setup_project(self):
        """Configurar proyecto puente grúa"""
        print("\n🏗️ Configurando proyecto...")

        # Crear directorios
        project_dirs = [
            "/opt/crane-control",
            "/var/log/crane-control",
            "/etc/crane-control"
        ]

        for dir_path in project_dirs:
            os.makedirs(dir_path, exist_ok=True)

        # Clonar o copiar proyecto
        if not Path("/opt/crane-control").exists():
            self.run_command("git clone https://github.com/arturo393/crane-emergency-stop.git /opt/crane-control",
                           "Clonando repositorio del proyecto")

        # Instalar dependencias del proyecto
        os.chdir("/opt/crane-control")
        self.run_command("pip3 install -r requirements.txt", "Instalando dependencias del proyecto")

    def create_services(self):
        """Crear servicios del sistema"""
        print("\n⚙️ Creando servicios del sistema...")

        # Servicio CAN Gateway
        service_config = """
[Unit]
Description=Crane Control CAN Gateway
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/crane-control
ExecStart=/usr/bin/python3 src/k13_controller/rpi_can_gateway.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

        with open('/etc/systemd/system/crane-gateway.service', 'w') as f:
            f.write(service_config)

        self.run_command("sudo systemctl daemon-reload", "Recargando systemd")
        self.run_command("sudo systemctl enable crane-gateway", "Habilitando servicio gateway")

    def configure_gpio(self):
        """Configurar GPIO para botones de emergencia"""
        print("\n🔘 Configurando GPIO...")

        # Instalar RPi.GPIO (compatible con EdgeBox)
        self.run_command("pip3 install RPi.GPIO", "Instalando RPi.GPIO")

        # Configurar pin de emergencia
        gpio_config = """
# Configuración GPIO para botón de emergencia
import RPi.GPIO as GPIO

EMERGENCY_PIN = 17  # GPIO 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(EMERGENCY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def emergency_callback(channel):
    print("🚨 ¡BOTÓN DE EMERGENCIA PRESIONADO!")
    # Aquí va la lógica de parada de emergencia

GPIO.add_event_detect(EMERGENCY_PIN, GPIO.FALLING,
                     callback=emergency_callback,
                     bouncetime=200)
"""

        with open('/opt/crane-control/emergency_gpio.py', 'w') as f:
            f.write(gpio_config)

    def run_diagnostics(self):
        """Ejecutar diagnósticos del sistema"""
        print("\n🔍 Ejecutando diagnósticos...")

        diagnostics = [
            ("uname -a", "Información del sistema"),
            ("ip addr show", "Interfaces de red"),
            ("ip link show can0", "Estado CAN Bus"),
            ("python3 --version", "Versión Python"),
            ("pip3 list | grep can", "Librerías CAN instaladas")
        ]

        for command, description in diagnostics:
            print(f"\n📊 {description}:")
            self.run_command(command, "")

    def save_config(self):
        """Guardar configuración actual"""
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
        print(f"💾 Configuración guardada en {self.config_file}")

    @staticmethod
    def netmask_to_cidr(netmask):
        """Convertir netmask a CIDR"""
        return sum([bin(int(x)).count('1') for x in netmask.split('.')])

    def full_setup(self):
        """Configuración completa del EdgeBox"""
        print("🚀 Iniciando configuración completa de EdgeBox Lite WiFi")
        print("=" * 60)

        steps = [
            self.configure_network,
            self.configure_can_bus,
            self.install_dependencies,
            self.setup_project,
            self.create_services,
            self.configure_gpio,
            self.run_diagnostics,
            self.save_config
        ]

        for step in steps:
            try:
                step()
                print("-" * 40)
            except Exception as e:
                print(f"❌ Error en {step.__name__}: {str(e)}")
                continue

        print("✅ Configuración completada!")
        print("\n📋 Próximos pasos:")
        print("1. Reiniciar el dispositivo: sudo reboot")
        print("2. Verificar servicios: sudo systemctl status crane-gateway")
        print("3. Probar conexión CAN: candump can0")
        print("4. Conectar aplicación: python3 src/k13_controller/main.py")

def main():
    """Función principal"""
    print("EdgeBox Lite WiFi - Configurador para Puente Grúa")
    print("Proyecto: Control de Emergencia - Sistema R13 CANopen")
    print("-" * 55)

    configurator = EdgeBoxConfigurator()

    if len(os.sys.argv) > 1:
        command = os.sys.argv[1]
        if command == "network":
            configurator.configure_network()
        elif command == "can":
            configurator.configure_can_bus()
        elif command == "install":
            configurator.install_dependencies()
        elif command == "full":
            configurator.full_setup()
        else:
            print("Uso: python3 edgebox_setup.py [network|can|install|full]")
    else:
        print("Ejecutando configuración completa...")
        configurator.full_setup()

if __name__ == '__main__':
    main()