# Conexión Servidor ↔ Danfoss IC7 — Resumen simple

Objetivo: el servidor de visión (en red local) detiene la grúa cuando detecta peligro, enviando comandos de paro al IC7 (que es el variador/controlador de la grúa).

**Nota importante**: El IC7 es el variador que controla los motores. Tu servidor le envía comandos (Quick Stop, Reset, etc.) para controlarlo.

## Diagrama

```
Servidor (en red local) ──► (Gateway si hace falta) ──► IC7 (Variador)
                                                             │
                                                             ▼
                                                         Motores grúa
```

**Opcional** (solo si exigen certificación SIL/PL):
```
Servidor ──► PLC/Relé de seguridad ──► Entrada STO del IC7 (corte eléctrico directo)
```

## Alternativas

- Ethernet directo (sin gateway)
  - Cuándo: el IC7 tiene puerto Ethernet.
  - Qué necesitas: cable de red del servidor al IC7.

- RS‑485 (con gateway)
  - Cuándo: el IC7 sólo tiene puerto RS‑485.
  - Qué necesitas: un equipo convertidor IP a RS‑485.

- CANopen (con gateway)
  - Cuándo: el IC7 tiene puerto CANopen.
  - Qué necesitas: un gateway que convierta IP a CANopen.

- PLC/Relé de seguridad (opcional)
  - Cuándo: solo si te lo exigen por normas de seguridad industrial.
  - Qué hace: corta la electricidad al variador si falla la red.

## Decidir rápido

- ¿IC7 tiene Ethernet? → enviar comandos directo por red local (el caso más simple).
- ¿IC7 sólo tiene RS‑485/CANopen? → necesitas un gateway local.
- ¿Exigen certificación SIL/PL? → agregar PLC/relé de seguridad (casi nunca necesario para pruebas).

## Próximos pasos

1) Identificar qué puertos tiene el IC7: ¿Ethernet / CANopen / RS‑485?
2) Conseguir el equipo necesario (gateway si hace falta).
3) Probar según el puerto:
   - Ethernet: enviar comando de Quick Stop por red y ver si para.
   - RS‑485: conectar gateway, enviar comando y ver si para.
   - CANopen: conectar gateway, configurar y probar parada.
4) (Opcional) Si exigen certificación: agregar PLC/relé de seguridad.
