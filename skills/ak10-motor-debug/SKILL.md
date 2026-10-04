---
name: ak10-motor-debug
description: Debug and control Cubemars AK10-9 (and AK series) motors via STM32H723 FDCAN. Use when the user is bringing up, tuning, diagnosing, or writing control code for AK10 motors over CAN bus.
allowed-tools: Bash, Read, Grep, Edit, Write
---

# AK10-9 Motor Debug & Control Guide

This skill guides bring-up, control, and diagnostics of Cubemars AK10-9 motors (and other AK-series actuators) using the STM32H723 FDCAN reference implementation.

## When to Use This Skill

- First-time power-on and CAN communication check
- Enabling/disabling the motor or setting zero position
- Sending velocity / position / MIT control frames
- Parsing motor feedback and diagnosing why feedback is missing
- Investigating runaway, saturation, or no-motion issues

## Quick Reference

| Parameter | Range |
| --- | --- |
| Motor ID | 1 – 8 |
| Position `p_des` | [-12.56, 12.56] rad |
| Velocity `v_des` | [-60.0, 60.0] rad/s |
| Torque `t_ff` | [-12.0, 12.0] N·m |
| Kp | [0.0, 500.0] |
| Kd | [0.0, 5.0] |

MIT control frame bit layout (DLC=8, standard CAN ID = motor ID):

```text
p_des : 16 bits -> data[0..1]
v_des : 12 bits -> data[2..3:4]
kp    : 12 bits -> data[3:4..4]
kd    : 12 bits -> data[5..6:4]
t_ff  : 12 bits -> data[6:4..7]
```

Special extended-frame commands (ID = motor ID, extended frame):

| Command | data[0..7] |
| --- | --- |
| Enable | `FF FF FF FF FF FF FF FC` |
| Disable | `FF FF FF FF FF FF FF FD` |
| Set zero | `FF FF FF FF FF FF FF FE` |

## Hardware Checklist

Before writing code, verify the physical layer:

1. **Power**: supply voltage and current capability match AK10-9 spec.
2. **CAN wiring**: CAN_H, CAN_L, and a common ground between motor and MCU.
3. **Termination**: 120 Ω resistor at each end of the CAN bus.
4. **Pins**: STM32H723 uses FDCAN1 on PD0 (RX) / PD1 (TX).
5. **UART debug**: UART7 on PE8 (TX) / PE7 (RX), 921600 8N1.

## Bring-Up Flow

### 1. Verify the firmware build

Open the reference Keil project:

```text
ak10_h723_ctrl/MDK-ARM/AK10_H723.uvprojx
```

Expected toolchain: Keil MDK-ARM or STM32CubeMX-generated HAL.

### 2. Enable the motor

After boot, send the enable command before any motion command:

```c
ak10_enable(&hfdcan1, 1);
```

This enters MIT/control mode.

### 3. Send a safe velocity command

Start with zero velocity (effectively a soft hold):

```c
ak10_mit_ctrl(&hfdcan1, 1, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f);
```

Then move slowly:

```c
ak10_mit_ctrl(&hfdcan1, 1, 0.0f, 3.0f, 0.0f, 0.0f, 0.0f);
```

### 4. Disable when done

```c
ak10_disable(&hfdcan1, 1);
```

**Important**: `disable` exits motor control mode and frees the shaft. `stop` (zero-velocity command) still keeps the motor active.

## Position Control

The reference code uses a host-side position loop because raw `p_des + kp/kd` control was observed to overshoot or saturate.

Recommended approach:

1. Read motor feedback position.
2. Compute error and generate a velocity setpoint.
3. Send velocity-mode MIT frame:

```c
ak10_mit_ctrl(&hfdcan1, 1, 0.0f, target_vel_rad_s, 0.0f, 0.0f, 0.0f);
```

For absolute/relative position commands via UART:

```text
abs 1.57   # absolute position target, needs fresh feedback
rel 0.5    # relative offset from current feedback, needs fresh feedback
zero       # set current mechanical position as zero
```

Position wrapping: feedback is bounded to [-12.56, 12.56] rad. Compute shortest-path error near the ±12.56 boundary.

## Feedback Diagnosis

Use the `status` UART command. It prints three lines:

```text
id=... mode=... en=... tgt_p=... tgt_v=... fb=... p=... v=... t=...
cnt ctrl=... fb=... can_rx=... drop=... uart=... err=...
last id=0x... type=std/ext len=... data=...
```

### Interpretation

- `fb=1` and `fb` counter increasing → feedback parsing is healthy.
- `can_rx` increases but `fb` does not → frame received but motor ID or frame layout mismatch; inspect `last id/type/len/data`.
- `can_rx` does not increase → check wiring, termination, baud rate, transceiver power, and whether motor is actually replying.

### Common Issues

| Symptom | Likely Cause | Action |
| --- | --- | --- |
| Motor does not move | Not enabled | Send `ak10_enable()` first |
| Motor spins continuously | Position target saturated to ±12.56 rad | Use host-side velocity loop or reduce target |
| No feedback | Wrong motor ID / CAN id mismatch | Verify motor ID switch/jumper and `target_id` |
| No feedback | Baud rate mismatch | Confirm 1 Mbps on both sides |
| Runaway on CAN disconnect | AK10 has no comm timeout disable | Always disable or send safe command before disconnecting |

## Safety Rules

1. **AK10 does NOT have a communication timeout disable.** If CAN is disconnected while a non-zero command is active, the motor continues executing the last command. Always `disable` or send a safe zero-velocity command before power-down or disconnection.
2. Prepare an independent emergency stop or power cut before running motion commands.
3. Keep initial velocity and torque limits low during first tests.
4. Send `set_zero` only when the mechanism is mechanically safe, stationary, and you are sure no unintended motion will occur.

## Reference Files

- Motor protocol implementation: `source/User/ak10_motor.c`, `source/User/ak10_motor.h`
- Python protocol tests: `tools/ak10_protocol.py`, `tests/test_ak10_protocol.py`
- Hardware/debug notes: `docs/Cubemars_AK10_电机控制调试说明_20260702.md`, `docs/README_AK10.md`

## Debugging Prompt Template

When the user reports a motor issue, follow this order:

1. Ask for motor ID, power state, and whether `enable` was sent.
2. Check the latest `status` output for `fb`, `can_rx`, and `last id/type/data`.
3. Verify target values are inside the ranges in the Quick Reference table.
4. If `can_rx` is zero, focus on physical layer (wiring, termination, baud, transceiver).
5. If `can_rx` is non-zero but `fb` is zero, focus on frame layout / motor ID mismatch.
6. If feedback is healthy but motion is wrong, check for saturation or position-loop wrapping.
