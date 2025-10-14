# Email Inquiry to OpenEmbedded - EdgeBox-Hybrid Compatibility

**Subject:** Compatibility Inquiry: EdgeBox-Hybrid with Danfoss K13 F Receiver for Crane Control System

---

Dear OpenEmbedded Team,

I hope this email finds you well. I am writing to inquire about the compatibility of your **EdgeBox-Hybrid** device with a specific industrial application we are developing.

## Project Context

We are developing a **remote emergency stop system for bridge cranes** that requires an Ethernet-to-CAN gateway solution. Our architecture consists of:

- **Control Application**: Running on a remote computer
- **Gateway Device**: Ethernet-to-CAN bridge (this is where EdgeBox-Hybrid would fit)
- **Target Device**: Danfoss K13 F Receiver for crane control

## Technical Requirements

Our system needs to:
1. **Receive TCP/IP commands** from a control application over Ethernet
2. **Translate these commands** to CANopen protocol messages
3. **Communicate with Danfoss R13 F Receiver** via CAN bus
4. **Handle bidirectional communication** for command confirmation and status feedback

## Danfoss K13 F Receiver Specifications

The target device is the **Danfoss K13 F Receiver** used in industrial crane applications:
- **Product Link**: https://www.danfoss.com/en/products/dps/electronic-controls-hmi-and-iot/plusplus1-remote-controls/remote-control-receivers/r-family-receivers/r13-f/#tab-overview
- **Communication**: CANopen protocol
- **CAN Bus**: Standard industrial CAN interface
- **Application**: Bridge crane motor control and safety systems

## Specific Questions

1. **CAN Interface Compatibility**: Does the EdgeBox-Hybrid support CANopen protocol communication? Could you clarify which profiles (like CiA 301/402) and bus speeds are supported?

2. **Software Flexibility**: Can we develop custom applications on EdgeBox-Hybrid to handle:
   - TCP/IP server functionality
   - JSON command parsing
   - CANopen message translation
   - Real-time industrial communication requirements

3. **Industrial Certification**: Does EdgeBox-Hybrid meet industrial standards suitable for crane control applications?

4. **Development Support**: What development tools, SDKs, or documentation would be available for this type of implementation?

5. **Performance**: Can EdgeBox-Hybrid handle real-time communication requirements for safety-critical crane emergency stop systems?

## Technical Architecture

```
[Control Computer] ──Ethernet/TCP─► [EdgeBox-Hybrid] ──CAN/CANopen─► [Danfoss R13] ──► [Crane Motors]
                                    (Gateway)                        (Receiver)       (Emergency Stop)
```

## Additional Information

- **Use Case**: Industrial bridge crane safety system
- **Geography**: Implementation in South America (Peru/Chile)
- **Timeline**: Evaluation phase for hardware selection
- **Volume**: Initial prototype, potential for series production

We would greatly appreciate any technical information, compatibility confirmation, or guidance you can provide regarding the suitability of EdgeBox-Hybrid for this application.

If you need any additional technical specifications or have questions about our requirements, please don't hesitate to ask.

Thank you for your time and consideration. I look forward to your response.

Best regards,

**[Your Name]**  
**[Your Title]**  
**[Company Name]**  
**[Email Address]**  
**[Phone Number]**

---

**Attachments:**
- Technical specification document (if available)
- System architecture diagram (if needed)

**CC:** Technical support team (if applicable)
