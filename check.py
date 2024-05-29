from model import Interface
from utils import mask_network


def ip_check(devices):
    # connected interfaces should have same subnet
    for device in devices.values():
        for interface in device.interfaces.values():
            if not interface.ip:
                continue
            for neighbor in interface.neighbors:
                if not neighbor.ip:
                    continue
                if mask_network(interface.ip, interface.mask) != mask_network(neighbor.ip, neighbor.mask):
                    print(f"[WARN] Subnet unmatch: {device.name} {interface.name} {interface.ip} {neighbor.ip}")
    # check ip conflict
    ip_set = set()
    for device in devices.values():
        for interface in device.interfaces.values():
            if not interface.ip:
                continue
            if interface.ip in ip_set:
                print(f"[WARN] IP conflict: {device.name} {interface.name} {interface.ip}")
            ip_set.add(interface.ip)
