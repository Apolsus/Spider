def mask_bit_to_mask(mask_bit, anti_mask=False):
    mask = [0, 0, 0, 0]
    mask_bit = int(mask_bit)
    for i in range(mask_bit):
        mask[i // 8] |= 1 << (7 - i % 8)
    if anti_mask:
        mask = [255 - x for x in mask]

    mask = '.'.join(map(str, mask))
    return mask


def mask_network(ip, bits):
    ip = ip.split('.')
    bits = int(bits)
    mask = mask_bit_to_mask(bits)
    network = [str(int(ip[i]) & int(mask.split('.')[i])) for i in range(4)]
    network = '.'.join(network)
    return network
