import psutil
import os

def run(args):
    if not args:
        print("Usage: kill <processName>")
        return
    
    process_name = " ".join(args)  # keep original casing
    killed_any = False

    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            cmdline = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            name = proc.info['name'] if proc.info['name'] else ''
            
            if process_name in name or process_name in cmdline:
                proc.kill()
                print(f"Killed process {proc.info['name']} (PID {proc.pid})")
                killed_any = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if not killed_any:
        print(f"No process matching '{process_name}' found.")