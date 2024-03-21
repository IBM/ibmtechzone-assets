import os

wwpn = os.environ["wwpn"]

def convert_wwpn(wwpn):
    if ":" in wwpn:
        new_wwpn = wwpn.replace(":", "")
    else:
        new_wwpn = ':'.join(wwpn[i:i+2] for i in range(0, len(wwpn), 2))

    return new_wwpn
    
new_wwpn = convert_wwpn(wwpn)
print(new_wwpn)