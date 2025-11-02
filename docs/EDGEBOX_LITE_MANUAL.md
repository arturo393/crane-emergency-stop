# EdgeBox-Lite User Manual v1.0

**A lightweight IoT controller for industrial applications**

**Manufacturer:** OpenEmbed  
**Website:** www.OpenEmbed.com  
**Document Version:** 1.0  
**Release Date:** 01-08-2022

---

## Revision History

| Revision | Date | Changes |
|----------|------|---------|
| 1.0 | 01-08-2022 | Initial release |

---

## Explanation of Symbols Used

The following symbols are used in these instructions:

**NOTE**  
Indicates tips, recommendations and useful information on specific actions and facts.

**NOTICE**  
Indicates a situation which may lead to property damage if not avoided.

**CAUTION**  
Indicates a dangerous situation or risk.

---

## Table of Contents

1. [Introduction](#1-introduction)
   - 1.1 [Features](#11-features)
   - 1.2 [Interfaces](#12-interfaces)
   - 1.3 [Block Diagram](#13-block-diagram)
2. [Installation and Wiring](#2-installation-and-wiring)
   - 2.1 [Mounting](#21-mounting)
   - 2.2 [Connectors and Interfaces](#22-connectors-and-interfaces)
   - 2.3 [GPIO Multiplex](#23-gpio-multiplex)
   - 2.4 [I2C Devices](#24-i2c-devices)
3. [Mainboard](#3-mainboard)
   - 3.1 [4G/LTE](#31-4glte)
   - 3.2 [Debug Port](#32-debug-port)
   - 3.3 [AI (Analog Input)](#33-ai-analog-input)
   - 3.4 [AO (Analog Output)](#34-ao-analog-output)
4. [Drivers and Programming](#4-drivers-and-programming)
5. [Applications](#5-applications)
6. [Electrical Specifications](#6-electrical-specifications)
   - 6.1 [Power Consumption](#61-power-consumption)

---

## 1. Introduction

EdgeBox-lite enables SCADA equipment via software-selectable 4G/LTE to remote networks or select Industrial Internet of Things (IIoT) Cloud platforms. 

Featuring an event-based engine that can trigger I/O or send SMS text messages based on real-time operational data, EdgeBox-lite controller can perform advanced local edge control and alert personnel of critical events.

A built-in I/O concentrator allows the controller to collect sensor data and optimize cellular data consumption by optionally reporting only on an exception or only transmitting relevant data points.

With built-in **Ethernet**, **serial**, **I/O**, and **GPS**, EdgeBox-lite controller easily integrates with existing equipment enabling remote monitoring and control for M2M applications in industries including:
- Oil and gas
- Water
- Utility
- Transportation
- Mining

### 1.1 Features

- ✅ **Rugged, reduced-maintenance hardware**
- ✅ **High isolation, surge, and short circuit protection**
- ✅ **Open architecture support for custom programming**
- ✅ **Ethernet, I/O, 4G/LTE, CANopen and Modbus bridging**
- ✅ **Natively supports Modbus & CANopen protocols**
- ✅ **Cloud connectivity to IIoT Cloud platforms**
- ✅ **Integrated wired solution for all analog and discrete I/O interface designs**
- ✅ **IEC 61131-3 compliant programs support** (under development)
- ✅ **35mm DIN Rail support**
- ✅ **Wide power supply range: 1.8V to 36V DC**

These features make the EdgeBox-lite designed as a cost-effective controller that provides the functions required for a variety of field automation applications. 

The EdgeBox-lite monitors, measures, and controls equipment in a remote environment. It is ideal for applications requiring:
- **Flow computation**
- **Proportional, Integral, and Derivative (PID) control loops**
- **Logic sequencing control**
- **Gateway with flexible wireless and field sensors expansion**

### 1.2 Interfaces

#### Front Panel

1. **LED** indicators
2. **Ethernet** port
3. **CAN bus and RS485** connector
4. **Multi-Function Phoenix connector**

#### Top Panel

1. **Ant.1** (WiFi antenna connector)
2. **SIM CARD** slot
3. **Reset** button
4. **USB PORT** (5V power output only - NO USB data function)
5. **Ant.2** (4G/LTE antenna connector)

> **NOTE:**
> 1. The Ant.1 is used for WiFi signal, and Ant.2 is used for 4G/LTE by default.
> 2. The USB port is ONLY used for 5V power output, it has NO USB communication function.

### 1.3 Block Diagram

The whole controller is built around **ESP32 SoC**. An OpenEmbed-specific base board implements the specific features.

**Core Components:**
- **ESP32-S3** microcontroller
- **W5500** Ethernet controller (SPI connection)
- **4G/LTE** modem (Mini-PCIe)
- **CAN transceiver**
- **RS485 transceiver**
- **Digital I/O** (6 outputs, 4 inputs)
- **Analog I/O** (4 inputs, 2 outputs)
- **I2C devices** (RTC, EEPROM, Crypto, ADC)

---

## 2. Installation and Wiring

### 2.1 Mounting

**DIN-rail mount is recommended.**

The EdgeBox-Lite is designed for standard 35mm DIN rail mounting in industrial control cabinets.

**Mounting Steps:**
1. Hook the top edge of the device onto the DIN rail
2. Press down the bottom until it clicks into place
3. Ensure secure mounting before wiring

**Removal:**
1. Pull down the release tab at the bottom
2. Tilt the device away from the rail

### 2.2 Connectors and Interfaces

#### 2.2.1 Multi-Function Phoenix Connector

**24-Pin Phoenix Connector Pinout:**

| PIN # | Function | Type | PIN # | Function | Type |
|-------|----------|------|-------|----------|------|
| 1 | S/S | Sensor Supply | 2 | DO_24V | Digital Output Supply |
| 3 | DI0 | Digital Input 0 | 4 | DO_0V | Digital Output GND |
| 5 | DI1 | Digital Input 1 | 6 | DO0 | Digital Output 0 |
| 7 | DI2 | Digital Input 2 | 8 | DO1 | Digital Output 1 |
| 9 | DI3 | Digital Input 3 | 10 | DO2 | Digital Output 2 |
| 11 | AGND | Analog Ground | 12 | DO3 | Digital Output 3 |
| 13 | AI0 | Analog Input 0 | 14 | DO4 | Digital Output 4 |
| 15 | AI1 | Analog Input 1 | 16 | DO5 | Digital Output 5 |
| 17 | AI2 | Analog Input 2 | 18 | AO0 | Analog Output 0 |
| 19 | AI3 | Analog Input 3 | 20 | AO1 | Analog Output 1 |
| 21 | AGND | Analog Ground | 22 | AGND | Analog Ground |
| 23 | GND | Power Ground | 24 | +24V | Power Supply |

**IMPORTANT NOTES:**

1. **Wire gauge:** 24 AWG to 16 AWG cables are suggested
2. **Isolation:** GND and AGND are isolated
3. **AGND connection:** All AGND signals are connected internally
4. **Input voltage:** DC voltage for digital inputs is **24V (±10%)**
5. **Output voltage:** DC voltage for digital outputs should be **24V (±10%)**, current capacity is **1A**

#### 2.2.2 Serial Port (CAN BUS and RS485)

**8-Pin Serial Connector:**

| Pin # | Signal | Description |
|-------|--------|-------------|
| 1 | N.C | Not used |
| 2 | N.C | Not used |
| 3 | N.C | Not used |
| 4 | **CAN_H** | CAN bus high |
| 5 | **CAN_L** | CAN bus low |
| 6 | N.C | Not used |
| 7 | **RS485_A** | RS485 A (positive) |
| 8 | **RS485_B** | RS485 B (negative) |

**LED Indicators:**

| LED Color | Label | Function |
|-----------|-------|----------|
| Green | LED_CAN | Active when CAN TX/RX |
| Yellow | LED_RS485 | Active when RS485 TX/RX |

**IMPORTANT NOTES:**

1. ✅ The **120Ω termination resistor for RS485** has been installed inside
2. ✅ The **120Ω termination resistor for CAN BUS** has been installed inside

#### 2.2.3 Ethernet

**Ethernet Interface Specifications:**

- **Controller:** W5500 (connected to ESP32 via SPI)
- **Speed:** 10/100-BaseT supported
- **Connector:** Shielded RJ45 modular jack
- **Cable:** Twisted pair cable or shielded twisted pair cable

**RJ45 Pinout:**

| Pin # | Signal | Description |
|-------|--------|-------------|
| 1 | TXP | Transmit positive |
| 2 | TXN | Transmit negative |
| 3 | RXP | Receive positive |
| 4 | N.C | Not used |
| 5 | N.C | Not used |
| 6 | RXN | Receive negative |
| 7 | N.C | Not used |
| 8 | N.C | Not used |

**LED Indicators:**

| LED Color | Label | Function |
|-----------|-------|----------|
| Green | LINK | Active when Ethernet link is up |
| Yellow | ACTIVE | Active when TX/RX data comes through |

> **KEY FINDING:** The Ethernet interface uses the **W5500 chip** connected to ESP32 via SPI - this is the same chip we identified for the ESP32 Gateway project!

#### 2.2.4 LED Indicators

**Main Board LEDs:**

| LED | Signal | Description |
|-----|--------|-------------|
| PWR | Power supply | Indicates power is ON |
| Cellular | 4G/LTE | Cellular modem status |
| ACT | Activity | Multiplexed with U0TXD (UART0 TX) |
| ERR | Error | Multiplexed with U0RXD (UART0 RX) |

#### 2.2.5 SMA Connector

**Antenna Connectors:**

- **ANT1:** Default used for Mini-PCIe socket (4G/LTE)
- **ANT2:** Internal WiFi signal from ESP32 module

**Connection Guidelines:**
- Use appropriate antennas for the frequency bands
- Ensure proper antenna placement for optimal signal strength
- Tighten SMA connectors hand-tight (do not over-torque)

#### 2.2.6 SIM Card Slot

- **Location:** Top panel
- **Usage:** Only needed in cellular network mode
- **Type:** Standard SIM card size
- **Installation:** Insert with contacts facing down

#### 2.2.7 Reset Button

The reset button has multiple functions:

1. **Power-up Download Mode:**
   - When powering up, the button can be used to boot in download mode
   - Useful if the OTA (Over-The-Air) mode crashes

2. **User Configuration Reset:**
   - In applications, user software can use the button to reset to default configurations
   - Examples: IP address, WiFi information, or other behavior and actions

### 2.3 GPIO Multiplex

**Complete GPIO Mapping Table:**

| Name | ESP32 IO | Type | Function | Notes |
|------|----------|------|----------|-------|
| **DO0** | IO40 | Digital Output | Digital output 0 | |
| **DO1** | IO39 | Digital Output | Digital output 1 | |
| **DO2** | IO38 | Digital Output | Digital output 2 | |
| **DO3** | IO37 | Digital Output | Digital output 3 | |
| **DO4** | IO36 | Digital Output | Digital output 4 | |
| **DO5** | IO35 | Digital Output | Digital output 5 | |
| **DI0** | IO4 | Digital Input | Digital input 0 | |
| **DI1** | IO5 | Digital Input | Digital input 1 | |
| **DI2** | IO6 | Digital Input | Digital input 2 | |
| **DI3** | IO7 | Digital Input | Digital input 3 | |
| **AO0** | IO42 | Analog Output | Analog output 0 | PWM + LPF |
| **AO1** | IO41 | Analog Output | Analog output 1 | PWM + LPF |
| **RS485** | IO17 | UART1 | U1TXD | |
| | IO18 | UART1 | U1RXD | |
| | IO8 | Control | RS485_RTS | Direction control |
| **4G/LTE WWAN** | IO48 | UART2 | U2TXD | |
| | IO47 | UART2 | U2RXD | |
| | IO21 | Control | PWR_KEY | Power key |
| | IO16 | Control | PWR_EN | Power enable |
| **Ethernet W5500** | IO10 | SPI | FSPI_CS0 | Chip select |
| | IO11 | SPI | FSPI_DI | Data in (MISO) |
| | IO12 | SPI | FSPI_DO | Data out (MOSI) |
| | IO13 | SPI | FSPI_SCLK | Clock |
| | IO14 | Interrupt | INT# | Interrupt |
| | IO15 | Reset | RST# | Reset |
| **CAN Bus** | IO1 | CAN | CAN_TXD | CAN transmit |
| | IO2 | CAN | CAN_RXD | CAN receive |
| **Debug/LED** | IO3 | UART0 | TXD0/LED_ACT# | Debug TX / Activity LED |
| | IO46 | UART0 | RXD0/LED_ERR# | Debug RX / Error LED |
| **Beep** | IO45 | Output | Beep | High active |
| **Reset Button** | IO0 | Input | Reset button | Boot mode selection |
| **I2C Bus** | IO19 | I2C | I2C_SCL | Clock |
| | IO20 | I2C | I2C_SDA | Data |
| | IO9 | Interrupt | Alarm/Wake | From PCF8563 RTC |

### 2.4 I2C Devices

**I2C Bus Devices:**

| Device | I2C Address | Function | Description |
|--------|-------------|----------|-------------|
| **FM24CL64B** | 0x50 | Retain memory | Non-volatile FRAM 64Kbit |
| **PCF8563** | 0x51 | RTC | Real-Time Clock |
| **ATECC608A** | 0x68 | Crypto device | Hardware cryptographic authentication |
| **ADS1115** or **SGM58031** | 0x48 | ADC | 16-bit Analog-to-Digital Converter |

---

## 3. Mainboard

### Top Side Components

- ESP32-S3 SoC
- W5500 Ethernet controller
- Mini-PCIe socket for 4G/LTE modem
- Phoenix connectors
- Power supply circuitry
- Digital I/O drivers
- Analog I/O conditioning

### Bottom Side Components

- Additional power regulation
- CAN transceiver
- RS485 transceiver
- I2C devices (RTC, EEPROM, Crypto, ADC)
- Supporting passive components

### 3.1 4G/LTE

**Cellular Connectivity:**

- **Interface:** Mini-PCIe socket
- **Communication:** UART2 (IO48/IO47)
- **Control Signals:**
  - PWR_KEY (IO21): Power key control
  - PWR_EN (IO16): Power enable
- **SIM Card:** Standard SIM slot on top panel
- **Antennas:** ANT1 (SMA connector)

**Supported Bands:** (Depends on installed modem module)

### 3.2 Debug Port

**UART0 Debug Interface:**

- **TXD0:** IO3 (also multiplexed with LED_ACT#)
- **RXD0:** IO46 (also multiplexed with LED_ERR#)
- **GPIO0:** Connected to Reset Button

**Usage:**
- Allows users to develop EdgeBox-lite in **bare metal** mode
- Download mode access via Reset Button + UART0
- Serial debugging and monitoring

**Download Mode Entry:**
1. Hold Reset button
2. Apply power
3. Release Reset button
4. Device enters download mode

### 3.3 AI (Analog Input)

**Analog Input Specifications:**

- **ADC Chip:** ADS1115 or compatible (SGM58031)
- **Resolution:** 16-bit
- **Channels:** 4 (AI0, AI1, AI2, AI3)
- **Default Input Type:** **4-20mA** current loop
- **Optional Input Type:** **0-10V** voltage input
- **I2C Address:** 0x48
- **Common Ground:** AGND (isolated from digital GND)

**Input Configuration:**

| Channel | Pin # | Range (4-20mA) | Range (0-10V) |
|---------|-------|----------------|---------------|
| AI0 | 13 | 4-20 mA | 0-10 V |
| AI1 | 15 | 4-20 mA | 0-10 V |
| AI2 | 17 | 4-20 mA | 0-10 V |
| AI3 | 19 | 4-20 mA | 0-10 V |

**NOTES:**
1. The default input type is **4-20mA**
2. **0-10V** input type is optional (hardware configuration)
3. All analog inputs share common AGND

### 3.4 AO (Analog Output)

**Analog Output Specifications:**

- **Technology:** PWM + Low-Pass Filter (LPF)
- **Channels:** 2 (AO0, AO1)
- **ESP32 Pins:** IO42 (AO0), IO41 (AO1)
- **Output Type:** Configurable (voltage or current)

**Output Configuration:**

| Channel | Pin # | ESP32 IO | Technology |
|---------|-------|----------|------------|
| AO0 | 18 | IO42 | PWM + LPF |
| AO1 | 20 | IO41 | PWM + LPF |

**PWM to Analog Conversion:**
- High-frequency PWM signal
- Low-pass filter for smooth analog output
- Software-configurable output range

---

## 4. Drivers and Programming

**Development Frameworks:**

- **ESP-IDF** (ESP32 official framework)
- **Arduino** (community support)
- **MicroPython** (interpreted Python)
- **IEC 61131-3** (under development)

**Communication Protocols:**

- **Modbus RTU/TCP** (natively supported)
- **CANopen** (natively supported)
- **MQTT** (IoT cloud connectivity)
- **HTTP/HTTPS** (web APIs)

**Programming Interfaces:**

- UART0 (debug/download)
- OTA (Over-The-Air updates)
- Web-based configuration

---

## 5. Applications

**Typical Use Cases:**

1. **Industrial Automation**
   - PLC replacement
   - Remote I/O expansion
   - Process control

2. **SCADA Systems**
   - Data acquisition
   - Remote monitoring
   - Alarm notification (SMS)

3. **Oil & Gas**
   - Pipeline monitoring
   - Pump control
   - Flow computation

4. **Water/Wastewater**
   - Level monitoring
   - Pump stations
   - Treatment plants

5. **Transportation**
   - Fleet management
   - GPS tracking
   - Vehicle diagnostics

6. **Mining**
   - Equipment monitoring
   - Environmental sensing
   - Safety systems

---

## 6. Electrical Specifications

### 6.1 Power Consumption

The power consumption of the EdgeBox-Lite strongly depends on:
- Application type
- Mode of operation
- Connected peripheral devices

**Approximate Values (24V power supply):**

| Mode of Operation | Current (mA) | Power (W) | Remark |
|-------------------|--------------|-----------|--------|
| Idle | ~80 | ~1.9 | No communication |
| WiFi Active | ~120 | ~2.9 | WiFi connected |
| 4G/LTE Active | ~150-300 | ~3.6-7.2 | Depends on signal strength |
| Full Load | ~350 | ~8.4 | All I/O + communication active |

**Power Supply Requirements:**

- **Input Voltage Range:** 1.8V to 36V DC
- **Recommended:** 24V DC (±10%)
- **Protection:** Reverse polarity, over-voltage, over-current

**Digital Output Specifications:**

- **Supply Voltage:** 24V DC (±10%)
- **Current Capacity:** 1A per channel
- **Total Output Current:** Check datasheet for total limit

---

## Hardware Compatibility Notes

### W5500 Ethernet Controller

✅ **CONFIRMED:** This EdgeBox-Lite uses the **same W5500 Ethernet controller** that we're planning to use in our ESP32 Gateway project.

**Key Advantages:**
- Proven industrial design
- SPI interface to ESP32
- Integrated TCP/IP stack
- 10/100 Mbps support
- Hardware-compatible with our gateway

### ESP32-S3 SoC

✅ **CONFIRMED:** Built around ESP32-S3, the same family as our target hardware.

**Shared Features:**
- WiFi + Bluetooth
- FreeRTOS support
- Multiple UART, SPI, I2C
- CAN bus support (via IO pins)
- Wide GPIO availability

---

## Reference Implementation Value

This EdgeBox-Lite serves as an **excellent reference design** for our K13 Puente Grúa project:

1. ✅ **W5500 Ethernet integration** (same chip we need)
2. ✅ **ESP32-S3 platform** (same SoC family)
3. ✅ **CAN bus implementation** (industrial-grade)
4. ✅ **Industrial I/O conditioning** (24V, isolation, protection)
5. ✅ **DIN-rail mounting** (industrial standard)
6. ✅ **Proven reliability** (commercial product)

**Lessons for Our Gateway:**
- SPI pinout for W5500 (IO10-15)
- CAN bus pins (IO1-2)
- Debug UART configuration
- Power supply design
- I/O protection circuits

---

## Document Information

**Compiled from:** Manual_Edgebox-Lite.pdf  
**Total Pages:** 22  
**Converted to Markdown:** November 1, 2025  
**Project:** K13 Puente Grúa - ESP32 Gateway  
**Reference:** Hardware design validation

---

## Additional Resources

- **Manufacturer:** OpenEmbed
- **Website:** www.OpenEmbed.com
- **Support:** Contact manufacturer for detailed schematics
- **Updates:** Check manufacturer website for firmware updates

---

**END OF DOCUMENT**
