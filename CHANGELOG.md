# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

- `docs/hardware_gateways_simplified.md`: created simplified hardware comparison focusing on SOC ARM + Ubuntu IoT + CAN integrated solutions. Recommends Revolution Pi Connect+ SE as optimal choice for industrial crane control.
- `docs/hardware_gateways_comparison.md`: comprehensive comparison of Ethernet-CAN gateways for industrial crane control. Analyzed PEAK PCAN-Ethernet Gateway DR, HMS Anybus X-Gateway, Raspberry Pi Industrial, ESP32 alternatives, and industrial SOC devices with detailed technical specifications, programming examples, and vendor information.
- `src/k13_controller/rpi_can_gateway.py`: added Raspberry Pi CAN HAT driver with CANopen support for Danfoss R13 communication.
- `config/raspberry_pi_config.yaml`: added comprehensive configuration for Raspberry Pi + CAN HAT setup including hardware-specific settings and safety parameters.
- `README.md`: consolidated Executive Summary; unified architecture and communication flow; simplified and compacted diagrams.
- `email_openembedded_inquiry.md`: created and revised. Removed explicit CAN bus speed and direct references to CiA 301/402; updated questions to request vendor clarification on supported CANopen profiles and bus speeds.
- Documentation formatting: compacted markdown in the inquiry file to reduce blank-line and paste issues when copying into Gmail.
- Repository: local Git repository initialized; initial commit created (project skeleton, docs, tests, VS Code tasks).

## 2025-09-10 - Initial commit

- Project skeleton and source files added.
- Documentation and diagrams added to `README.md`.
- Tests added under `tests/` and passing locally.
- VS Code tasks and setup scripts added under `scripts/`.

For older history, check the Git commit log.
