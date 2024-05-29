from dataclasses import dataclass


@dataclass
class Route:
    ip: str
    mask: str
    next_hop: str
    type: str
