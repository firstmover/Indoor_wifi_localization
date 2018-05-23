#!python3
import platform
PLATFORM = platform.system() 
import argparse
import struct
import json 
import scapy.all as sca 
from IPython import embed


class PktFilter(object):
    """
    sniffer filter using ssids
    """
    def __init__(self, ssids):
        self.ssids = ssids

    def __call__(self, pkt):
        return pkt.haslayer(sca.Dot11Beacon) and pkt.ID == 0 \
                            and str(pkt.info, encoding="utf-8") in self.ssids

class ScapyRssi:
    def __init__(self, ssids):
        # data
        self.data = {}
        self.filter = PktFilter(ssids)

    def sniff(self, interface, amount):
        # TODO: why Linux do not support monitor=True?
        if PLATFORM == 'Darwin':
            packets = sca.sniff(iface=interface, lfilter=self.filter, count=amount, monitor=True)
        elif PLATFORM == 'Linux':
            packets = sca.sniff(iface=interface, lfilter=self.filter, count=amount)
        else:
            raise ValueError('unknown system.')
        for pkt in packets:
            ssid, rssi = self.parsePacket(pkt)
            print(ssid, rssi)
            if ssid is not None:
                if ssid in self.data.keys():
                    self.data[ssid].append(rssi)
                else:
                    self.data[ssid] = [rssi]

    def parsePacket(self, pkt):
        field, val = pkt.getfield_and_val("present")
        names = [field.names[i] for i in range(len(field.names)) if (1 << i) & val != 0]
        #print(names)
        #print(pkt)
        # check if has signal strength field
        if "dBm_AntSignal" in names:
            return str(pkt.info, encoding="utf-8"), -(256 - ord(pkt.notdecoded[-2:-1]))

        return None, None


def main():
    # argument parser 
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", '-i', default='SSIDs.txt', required=True, type=str, 
            help="input file containing list of Wi-Fi SSIDs, one SSID per line")
    parser.add_argument("--output", '-o', default='result.txt', required=True, type=str, 
            help="output file recording RSSIs")
    parser.add_argument("--iface", '-if', required=True, type=str, 
            help="NIC interface to sniff on, NOTE monitor mode must be open beforehand!")
    parser.add_argument("--amount", '-a', default=100, type=int, 
            help="amount of total beacon frames to be captured at once(default: 100)")
    args = parser.parse_args()

    # only support MacOS and Linux 
    if PLATFORM not in ['Linux', 'Darwin']:
        raise ValueError('only support Linux or MacOS system.')

    # read ssids from input file. 
    with open(args.input, "r") as i:
        ssids = [_.strip() for _ in i.readlines()]
    print('SSIDs: {}'.format(ssids))

    # do sniff
    sniffer = ScapyRssi(ssids)
    sniffer.sniff(args.iface, args.amount)

    # debug
    #print(sniffer.data)
    # save to json
    with open(args.output, "a") as o:
        json.dump(sniffer.data, o)
        o.write("\n")

if __name__ == "__main__":
    main()





    

