import json
import os
import shutil

from model import BGPPeer, BGPPeerGroup, VPN, MPLS, BGP, OSPF, Interface, Router, Switch


def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def parse_link(config, devices):
    for link_config in config['Link']:
        source_device_name, source_interface_name = link_config[0].split('.')
        target_device_name, target_interface_name = link_config[1].split('.')
        source_device = devices.get(source_device_name)
        target_device = devices.get(target_device_name)
        source_interface = source_device.interfaces[source_interface_name]
        target_interface = target_device.interfaces[target_interface_name]
        source_interface.neighbors.append(target_interface)
        target_interface.neighbors.append(source_interface)


def parse_ip(config, devices):
    for key, ip in config['IP'].items():
        device_name, interface_name = key.split('.')
        device = devices.get(device_name)
        interface = device.interfaces[interface_name]
        interface.ip = ip


def parse_vlan(config, devices):
    for vlan_config in config['VLAN']:
        for device_name, device in devices.items():
            if isinstance(device, Switch):
                vlan = device.vlan
                vlan_id = vlan_config['id']
                interfaces = vlan_config['interfaces']
                ip = vlan_config.get('ip', None)
                vlan[vlan_id] = (ip, interfaces)


def parse_ospf(config, devices):
    for ospf_config in config['OSPF']:
        for device_config in ospf_config['devices']:
            area = ospf_config['area']
            device_name = device_config['name']
            device = devices.get(device_name)
            ospf = OSPF()
            ospf.pid = len(device.ospf)  # HACK
            ospf.rid = device_config['router_id']
            ospf.area = area
            ospf.network = device_config.get('network', [])
            ospf.ospf_cost = device_config.get('cost', {})
            device.ospf[ospf.pid] = ospf


def parse_bgp(config, devices):
    for bgp_config in config['BGP']:
        for device_config in bgp_config['devices']:
            area = bgp_config['area']
            device_name = device_config['name']
            device = devices[device_name]
            bgp = BGP()
            bgp.rr = device_config.get('rr', False)
            bgp.area = area
            bgp.network = device_config.get('network', [])

            for peer in device_config.get('peers', []):
                bgp_peer = BGPPeer()
                bgp_peer.address_family = peer['address_family']
                bgp_peer.ip = peer['ip']
                bgp_peer.area = peer['area']
                bgp.peers.append(bgp_peer)

            for peer_grp in device_config.get('peer_group', []):
                bgp_peer_group = BGPPeerGroup()
                bgp_peer_group.name = peer_grp['name']
                bgp_peer_group.peer = peer_grp['peer']
                bgp.peer_group[bgp_peer_group.name] = bgp_peer_group

            device.bgp[area] = bgp


def parse_mpls(config, devices):
    for mpls_config in config['MPLS']:
        device_name = mpls_config['name']
        device = devices.get(device_name)
        mpls = MPLS()
        mpls.lsr_id = mpls_config['lsr_id']
        mpls.ldp = mpls_config.get('ldp', [])
        device.mpls = mpls


def parse_vpn(config, devices):
    for vpn_config in config['VPN']:
        for device_config in vpn_config['devices']:
            vpn = VPN()
            vpn.name = vpn_config['name']
            vpn.rd = vpn_config['rd']
            vpn.target_export = vpn_config.get('vpn_target_export', [])
            vpn.target_import = vpn_config.get('vpn_target_import', [])
            device_name = device_config['name']
            device = devices.get(device_name)
            for interface in device_config['interfaces']:
                vpn.bind_interface[interface] = device.interfaces[interface].ip
            device.vpn[vpn.name] = vpn


def create_devices(config):
    devices = {}
    for device_config in config['Device']:
        if device_config['type'] == 'router':
            device = Router()
        elif device_config['type'] == 'switch':
            device = Switch()
        else:
            raise ValueError(f"Unknown device type: {device_config['type']}")
        device.name = device_config['name']
        for interface_name in device_config['interfaces']:
            interface = Interface()
            interface.name = interface_name
            device.interfaces[interface_name] = interface

        devices[device.name] = device
    return devices


def parse():
    config = load_config('config.json')
    devices = create_devices(config)

    parse_ip(config, devices)
    parse_vlan(config, devices)
    parse_ospf(config, devices)
    parse_bgp(config, devices)
    parse_mpls(config, devices)
    parse_vpn(config, devices)

    return devices


if __name__ == '__main__':
    devices_ = parse()

    # rm -r res
    shutil.rmtree('res', ignore_errors=True)
    os.mkdir('res')

    for device_name_, device_ in devices_.items():
        with open(f'res/{device_name_}.vrf', 'w') as f:
            f.write(str(device_))
