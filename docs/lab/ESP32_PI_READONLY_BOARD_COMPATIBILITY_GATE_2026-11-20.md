# ESP32-WROOM / ESP32-S2 / Raspberry Pi 4B: read-only lab compatibility gate

Status: PUBLIC-SAFE design/diagnostic fixture, 2026-11-20. Not a hardware-tested flashing recipe. No firmware, credentials, private logs, radio streams or user identifiers.

## Distinguish the two ESP32 targets
| Target | Boot entry | Transport candidates | Must establish before any programming |
| --- | --- | --- | --- |
| Classic ESP32-WROOM module on breakout | GPIO0 low during reset (EN low then released); GPIO0 released after ROM entry | 3.3 V UART0 via verified USB-UART adapter; USB only if carrier includes converter | Exact module/carrier pinout; 3.3 V logic and supply; EN pull-up; correct boot strap wiring; UART0 TX/RX crossed; common ground; verified ROM chip identity |
| ESP32-S2 development board | GPIO0 low during reset; some boards label buttons BOOT and RESET/EN | Native USB ROM download on supported board wiring, or 3.3 V UART; not interchangeable with classic ESP32 | Board schematic, USB connector path (native USB vs UART bridge), selected ROM transport, chip identity and board-specific boot sequence |
| Raspberry Pi 4B host | Not applicable | USB serial or USB native device enumeration | Correct physical port, stable power, no other process holding port, non-root access policy; never infer chip from tty name alone |
| Flipper Zero GPIO | Not a generic 5 V UART adapter | Only an explicitly reviewed 3.3 V interface and firmware-supported transport | Pinout, electrical limits, transport authorization, isolation from Pi/USB power; never wire multiple TX outputs together |

## Read-only Pi diagnostics (operator runs locally, not automation)
```sh
python3 --version
python3 -m esptool version
lsusb
ls -l /dev/serial/by-id/ 2>/dev/null || true
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || true
```
These commands only inventory local software and device nodes. The absence of `/dev/serial/by-id` does not prove a board is faulty. `lsusb` can show a USB-UART bridge without proving ESP ROM readiness. Never automatically select the first serial port. Do not run `write_flash`, `erase_flash`, `reset`, or any remote programming command in this workstream.

## Hardware safety gates
1. Disconnect power before changing wiring. Identify the exact board revision from its markings and manufacturer schematic; do not extrapolate ESP32-WROOM pin numbers to ESP32-S2.
2. Establish voltage domains: ESP32 GPIO is 3.3 V, not 5 V tolerant. Arduino Uno 5 V output requires appropriate level shifting into ESP32 input. Do not backfeed 5 V from Uno/Pi/USB into a 3.3 V rail.
3. Use one defined power source per rail, common signal reference only where electrically appropriate, and adequate regulator/current budget. Pi GPIO is not a substitute for a high-current ESP32 power supply.
4. Keep ESP32-WROOM and ESP32-S2 programming paths separate. A USB connector alone does not prove the board supports native USB flashing.
5. Distinguish a UART adapter's 3.3 V logic setting from its available 3.3 V power output; they are not equivalent guarantees.
6. Record chip family, board revision, USB VID/PID (if any), observed ROM boot text, selected interface, and operator approval in a **local** diagnostic worksheet. Sanitize serial numbers, paths and identifiers before publishing fixtures.
7. No Flipper GPIO reset/boot control until a separate transport contract, voltage review, owner approval, and physical bench tests pass.

## Integration handoff gate
- This document is not a flashing authorization, ESP32 firmware artifact, or proof of physical compatibility.
- Require exact-commit offline tests, CI run URL, schematic review, hardware observations made by owner, and safe recovery instructions before promoting a peripheral component.
- Keep it optional and outside Android test APK / native F7 Momentum updater until API/AI1 compatibility and device-level tests are proven.
- Respect two-failure CI fallback: two consecutive completed failures for the same workflow/branch (or repeated pre-job failure) route through approved PUBLIC-SAFE testing; missing private Actions:read => BLOCKED, never claimed successful.
- Do not retry known failing DFU CRC 9-99 updater; do not replace installed Android APK due to signing mismatch. No protected merges, hardware flashing, radio transmission or vehicle integration.
