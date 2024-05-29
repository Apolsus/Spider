from utils import mask_bit_to_mask


class BGPPeer:
    def __init__(self):
        self.address_family = None  # unicast | vpnv4
        self.ip = None
        self.area = None
        self.scope = "internal"

    def __str__(self):
        cfg = f"\tipv4-family {self.address_family}\n"
        cfg += f'\t\tpeer {self.ip} as-number {self.area}\n'
        cfg += f"\t\tpeer {self.ip} enable\n"
        return cfg


class BGPPeerGroup:
    def __init__(self):
        self.address_family = None
        self.name = None
        self.peer = []
        self.scope = "internal"

    def __str__(self):
        cfg = f"\tipv4-family {self.address_family}\n"
        cfg += f"\t\tgroup {self.name} {self.scope}\n"
        cfg += f"\t\tpeer {self.name} enable\n"
        for peer in self.peer:
            cfg += f"\t\tpeer {peer} group {self.name}\n"
            cfg += f"\t\tpeer {peer} enable\n"
        return cfg


class VPN:
    def __init__(self):
        self.name = None
        self.rd = None
        self.target_export = []
        self.target_import = []
        self.bind_interface = {}

    def __str__(self):
        cfg = f"ip vpn-instance {self.name}\n"
        cfg += f"\tipv4-family\n"
        cfg += f"\t\troute-distinguisher {self.rd}\n"
        if self.target_export:
            cfg += "\t\tvpn-target " + " ".join(self.target_export) + " export-extcommunity\n"
        if self.target_import:
            cfg += "\t\tvpn-target " + " ".join(self.target_import) + " import-extcommunity\n"

        for interface, ip in self.bind_interface.items():
            cfg += f"\tinterface {interface}\n"
            cfg += f"\t\tip binding vpn-instance {self.name}\n"
            if ip:
                ip, n_bits = ip.split('/')
                cfg += f"\t\tip address {ip} {mask_bit_to_mask(n_bits)}\n"
        return cfg


class MPLS:
    def __init__(self):
        self.ldp = True
        self.lsr_id = None
        self.lsp_trigger = 'all'
        self.ldp = []

    def __str__(self):
        cfg = f"mpls lsr-id {self.lsr_id}\n"
        cfg += f"\t\tlsp-trigger {self.lsp_trigger}\n"
        if self.ldp:
            cfg += "mpls ldp\n"
            for interface in self.ldp:
                cfg += f"\tinterface {interface}\n"
                cfg += "\t\tmpls\n"
                cfg += "\t\tmpls ldp\n"
        return cfg


class BGP:
    def __init__(self):
        self.area = None
        self.rr = False
        self.peers = []
        self.peer_group = {}
        self.network = []
        self.connect_interface = None

    def __str__(self):
        cfg = f"bgp {self.area}\n"

        for net in self.network:
            ip, n_bits = net.split('/')
            n_bits = int(n_bits)
            cfg += f"\tnetwork {ip} {mask_bit_to_mask(n_bits)}\n"

        for peer in self.peers:
            cfg += str(peer)
            if peer.area == self.area:
                cfg += f"\t\tpeer {peer.ip} next-hop-self\n"

        for peer_grp in self.peer_group.values():
            cfg += str(peer_grp)

        return cfg


class OSPF:
    def __init__(self):
        self.pid = None
        self.rid = None
        self.area = None
        self.network = []
        self.ospf_cost = {}

    def __str__(self):
        cfg = f"ospf {self.pid} router-id {self.rid}\n"
        cfg += f"\tarea {self.area}\n"
        for net in self.network:
            ip, n_bits = net.split('/')
            n_bits = int(n_bits)
            cfg += f"\tnetwork {ip} {mask_bit_to_mask(n_bits, anti_mask=True)}\n"

        for interface, cost in self.ospf_cost.items():
            cfg += (f"\tinterface {interface}\n"
                    f"\t\tospf cost {cost}\n")
        return cfg


class Interface:
    def __init__(self):
        self.name = None
        self.ip = None
        self.neighbors = []


class Router:
    def __init__(self):
        self.name = None
        self.interfaces = {}
        self.bgp = {}
        self.ospf = {}
        self.mpls = None
        self.vpn = {}
        self.routing_table = []

    def __str__(self):
        cfg = ""
        for interface in self.interfaces.values():
            if interface.ip:
                cfg += f"interface {interface.name}\n"
                ip, n_bits = interface.ip.split('/')
                cfg += f"\tip address {ip} {mask_bit_to_mask(n_bits)}\n"

        if self.mpls:
            cfg += str(self.mpls)

        for bgp in self.bgp.values():
            cfg += str(bgp)

        for ospf in self.ospf.values():
            cfg += str(ospf)

        for vpn in self.vpn.values():
            cfg += str(vpn)

        return cfg


class Switch(Router):
    def __init__(self):
        super().__init__()
        self.vlan = {}

    def __str__(self):
        cfg = ""
        if self.vlan:
            for vlan, (ip, ports) in self.vlan.items():
                cfg = f"vlan {vlan}\n"
                for port in ports:
                    cfg += f"\tport {port}\n"
                if ip:
                    cfg += f"\tip address {ip}\n"
        return cfg
