#!/usr/bin/env python3
"""
Simulador CANopen Completo para Danfoss R13 F

Simula completamente el receptor Danfoss R13 F con soporte PDO,
Object Dictionary CiA 402, y estados realistas del dispositivo.
Incluye modo batch para testing automatizado.
"""

import can
import canopen
import time
import logging
import random
from threading import Thread, Event, Lock
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("R13F_Simulator")


class OperationMode(Enum):
    """Modos de operación según CiA 402"""
    NO_MODE = 0
    PROFILE_POSITION = 1
    PROFILE_VELOCITY = 3
    HOMING = 6
    CYCLIC_SYNC_POSITION = 8
    CYCLIC_SYNC_VELOCITY = 9


class DeviceState(Enum):
    """Estados del dispositivo según CiA 402"""
    NOT_READY_TO_SWITCH_ON = 0
    SWITCH_ON_DISABLED = 1
    READY_TO_SWITCH_ON = 2
    SWITCHED_ON = 3
    OPERATION_ENABLED = 4
    QUICK_STOP_ACTIVE = 5
    FAULT_REACTION_ACTIVE = 6
    FAULT = 7


class R13FSimulator:
    """Simulador completo del receptor Danfoss R13 F con CANopen CiA 402"""

    def __init__(self, channel='vcan0', node_id=1, batch_mode=False, bus=None):
        """
        Inicializar simulador

        Args:
            channel: Canal CAN virtual (default: vcan0)
            node_id: ID del nodo CANopen (default: 1)
            batch_mode: Modo batch para testing automatizado
            bus: Bus CAN pre-creado (opcional, para integración con gateway)
        """
        self.channel = channel
        self.node_id = node_id
        self.batch_mode = batch_mode
        self.bus = bus  # Puede ser None o un bus pre-creado
        self.running = Event()
        self.state_lock = Lock()
        self.external_bus = bus is not None  # Flag para saber si es bus externo

        # Estado del dispositivo según CiA 402
        self.device_state = DeviceState.SWITCH_ON_DISABLED
        self.operation_mode = OperationMode.PROFILE_VELOCITY
        self.operation_mode_display = OperationMode.PROFILE_VELOCITY

        # Object Dictionary simulado (CiA 402)
        self.object_dictionary = {
            # Control Word - 0x6040
            0x6040: {'value': 0x0000, 'access': 'RW', 'type': 'UINT16'},
            # Status Word - 0x6041
            0x6041: {'value': 0x0000, 'access': 'RO', 'type': 'UINT16'},
            # Modes of Operation - 0x6060
            0x6060: {'value': OperationMode.PROFILE_VELOCITY.value, 'access': 'RW', 'type': 'INT8'},
            # Modes of Operation Display - 0x6061
            0x6061: {'value': OperationMode.PROFILE_VELOCITY.value, 'access': 'RO', 'type': 'INT8'},
            # Target Position - 0x607A
            0x607A: {'value': 0, 'access': 'RW', 'type': 'INT32'},
            # Profile Velocity - 0x6081
            0x6081: {'value': 1000, 'access': 'RW', 'type': 'UINT32'},
            # Velocity Actual Value - 0x606C
            0x606C: {'value': 0, 'access': 'RO', 'type': 'INT32'},
            # Position Actual Value - 0x6064
            0x6064: {'value': 0, 'access': 'RO', 'type': 'INT32'},
        }

        # Estado de PDO
        self.pdo_data = {
            'rpdo1': {'cob_id': 0x200 + node_id, 'data': [0x00] * 8},
            'tpdo1': {'cob_id': 0x180 + node_id, 'data': [0x00] * 8, 'period': 100},
            'tpdo2': {'cob_id': 0x280 + node_id, 'data': [0x00] * 8, 'period': 200},
        }

        # Estadísticas
        self.stats = {
            'heartbeats_sent': 0,
            'pdo_sent': 0,
            'sdo_requests': 0,
            'emergency_stops': 0,
            'errors': 0,
            'start_time': time.time()
        }

        # Simulación de movimiento
        self.target_velocity = 0
        self.actual_velocity = 0
        self.target_position = 0
        self.actual_position = 0
        
        # Historial de mensajes CAN (para Web UI)
        self.message_history = []
        self.max_message_history = 100

        logger.info(f"Simulador R13 F inicializado: Node ID={node_id}, Channel={channel}, Batch Mode={batch_mode}")

    def start(self):
        """Iniciar simulador"""
        try:
            # Crear bus CAN virtual solo si no se proporcionó uno externo
            if not self.external_bus:
                self.bus = can.interface.Bus(
                    channel=self.channel,
                    interface='socketcan',
                    bitrate=250000
                )
                logger.info(f"Bus CAN creado: {self.channel}")
            else:
                logger.info(f"Usando bus CAN externo")

            self.running.set()
            self._update_status_word()

            # Iniciar threads
            Thread(target=self._heartbeat_task, daemon=True).start()
            Thread(target=self._pdo_transmit_task, daemon=True).start()
            Thread(target=self._receive_task, daemon=True).start()
            Thread(target=self._simulation_task, daemon=True).start()

            logger.info("Simulador iniciado correctamente")
            if not self.batch_mode:
                print("🚀 Simulador R13 F CANopen iniciado")

        except Exception as e:
            logger.error(f"Error iniciando simulador: {e}")
            if not self.batch_mode:
                print("❌ Error iniciando simulador")
                print("Asegúrate de crear el canal virtual:")
                print("  sudo modprobe vcan")
                print("  sudo ip link add dev vcan0 type vcan")
                print("  sudo ip link set up vcan0")

    def stop(self):
        """Detener simulador"""
        self.running.clear()
        if self.bus:
            self.bus.shutdown()
        logger.info("Simulador detenido")
    
    def _log_message(self, msg: can.Message, is_rx: bool = False):
        """
        Registrar mensaje en historial para Web UI
        
        Args:
            msg: Mensaje CAN
            is_rx: True si es recibido (RX), False si es transmitido (TX)
        """
        # Agregar atributo de dirección al mensaje
        msg.is_rx = is_rx
        
        # Agregar al historial (buffer circular)
        self.message_history.append(msg)
        if len(self.message_history) > self.max_message_history:
            self.message_history.pop(0)

    def _heartbeat_task(self):
        """Enviar heartbeat cada 500ms"""
        while self.running.is_set():
            try:
                # Heartbeat CANopen: COB-ID = 0x700 + Node ID
                cob_id = 0x700 + self.node_id

                # Estado según CiA 402
                state_byte = self._get_state_byte()

                msg = can.Message(
                    arbitration_id=cob_id,
                    data=[state_byte],
                    is_extended_id=False
                )

                self.bus.send(msg)
                self._log_message(msg, is_rx=False)  # TX
                self.stats['heartbeats_sent'] += 1

                if not self.batch_mode and self.stats['heartbeats_sent'] % 20 == 0:
                    logger.debug(f"Heartbeat: {self.stats['heartbeats_sent']}")

            except Exception as e:
                logger.error(f"Error enviando heartbeat: {e}")
                self.stats['errors'] += 1

            time.sleep(0.5)

    def _pdo_transmit_task(self):
        """Enviar PDOs periódicos"""
        last_tpdo1 = time.time()
        last_tpdo2 = time.time()

        while self.running.is_set():
            try:
                current_time = time.time()

                # TPDO1 - Estado del dispositivo (cada 100ms)
                if current_time - last_tpdo1 >= self.pdo_data['tpdo1']['period'] / 1000.0:
                    self._send_tpdo1()
                    last_tpdo1 = current_time

                # TPDO2 - Información adicional (cada 200ms)
                if current_time - last_tpdo2 >= self.pdo_data['tpdo2']['period'] / 1000.0:
                    self._send_tpdo2()
                    last_tpdo2 = current_time

            except Exception as e:
                logger.error(f"Error en PDO transmit: {e}")
                self.stats['errors'] += 1

            time.sleep(0.01)  # 10ms para precisión

    def _send_tpdo1(self):
        """Enviar TPDO1 - Estado principal"""
        try:
            # Status Word (2 bytes)
            status_word = self.object_dictionary[0x6041]['value']
            # Actual Velocity (4 bytes)
            velocity = int(self.actual_velocity)
            # Actual Position (4 bytes, simplificado)
            position = int(self.actual_position)

            data = [
                status_word & 0xFF,          # Status Word LSB
                (status_word >> 8) & 0xFF,   # Status Word MSB
                velocity & 0xFF,             # Velocity LSB
                (velocity >> 8) & 0xFF,
                (velocity >> 16) & 0xFF,
                (velocity >> 24) & 0xFF,     # Velocity MSB
                position & 0xFF,             # Position LSB
                (position >> 8) & 0xFF       # Position byte 1
            ]

            msg = can.Message(
                arbitration_id=self.pdo_data['tpdo1']['cob_id'],
                data=data,
                is_extended_id=False
            )

            self.bus.send(msg)
            self._log_message(msg, is_rx=False)  # TX
            self.stats['pdo_sent'] += 1

            if not self.batch_mode:
                logger.debug(f"TPDO1 enviado: Status=0x{status_word:04X}, Vel={velocity}")

        except Exception as e:
            logger.error(f"Error enviando TPDO1: {e}")

    def _send_tpdo2(self):
        """Enviar TPDO2 - Información adicional"""
        try:
            # Operation Mode
            op_mode = self.operation_mode_display.value
            # Error code (0 = no error)
            error_code = 0
            # Temperature (simulado)
            temperature = 25 + random.randint(-5, 5)

            data = [
                op_mode,                    # Operation Mode
                error_code & 0xFF,          # Error Code LSB
                (error_code >> 8) & 0xFF,   # Error Code MSB
                temperature & 0xFF,         # Temperature
                0x00, 0x00, 0x00, 0x00     # Reservado
            ]

            msg = can.Message(
                arbitration_id=self.pdo_data['tpdo2']['cob_id'],
                data=data,
                is_extended_id=False
            )

            self.bus.send(msg)
            self._log_message(msg, is_rx=False)  # TX

            if not self.batch_mode:
                logger.debug(f"TPDO2 enviado: Mode={op_mode}, Temp={temperature}°C")

        except Exception as e:
            logger.error(f"Error enviando TPDO2: {e}")

    def _receive_task(self):
        """Recibir y procesar mensajes CAN"""
        while self.running.is_set():
            try:
                msg = self.bus.recv(timeout=0.1)
                if msg:
                    self._log_message(msg, is_rx=True)  # RX
                    self._process_message(msg)
            except Exception as e:
                logger.error(f"Error recibiendo mensaje: {e}")

    def _process_message(self, msg: can.Message):
        """Procesar mensaje CAN recibido"""
        cob_id = msg.arbitration_id
        data = msg.data

        if not self.batch_mode:
            logger.debug(f"RX: ID=0x{cob_id:03X}, Data={data.hex()}")

        # NMT (Network Management) - COB-ID 0x000
        if cob_id == 0x000:
            self._handle_nmt(data)

        # SDO Request - COB-ID 0x600 + Node ID
        elif cob_id == 0x600 + self.node_id:
            self._handle_sdo_request(data)

        # RPDO1 - COB-ID 0x200 + Node ID
        elif cob_id == self.pdo_data['rpdo1']['cob_id']:
            self._handle_rpdo1(data)

        # Emergency Stop - COB-ID específico
        elif cob_id == 0x080 + self.node_id:  # Emergency
            self._handle_emergency_stop(data)

        else:
            if not self.batch_mode:
                logger.debug(f"Mensaje no manejado: COB-ID=0x{cob_id:03X}")

    def _handle_nmt(self, data):
        """Manejar comandos NMT"""
        if len(data) < 2:
            return

        command = data[0]
        node_id = data[1]

        # Si el comando es para este nodo o broadcast (0)
        if node_id == self.node_id or node_id == 0:
            with self.state_lock:
                if command == 0x01:  # Start (Operational)
                    if self.device_state in [DeviceState.READY_TO_SWITCH_ON, DeviceState.SWITCHED_ON]:
                        self.device_state = DeviceState.OPERATION_ENABLED
                        logger.info("Estado: OPERATION ENABLED")
                elif command == 0x02:  # Stop
                    self.device_state = DeviceState.QUICK_STOP_ACTIVE
                    logger.info("Estado: QUICK STOP ACTIVE")
                elif command == 0x80:  # Pre-operational
                    self.device_state = DeviceState.READY_TO_SWITCH_ON
                    logger.info("Estado: READY TO SWITCH ON")
                elif command == 0x81:  # Reset
                    self._reset_device()
                    logger.info("Dispositivo reseteado")

                self._update_status_word()

    def _handle_sdo_request(self, data):
        """Manejar solicitud SDO"""
        if len(data) < 8:
            return

        command = data[0]
        index = (data[2] << 8) | data[1]
        subindex = data[3]

        self.stats['sdo_requests'] += 1

        if not self.batch_mode:
            logger.debug(f"SDO Request: cmd=0x{command:02X}, index=0x{index:04X}, sub={subindex}")

        # Leer objeto (upload)
        if command == 0x40:
            self._handle_sdo_upload(index, subindex)
        # Escribir objeto (download)
        elif command in [0x2F, 0x2B, 0x27, 0x23]:  # Diferentes tamaños
            value = self._extract_sdo_value(data, command)
            self._handle_sdo_download(index, subindex, value)

    def _handle_sdo_upload(self, index, subindex):
        """Manejar SDO upload (lectura)"""
        try:
            if index in self.object_dictionary:
                obj = self.object_dictionary[index]
                value = obj['value']

                # Preparar respuesta SDO
                response_data = [0x43, index & 0xFF, (index >> 8) & 0xFF, subindex]

                # Agregar valor según tipo
                if obj['type'] == 'UINT16':
                    response_data.extend([value & 0xFF, (value >> 8) & 0xFF, 0x00, 0x00])
                elif obj['type'] == 'INT8':
                    response_data.extend([value & 0xFF, 0x00, 0x00, 0x00])
                elif obj['type'] == 'UINT32':
                    response_data.extend([
                        value & 0xFF, (value >> 8) & 0xFF,
                        (value >> 16) & 0xFF, (value >> 24) & 0xFF
                    ])
                elif obj['type'] == 'INT32':
                    # Para valores negativos
                    if value < 0:
                        value = (1 << 32) + value
                    response_data.extend([
                        value & 0xFF, (value >> 8) & 0xFF,
                        (value >> 16) & 0xFF, (value >> 24) & 0xFF
                    ])

                msg = can.Message(
                    arbitration_id=0x580 + self.node_id,
                    data=response_data,
                    is_extended_id=False
                )

                self.bus.send(msg)
                self._log_message(msg, is_rx=False)  # TX

                if not self.batch_mode:
                    logger.debug(f"SDO Upload: index=0x{index:04X}, value={value}")

            else:
                # Objeto no encontrado
                response_data = [0x80, index & 0xFF, (index >> 8) & 0xFF, subindex, 0x00, 0x00, 0x00, 0x00]
                msg = can.Message(
                    arbitration_id=0x580 + self.node_id,
                    data=response_data,
                    is_extended_id=False
                )
                self.bus.send(msg)
                self._log_message(msg, is_rx=False)  # TX

        except Exception as e:
            logger.error(f"Error en SDO upload: {e}")

    def _handle_sdo_download(self, index, subindex, value):
        """Manejar SDO download (escritura)"""
        try:
            if index in self.object_dictionary:
                obj = self.object_dictionary[index]
                if obj['access'] in ['RW', 'WO']:
                    obj['value'] = value

                    # Actualizar estado según cambios
                    if index == 0x6040:  # Control Word
                        self._process_control_word(value)
                    elif index == 0x6060:  # Modes of Operation
                        self.operation_mode = OperationMode(value)
                    elif index == 0x607A:  # Target Position
                        self.target_position = value
                    elif index == 0x6081:  # Profile Velocity
                        self.target_velocity = value

                    self._update_status_word()

                    # Enviar confirmación
                    response_data = [0x60, index & 0xFF, (index >> 8) & 0xFF, subindex, 0x00, 0x00, 0x00, 0x00]
                    msg = can.Message(
                        arbitration_id=0x580 + self.node_id,
                        data=response_data,
                        is_extended_id=False
                    )
                    self.bus.send(msg)
                    self._log_message(msg, is_rx=False)  # TX

                    if not self.batch_mode:
                        logger.debug(f"SDO Download: index=0x{index:04X}, value={value}")

                else:
                    # Acceso denegado
                    response_data = [0x80, index & 0xFF, (index >> 8) & 0xFF, subindex, 0x01, 0x00, 0x00, 0x00]
                    msg = can.Message(
                        arbitration_id=0x580 + self.node_id,
                        data=response_data,
                        is_extended_id=False
                    )
                    self.bus.send(msg)
                    self._log_message(msg, is_rx=False)  # TX

        except Exception as e:
            logger.error(f"Error en SDO download: {e}")

    def _handle_rpdo1(self, data):
        """Manejar RPDO1 - Comandos de control"""
        try:
            if len(data) >= 2:
                # Control Word (primeros 2 bytes)
                control_word = data[0] | (data[1] << 8)
                logger.warning(f"[RPDO1] COB-ID=0x{self.pdo_data['rpdo1']['cob_id']:03X}, Control=0x{control_word:04X}, Estado actual={self.device_state.name}, Raw={data.hex()}")

                # Procesar Control Word siempre
                self._process_control_word(control_word)

                # Target Velocity (bytes 2-5, si están presentes)
                if len(data) >= 6:
                    velocity = data[2] | (data[3] << 8) | (data[4] << 16) | (data[5] << 24)
                    if velocity & 0x80000000:  # Sign extension
                        velocity -= 1 << 32
                    self.target_velocity = velocity

                if not self.batch_mode:
                    logger.debug(f"RPDO1 recibido: Control=0x{control_word:04X}, TargetVel={self.target_velocity}")

        except Exception as e:
            logger.error(f"Error procesando RPDO1: {e}")

    def _handle_emergency_stop(self, data):
        """Manejar parada de emergencia"""
        self.stats['emergency_stops'] += 1
        self.device_state = DeviceState.QUICK_STOP_ACTIVE
        self.target_velocity = 0
        self._update_status_word()

        logger.warning("⚠️  PARADA DE EMERGENCIA ACTIVADA")

        # Enviar confirmación por PDO
        self._send_tpdo1()

    def _process_control_word(self, control_word):
        """Procesar Control Word según CiA 402"""
        with self.state_lock:
            # Capturar estado previo para log
            prev_state = self.device_state.name

            # Bit 0: Switch On
            # Bit 1: Enable Voltage
            # Bit 2: Quick Stop
            # Bit 3: Enable Operation
            # Bit 7: Reset Fault

            switch_on = bool(control_word & (1 << 0))
            enable_voltage = bool(control_word & (1 << 1))
            quick_stop = bool(control_word & (1 << 2))
            enable_operation = bool(control_word & (1 << 3))
            reset_fault = bool(control_word & (1 << 7))

            # Forzar transición a READY_TO_SWITCH_ON si recibimos 0x0007 en SWITCH_ON_DISABLED o QUICK_STOP_ACTIVE
            # Control Word 0x0007 = bits 0,1,2 = 1 (Switch On, Enable Voltage, Quick Stop)
            if control_word == 0x0007 and self.device_state in [DeviceState.SWITCH_ON_DISABLED, DeviceState.QUICK_STOP_ACTIVE]:
                logger.warning(f"[DEBUG] Forzando transición: {prev_state} → READY_TO_SWITCH_ON por Control=0x0007")
                self.device_state = DeviceState.READY_TO_SWITCH_ON
                self._update_status_word()
                logger.info(f"Transición forzada: {prev_state} → READY_TO_SWITCH_ON por 0x0007")
                return

            # Reset fault tiene máxima prioridad
            if reset_fault and self.device_state == DeviceState.FAULT:
                self.device_state = DeviceState.SWITCH_ON_DISABLED
                self._update_status_word()
                return

            # Quick Stop: Control Word 0x0002 (solo Enable Voltage, Quick Stop activo)
            # Cuando bit 2 (Quick Stop) está en 0, activar QUICK_STOP_ACTIVE
            if not quick_stop:
                if self.device_state in [DeviceState.OPERATION_ENABLED, DeviceState.SWITCHED_ON]:
                    self.device_state = DeviceState.QUICK_STOP_ACTIVE
                    self.target_velocity = 0
                    self._update_status_word()
                    return

            # Control Word 0x0002 específico (Emergency Stop común)
            if control_word == 0x0002:
                self.device_state = DeviceState.QUICK_STOP_ACTIVE
                self.target_velocity = 0
                self._update_status_word()
                return

            # Aplicar transiciones en secuencia natural (hasta 3 transiciones)
            max_transitions = 3
            transitions = 0

            while transitions < max_transitions:
                old_state = self.device_state
                changed = False

                if self.device_state == DeviceState.SWITCH_ON_DISABLED:
                    # Transición 2: Shutdown (0x0006 o 0x0007)
                    # CiA 402: Requiere Enable Voltage=1 y Quick Stop=1
                    # Switch On puede estar en 0 (0x0006) o en 1 (0x0007)
                    if enable_voltage and quick_stop:
                        self.device_state = DeviceState.READY_TO_SWITCH_ON
                        changed = True

                elif self.device_state == DeviceState.READY_TO_SWITCH_ON:
                    # Transición 3: Switch On (0x0007)
                    # Requiere mantener voltaje y switch on
                    if switch_on and enable_voltage and quick_stop:
                        self.device_state = DeviceState.SWITCHED_ON
                        changed = True
                    # Transición hacia atrás: Disable Voltage
                    elif not enable_voltage:
                        self.device_state = DeviceState.SWITCH_ON_DISABLED
                        changed = True

                elif self.device_state == DeviceState.SWITCHED_ON:
                    # Transición 4: Enable Operation (0x000F)
                    if enable_operation and switch_on and enable_voltage and quick_stop:
                        self.device_state = DeviceState.OPERATION_ENABLED
                        changed = True
                    # Transición hacia atrás
                    elif not switch_on or not enable_voltage:
                        self.device_state = DeviceState.READY_TO_SWITCH_ON
                        changed = True

                elif self.device_state == DeviceState.OPERATION_ENABLED:
                    # Ya fue manejado arriba (quick stop cuando no switch_on)
                    # Aquí solo retrocesos normales
                    if not enable_operation and enable_voltage:
                        self.device_state = DeviceState.SWITCHED_ON
                        changed = True
                    elif not enable_voltage:
                        self.device_state = DeviceState.READY_TO_SWITCH_ON
                        changed = True

                elif self.device_state == DeviceState.QUICK_STOP_ACTIVE:
                    # Salir de Quick Stop con 0x0007 (Shutdown)
                    if switch_on and enable_voltage and quick_stop:
                        self.device_state = DeviceState.READY_TO_SWITCH_ON
                        changed = True
                    # Salir de Quick Stop con reset fault
                    elif reset_fault:
                        self.device_state = DeviceState.SWITCH_ON_DISABLED
                        changed = True

                if not changed:
                    break

                transitions += 1

            self._update_status_word()

    def _update_status_word(self):
        """Actualizar Status Word según estado del dispositivo"""
        status_word = 0

        if self.device_state == DeviceState.SWITCH_ON_DISABLED:
            status_word |= (1 << 6)  # Switch On Disabled
        elif self.device_state == DeviceState.READY_TO_SWITCH_ON:
            status_word |= (1 << 0)  # Ready to Switch On
        elif self.device_state == DeviceState.SWITCHED_ON:
            status_word |= (1 << 0) | (1 << 1)  # Ready + Switched On
        elif self.device_state == DeviceState.OPERATION_ENABLED:
            status_word |= (1 << 0) | (1 << 1) | (1 << 2)  # Ready + Switched On + Operation Enabled
        elif self.device_state == DeviceState.QUICK_STOP_ACTIVE:
            status_word |= (1 << 0) | (1 << 1) | (1 << 5)  # Ready + Switched On + Quick Stop
        elif self.device_state == DeviceState.FAULT:
            status_word |= (1 << 3)  # Fault

        # Voltage Enabled (simulado como siempre true en operación)
        if self.device_state in [DeviceState.SWITCHED_ON, DeviceState.OPERATION_ENABLED, DeviceState.QUICK_STOP_ACTIVE]:
            status_word |= (1 << 4)

        self.object_dictionary[0x6041]['value'] = status_word

    def _get_state_byte(self):
        """Obtener byte de estado para heartbeat"""
        state_map = {
            DeviceState.NOT_READY_TO_SWITCH_ON: 0x00,
            DeviceState.SWITCH_ON_DISABLED: 0x40,
            DeviceState.READY_TO_SWITCH_ON: 0x21,
            DeviceState.SWITCHED_ON: 0x23,
            DeviceState.OPERATION_ENABLED: 0x27,
            DeviceState.QUICK_STOP_ACTIVE: 0x07,
            DeviceState.FAULT_REACTION_ACTIVE: 0x0F,
            DeviceState.FAULT: 0x08
        }
        return state_map.get(self.device_state, 0x00)

    def _simulation_task(self):
        """Simular movimiento y física del dispositivo"""
        while self.running.is_set():
            try:
                with self.state_lock:
                    if self.device_state == DeviceState.OPERATION_ENABLED:
                        # Simular aceleración/decercación
                        acceleration = 100  # unidades/s²

                        if self.actual_velocity < self.target_velocity:
                            self.actual_velocity = min(self.target_velocity, self.actual_velocity + acceleration * 0.1)
                        elif self.actual_velocity > self.target_velocity:
                            self.actual_velocity = max(self.target_velocity, self.actual_velocity - acceleration * 0.1)

                        # Actualizar posición
                        self.actual_position += self.actual_velocity * 0.1

                    elif self.device_state in [DeviceState.QUICK_STOP_ACTIVE, DeviceState.SWITCH_ON_DISABLED]:
                        # Detener gradualmente
                        if abs(self.actual_velocity) > 10:
                            self.actual_velocity *= 0.9
                        else:
                            self.actual_velocity = 0

                    # Simular fault aleatorio (baja probabilidad)
                    if random.random() < 0.0001 and self.device_state != DeviceState.FAULT:
                        self.device_state = DeviceState.FAULT
                        self._update_status_word()
                        logger.warning("🔴 FAULT SIMULADO - Dispositivo en estado de error")

            except Exception as e:
                logger.error(f"Error en simulación: {e}")

            time.sleep(0.1)  # 100ms

    def _extract_sdo_value(self, data, command):
        """Extraer valor de datos SDO según comando"""
        if command == 0x2F:  # 1 byte
            return data[4]
        elif command == 0x2B:  # 2 bytes
            return data[4] | (data[5] << 8)
        elif command == 0x27:  # 4 bytes
            return data[4] | (data[5] << 8) | (data[6] << 16) | (data[7] << 24)
        else:
            return 0

    def _reset_device(self):
        """Reset completo del dispositivo"""
        with self.state_lock:
            self.device_state = DeviceState.SWITCH_ON_DISABLED
            self.operation_mode = OperationMode.PROFILE_VELOCITY
            self.operation_mode_display = OperationMode.PROFILE_VELOCITY
            self.target_velocity = 0
            self.actual_velocity = 0
            self.target_position = 0
            self.actual_position = 0

            # Reset Object Dictionary a valores por defecto
            self.object_dictionary[0x6040]['value'] = 0x0000
            self.object_dictionary[0x6060]['value'] = OperationMode.PROFILE_VELOCITY.value
            self.object_dictionary[0x6061]['value'] = OperationMode.PROFILE_VELOCITY.value
            self.object_dictionary[0x607A]['value'] = 0
            self.object_dictionary[0x6081]['value'] = 1000
            self.object_dictionary[0x606C]['value'] = 0
            self.object_dictionary[0x6064]['value'] = 0

            self._update_status_word()

    def get_state(self):
        """Obtener estado completo del simulador"""
        return {
            'device_state': self.device_state.name,
            'operation_mode': self.operation_mode.name,
            'target_velocity': self.target_velocity,
            'actual_velocity': int(self.actual_velocity),
            'target_position': self.target_position,
            'actual_position': int(self.actual_position),
            'status_word': f"0x{self.object_dictionary[0x6041]['value']:04X}",
            'control_word': f"0x{self.object_dictionary[0x6040]['value']:04X}",
            'stats': self.stats.copy()
        }

    def simulate_fault(self):
        """Simular un fault para testing"""
        with self.state_lock:
            self.device_state = DeviceState.FAULT
            self._update_status_word()
            logger.warning("🔴 FAULT SIMULADO MANUALMENTE")

    def clear_fault(self):
        """Limpiar fault simulado"""
        with self.state_lock:
            if self.device_state == DeviceState.FAULT:
                self.device_state = DeviceState.SWITCH_ON_DISABLED
                self._update_status_word()
                logger.info("🟢 FAULT LIMPIADO")


def main():
    """Función principal para ejecutar el simulador"""
    import argparse

    parser = argparse.ArgumentParser(description='Simulador CANopen R13 F')
    parser.add_argument('--channel', default='vcan0', help='Canal CAN virtual')
    parser.add_argument('--node-id', type=int, default=1, help='ID del nodo')
    parser.add_argument('--batch', action='store_true', help='Modo batch para testing')
    parser.add_argument('--verbose', action='store_true', help='Modo verbose')

    args = parser.parse_args()

    if args.verbose or args.batch:
        logging.getLogger().setLevel(logging.DEBUG)

    # Crear y ejecutar simulador
    simulator = R13FSimulator(
        channel=args.channel,
        node_id=args.node_id,
        batch_mode=args.batch
    )

    if not args.batch:
        print("=" * 70)
        print("🚀 Simulador CANopen Danfoss R13 F (CiA 402)")
        print("=" * 70)
        print(f"Canal: {args.channel}")
        print(f"Node ID: {args.node_id}")
        print(f"Bitrate: 250 kbps")
        print(f"Modo: {'Batch' if args.batch else 'Interactivo'}")
        print("\nPara crear el canal virtual ejecuta:")
        print("  sudo modprobe vcan")
        print("  sudo ip link add dev vcan0 type vcan")
        print("  sudo ip link set up vcan0")
        print("\nPresiona Ctrl+C para detener")
        print("=" * 70)

    simulator.start()

    try:
        if args.batch:
            # Modo batch: esperar señales o timeout
            time.sleep(300)  # 5 minutos máximo
        else:
            # Modo interactivo: mostrar estado cada 5 segundos
            while True:
                time.sleep(5)
                state = simulator.get_state()
                print(f"\n📊 Estado: {state['device_state']} | "
                      f"Vel: {state['actual_velocity']} RPM | "
                      f"Status: {state['status_word']} | "
                      f"Heartbeats: {state['stats']['heartbeats_sent']}")

    except KeyboardInterrupt:
        if not args.batch:
            print("\n\n⏹️  Deteniendo simulador...")
        simulator.stop()
        if not args.batch:
            print("✅ Simulador detenido")


if __name__ == "__main__":
    main()
