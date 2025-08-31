import psutil
import os 

def run(args):
    # Get CPU usage for each core
    cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
    for i, usage in enumerate(cpu_per_core):
        print(f"CPU Core {i}: {usage}%")