# Device Integration Tests

## Overview

This directory contains **Device Integration Tests** for the EdgeBox-Lite ESP32 Gateway. These tests are designed to run **directly on the ESP32 hardware** to validate that the physical connections and hardware configuration are correct.

Unlike native tests (which run on your development machine), these tests must be compiled for ESP32 and flashed to the actual device.

## Test Suites

### 1. CAN Bus Initialization (`test_can_bus_init.cpp`)

**Purpose:** Validate CAN bus configuration on EdgeBox-Lite hardware.

**Tests:**
- `test_can_bus_initialization`: Verifies TWAI driver can initialize on GPIO1 (TX) and GPIO2 (RX)
- `test_can_bus_loopback`: Tests CAN transmission in NO_ACK mode (no physical bus needed)

**Hardware Requirements:**
- None (loopback mode doesn't require physical CAN transceiver)
- For full testing: MCP2551 or similar CAN transceiver connected to GPIO1/GPIO2

**Expected Output:**
```
✅ TWAI driver installed successfully
✅ TWAI driver started successfully
✅ CAN bus initialization test PASSED
```

---

### 2. W5500 Ethernet SPI (`test_w5500_spi_init.cpp`)

**Purpose:** Validate W5500 Ethernet controller communication via SPI.

**Tests:**
- `test_w5500_spi_bus_init`: Initialize SPI2 bus with correct pins
- `test_w5500_hardware_reset`: Test hardware reset sequence
- `test_w5500_version_register`: Read W5500 version (should be 0x04)

**Hardware Requirements:**
- **REQUIRED:** W5500 Ethernet module connected via SPI
- Pin connections according to `hardware_config.h`:
  - MOSI: GPIO12
  - MISO: GPIO11
  - SCLK: GPIO13
  - CS: GPIO10
  - INT: GPIO14
  - RST: GPIO15

**Expected Output:**
```
✅ SPI bus initialized successfully
✅ W5500 reset complete
W5500 Version Register: 0x04
✅ W5500 is responding correctly!
```

**Troubleshooting:**
- If version != 0x04: Check SPI wiring and power supply to W5500
- If SPI init fails: Verify pin connections match `hardware_config.h`

---

### 3. Digital I/O (`test_digital_io.cpp`)

**Purpose:** Validate digital inputs and outputs configuration.

**Tests:**
- `test_digital_output_config`: Configure all 6 digital outputs (DO0-DO5)
- `test_digital_input_config`: Configure all 4 digital inputs (DI0-DI3)
- `test_digital_output_toggle`: Blink outputs (visual verification with LEDs)
- `test_digital_input_read`: Read input states
- `test_digital_loopback_interactive`: **Interactive test** requiring wire connection

**Hardware Requirements:**
- **Optional:** LEDs connected to outputs for visual verification
- **For loopback test:** Wire connecting DO0 (GPIO40) to DI0 (GPIO4)

**Interactive Loopback Test:**
```
⚠️  HARDWARE SETUP REQUIRED:
    Please connect a wire between:
    - Pin DO0 (GPIO 40)
    - Pin DI0 (GPIO 4)
    
Waiting 10 seconds for you to connect the wire...
```

The test will set DO0 HIGH/LOW and verify DI0 reads the correct value.

**Expected Output:**
```
✅ All digital outputs configured
✅ All digital inputs configured
✅ DI0 correctly reads HIGH
✅ DI0 correctly reads LOW
```

---

## How to Build and Run

### Option 1: Build Individual Test

To build and flash a specific test:

```bash
cd esp32_gateway/test/device

# For CAN bus test
idf.py -DTEST_COMPONENT=test_can_bus_init build flash monitor

# For W5500 test
idf.py -DTEST_COMPONENT=test_w5500_spi_init build flash monitor

# For Digital I/O test
idf.py -DTEST_COMPONENT=test_digital_io build flash monitor
```

### Option 2: Run from Main Project

Alternatively, modify the main project's `CMakeLists.txt` to build tests:

```bash
cd esp32_gateway
idf.py -DENABLE_DEVICE_TESTS=1 build flash monitor
```

### Viewing Results

All tests use Unity test framework and will output:
- ✅ Green checkmarks for passed tests
- ❌ Red X for failed tests
- Final summary with pass/fail count

**Monitor the serial output:**
```bash
idf.py monitor
```

Press `Ctrl+]` to exit monitor.

---

## Test Execution Workflow

1. **Flash the test to ESP32**
   ```bash
   idf.py flash
   ```

2. **Open serial monitor**
   ```bash
   idf.py monitor
   ```

3. **Follow on-screen instructions**
   - Some tests are automatic
   - Interactive tests will display hardware setup requirements

4. **Verify results**
   - Check for "PASSED" messages
   - All tests should show ✅

---

## Integration with CI/CD

These tests are designed for **manual execution** on physical hardware. They are NOT suitable for automated CI/CD pipelines unless you have:

- Dedicated hardware test rig
- Automated flashing capability
- Serial output capture and parsing

For CI/CD, use the **native tests** in `esp32_gateway/test/native/` instead.

---

## Hardware Configuration Reference

All pin definitions come from `esp32_gateway/main/hardware_config.h`:

```cpp
// CAN Bus
#define PIN_CAN_TX 1
#define PIN_CAN_RX 2

// Ethernet (W5500)
#define PIN_ETH_SPI_MOSI 12
#define PIN_ETH_SPI_MISO 11
#define PIN_ETH_SPI_SCLK 13
#define PIN_ETH_CS       10
#define PIN_ETH_INT      14
#define PIN_ETH_RST      15

// Digital I/O
#define PIN_DI_0 4    // Input 0
#define PIN_DI_1 5    // Input 1
#define PIN_DI_2 6    // Input 2
#define PIN_DI_3 7    // Input 3

#define PIN_DO_0 40   // Output 0
#define PIN_DO_1 39   // Output 1
#define PIN_DO_2 38   // Output 2
#define PIN_DO_3 37   // Output 3
#define PIN_DO_4 36   // Output 4
#define PIN_DO_5 35   // Output 5
```

---

## Troubleshooting

### Build Errors

**Error:** `fatal error: hardware_config.h: No such file or directory`
**Solution:** Ensure you're building from the `esp32_gateway` directory and `hardware_config.h` exists in `main/`.

**Error:** `undefined reference to 'app_main'`
**Solution:** Each test file has its own `app_main()`. Build only one test at a time.

### Runtime Errors

**CAN Test Fails:**
- Check GPIO1 and GPIO2 are not used by other peripherals
- Verify ESP32 variant supports TWAI on these pins (ESP32-S3 does)

**W5500 Test Returns Wrong Version:**
- Check power supply to W5500 (3.3V)
- Verify SPI wiring (MOSI, MISO, SCLK, CS)
- Ensure proper ground connection

**Digital I/O Loopback Fails:**
- Verify wire connection between DO0 and DI0
- Check for shorts or incorrect wiring
- Test with multimeter to confirm voltage levels

---

## Next Steps

After all device tests pass:

1. ✅ **Hardware validated** - All connections correct
2. 🔄 **Integration testing** - Test full gateway application
3. 🚀 **End-to-end testing** - Connect to real K13 device

---

## Documentation

- **EdgeBox-Lite Manual:** `docs/EDGEBOX_LITE_MANUAL.md`
- **Hardware Config:** `esp32_gateway/main/hardware_config.h`
- **Gateway Implementation:** `esp32_gateway/GATEWAY_IMPLEMENTATION_COMPLETE.md`

---

**Created:** November 1, 2025  
**Version:** 1.0  
**Target Hardware:** EdgeBox-Lite with ESP32-S3
