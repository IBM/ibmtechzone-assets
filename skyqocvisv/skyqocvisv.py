import sys

def convert_wwpn(wwpn):
    if ":" in wwpn:
        # Colons are present, so remove them
        new_wwpn = wwpn.replace(":", "")
    else:
        # Colons are missing, so add them
        new_wwpn = ':'.join(wwpn[i:i+2] for i in range(0, len(wwpn), 2))

    return new_wwpn

new_wwpn = convert_wwpn(wwpn)
print(new_wwpn)