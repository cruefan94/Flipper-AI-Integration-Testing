"""Pure offline classification of Pi USB identity snapshots; never opens a device."""
from dataclasses import dataclass
import re

PORT = re.compile(r'^/dev/(ttyUSB|ttyACM)[0-9]+$')
HEX4 = re.compile(r'^[0-9a-fA-F]{4}$')

@dataclass(frozen=True)
class Observation:
    port: str
    vid: str
    pid: str
    serial: str = ''
    driver: str = ''

def evaluate(observations, requested_port):
    """Return (status, reason). No port is opened or changed."""
    if not PORT.fullmatch(requested_port):
        return 'DENY', 'invalid requested port'
    if not observations:
        return 'DENY', 'no observations'
    if any(not PORT.fullmatch(o.port) or not HEX4.fullmatch(o.vid) or not HEX4.fullmatch(o.pid) for o in observations):
        return 'DENY', 'invalid observation'
    ports = [o.port for o in observations]
    if len(set(ports)) != len(ports):
        return 'DENY', 'duplicate port observations'
    matches = [o for o in observations if o.port == requested_port]
    if not matches:
        return 'DENY', 'requested port absent'
    match = matches[0]
    if not match.serial.strip():
        return 'REVIEW', 'missing stable serial identity'
    same = [o for o in observations if o.serial.strip() == match.serial.strip()]
    if len(same) > 1:
        return 'DENY', 'serial identity collision'
    return 'REVIEW', 'identity snapshot only; requires human board verification'
