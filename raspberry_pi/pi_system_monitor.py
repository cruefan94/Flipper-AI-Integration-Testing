#!/usr/bin/env python3
"""Read-only Pi health snapshot; Python standard library, no device writes."""
import argparse, json, os, shutil, subprocess, time
from pathlib import Path

def read(path):
    try: return Path(path).read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError): return None

def mem():
    d={}
    for line in (read("/proc/meminfo") or "").splitlines():
        if ":" in line:
            k,v=line.split(":",1)
            try: d[k]=int(v.strip().split()[0])*1024
            except (ValueError,IndexError): pass
    t,a=d.get("MemTotal"),d.get("MemAvailable")
    return {"total_bytes":t,"available_bytes":a,"used_percent":round((t-a)*100/t,1) if t and a is not None else None}

def temp():
    try: return round(int(read("/sys/class/thermal/thermal_zone0/temp"))/1000,1)
    except (TypeError,ValueError): return None

def storage():
    try:
        d=shutil.disk_usage("/")
        return {"total_bytes":d.total,"free_bytes":d.free,"used_percent":round(d.used*100/d.total,1)}
    except OSError: return {"used_percent":None}

def service(name):
    try:
        p=subprocess.run(["systemctl","is-active",name],capture_output=True,text=True,timeout=3)
        return p.stdout.strip() or "unknown"
    except (OSError,subprocess.TimeoutExpired): return "unknown"

def qflipper_running():
    try:
        for p in Path("/proc").iterdir():
            if p.name.isdigit() and (read(p/"comm") or "").lower()=="qflipper": return True
    except OSError: pass
    return False

def network():
    try: return {p.name:read(p/"operstate") for p in Path("/sys/class/net").iterdir() if p.name!="lo"}
    except OSError: return {}

def report():
    cpu_temp=temp()
    try: load=list(os.getloadavg())
    except OSError: load=None
    m=mem(); d=storage()
    alerts=[]
    if cpu_temp is not None and cpu_temp>=80: alerts.append("HIGH_CPU_TEMPERATURE")
    if m["used_percent"] is not None and m["used_percent"]>=90: alerts.append("HIGH_MEMORY_USE")
    if d["used_percent"] is not None and d["used_percent"]>=90: alerts.append("LOW_DISK_SPACE")
    return {"timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
      "cpu":{"cores":os.cpu_count(),"load_1_5_15":load,"temperature_c":cpu_temp},
      "memory":m,"root_disk":d,"network_interfaces":network(),
      "services":{"pironman.service":service("pironman.service"),"ssh.service":service("ssh.service")},
      "flipper":{"usb_acm":sorted(p.name for p in Path("/dev").glob("ttyACM*")),
                 "usb_serial":sorted(p.name for p in Path("/dev").glob("ttyUSB*")),
                 "qflipper_running":qflipper_running(),
                 "qflipper_installed":bool(shutil.which("qFlipper") or shutil.which("qflipper"))},
      "alerts":alerts,"read_only":True}

def main():
    p=argparse.ArgumentParser(description="Read-only Raspberry Pi system monitoring")
    p.add_argument("--watch",type=int,metavar="SECONDS")
    a=p.parse_args()
    if a.watch is not None and a.watch<5: p.error("--watch must be >= 5")
    try:
        while True:
            print(json.dumps(report(),sort_keys=True),flush=True)
            if a.watch is None: break
            time.sleep(a.watch)
    except KeyboardInterrupt: pass

if __name__=="__main__": main()
