# utils.py
import platform
import socket

def get_system_info():
    return {
        "os": platform.system(),
        "hostname": socket.gethostname(),
        "platform_version": platform.version(),
        "architecture": platform.architecture()[0]
    }