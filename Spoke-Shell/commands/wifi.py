# commands/wifi.py
import time
from pywifi import PyWiFi, const, Profile

def connect_to_wifi(ssid, password):
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]  # Assuming first interface

    iface.remove_all_network_profiles()

    profile = Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = password

    tmp_profile = iface.add_network_profile(profile)

    iface.connect(tmp_profile)

    time.sleep(5)

    if iface.status() == const.IFACE_CONNECTED:
        print(f"Successfully connected to {ssid}")
        return True
    else:
        print("Failed to connect")
        return False

def run(args):
    if len(args) < 2:
        print("Usage: wifi <ssid> <password>")
        return
    ssid = args[0]
    password = args[1]
    connect_to_wifi(ssid, password)
