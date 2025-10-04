# Hardware K13 - Especificaciones y Esquemas

## Información del Hardware

### Dispositivo Principal
- **Fabricante**: Danfoss Power Solutions
- **Modelo**: R13 F Receiver
- **Aplicación**: Control de puente grúa
- **Comunicación Primaria**: CAN bus (Protocolo CANopen)
- **Comunicación Secundaria**: RS232 / RS485

### Conexiones Eléctricas (según Datasheet)

#### Conector CAN
- **Función**: Interfaz de control principal.
- **Protocolo**: CANopen (estándar), Profibus DP, Profinet (opcional).

#### Conector RS232/RS485
- **Función**: Diagnóstico, configuración o control secundario.

### Arquitectura de Red Propuesta

Para integrar el receptor Danfoss R13 en la red Ethernet, se requiere un **Gateway Ethernet a CAN bus**.

```
Computador        Switch        Antena/Receptor      Switch PoE      Gateway ETH-CAN      Danfoss R13
┌───────────┐    ┌─────────┐    ┌───────────────┐    ┌────────────┐    ┌────────────────┐    ┌───────────┐
│ Controlador│◄─►│  Red    │◄─►│   Enlace WiFi   │◄─►│  En Grúa   │◄─►│ Raspberry Pi + │◄─►│ Receptor  │
│  Python   │    │ Admin.  │    │               │    │            │    │    CAN HAT     │    │           │
└───────────┘    └─────────┘    └───────────────┘    └────────────┘    └────────────────┘    └───────────┘
```

### Opciones de Gateway Ethernet a CAN bus

#### 1. Raspberry Pi + Módulo CAN (Opción Recomendada)
- **Componentes**: Raspberry Pi (4, 5, o similar) + Módulo CAN (HAT o USB).
- **Ventajas**: Máxima flexibilidad con Python, coste-efectivo, potente.
- **Implementación**: El software controlador se ejecuta en la Pi, comunicándose con el R13 vía `SocketCAN` y exponiendo una API de red para el computador de procesamiento.

#### 2. Gateways Industriales
- **Ejemplos**: HMS Anybus Communicator, Peak-System PCAN-Gateway.
- **Ventajas**: Solución robusta y certificada para entornos industriales.
- **Implementación**: El controlador Python se comunica por red (ej. Modbus TCP, EtherNet/IP) con el gateway, que se encarga de la traducción a CANopen.

#### 3. Microcontrolador (ESP32)
- **Componentes**: ESP32 + Transceptor CAN + Módulo Ethernet (opcional).
- **Ventajas**: Muy bajo coste, ideal para producto final embebido.
- **Implementación**: Requiere programación a bajo nivel (C++/MicroPython) en el ESP32.

## Modificaciones de Hardware

### Adaptadores Necesarios
- **Gateway Ethernet-a-CAN**: El componente clave a seleccionar (ver opciones arriba).
- **PoE HAT o Splitter**: Para alimentar el Gateway (ej. Raspberry Pi) desde el Switch PoE.
- **Cableado CAN bus**: Cable de par trenzado adecuado para CAN.
- **Resistencia de Terminación CAN**: Una resistencia de 120 Ohm al final del bus. El datasheet del R13 menciona un "CAN BUS termination Jumper" (ítem 13), lo que simplifica esto.

### Precauciones de Seguridad
- **Aislamiento galvánico**: Es crucial entre el gateway y el bus CAN para proteger los equipos. Muchos módulos CAN de calidad ya lo incluyen.
- **Parada de emergencia**: Debe seguir siendo manejada por el hardware del R13 para garantizar la seguridad funcional (Cat. 3-PLd / Cat 4 - PLe).

## Lista de Componentes

### Hardware Base
- [ ] Receptor Danfoss R13 F
- [ ] Gateway Ethernet-a-CAN (ej. Raspberry Pi 4)
- [ ] Módulo de interfaz CAN para el gateway (ej. Waveshare RS485 CAN HAT)
- [ ] Switch PoE
- [ ] Antena direccional y receptor WiFi
- [ ] Fuente de alimentación para los componentes que no son PoE.

### Herramientas de Análisis
- [ ] Multímetro
- [ ] Osciloscopio (para depurar el bus CAN si es necesario)
- [ ] Analizador de bus CAN (ej. PCAN-USB) para monitorear el tráfico.

---

**Fecha de última actualización**: 8 de septiembre de 2025
**Estado**: Arquitectura de red definida. Pendiente seleccionar el hardware específico del gateway.
