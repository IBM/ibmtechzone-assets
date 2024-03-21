import sys

def convert_wwpn(wwpn):
    if ":" in wwpn:
        # Colons are present, so remove them
        new_wwpn = wwpn.replace(":", "")
    else:
        # Colons are missing, so add them
        new_wwpn = ':'.join(wwpn[i:i+2] for i in range(0, len(wwpn), 2))

    return new_wwpn

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <WWPN>")
        sys.exit(1)

    wwpn = sys.argv[1]
    new_wwpn = convert_wwpn(wwpn)
    print(new_wwpn)