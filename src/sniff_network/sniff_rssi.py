#!/usr/bin/env python3
import platform
import argparse
import json 
import scapy.all as sca

PLATFORM = platform.system()


class PktFilter(object):
    """
    sniffer filter using ssids
    """
    def __init__(self, ssids):
        self.ssids = ssids

    def __call__(self, pkt):
        # if pkt.haslayer(sca.Dot11Beacon) and pkt.ID == 0:
        #     print(pkt.info)
        return pkt.haslayer(sca.Dot11Beacon) and pkt.ID == 0 \
                    and str(pkt.info, encoding="utf-8") in self.ssids
                    #and pkt.info in [i.encode('utf-8') for i in self.ssids]


def sniff_rssi(interface, ssid, amount):
    # pkt filter
    pkt_filter = PktFilter([ssid])

    # TODO: why Linux do not support monitor=True?
    if PLATFORM == 'Darwin':
        packets = sca.sniff(iface=interface, lfilter=pkt_filter, count=amount, monitor=True)
    elif PLATFORM == 'Linux':
        packets = sca.sniff(iface=interface, lfilter=pkt_filter, count=amount)
    else:
        raise ValueError('unknown system.')

    def parse_packet(p):
        field, val = p.getfield_and_val("present")
        names = [field.names[i] for i in range(len(field.names)) if (1 << i) & val != 0]
        # check if has signal strength field
        if "dBm_AntSignal" in names:
            return str(p.info, encoding="utf-8"), -(256 - ord(p.notdecoded[-2:-1]))
        return None, None

    data = []
    for pkt in packets:
        pkt_ssid, rssi = parse_packet(pkt)
        assert pkt_ssid == ssid
        data.append(rssi)
    return data


def main():
    # argument parser 
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", '-i', default='../../data/SSIDs.txt', required=True, type=str,
                        help="input file containing list of Wi-Fi SSIDs, one SSID per line")
    parser.add_argument("--output", '-o', default='../../data/result.txt', required=True, type=str,
                        help="output file recording RSSIs")
    parser.add_argument("--iface", '-if', required=True, type=str,
                        help="NIC interface to sniff on, NOTE monitor mode must be open beforehand!")
    parser.add_argument("--amount", '-a', default=100, type=int,
                        help="amount of total beacon frames to be captured at once(default: 100)")
    parser.add_argument("--tag", '-t', required=True, type=str,
                        help="tag for current position.")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise ValueError("input ssid not found.")

    if os.path.exists(arg.output):
        print("apending to existing result.txt")
    
    # only support MacOS and Linux 
    if PLATFORM not in ['Linux', 'Darwin']:
        raise ValueError('only support Linux or MacOS system.')

    # read ssids from input file. 
    with open(args.input, "r") as i:
        ssids = [_.strip() for _ in i.readlines()]
    print('get SSIDs: {}'.format(ssids))

    # sniff amount package for each ssid.
    print("position tag: {}".format(args.tag))
    data_dict = {'tag': args.tag}
    for ssid in ssids:
        print("sniffing ssid: {}".format(ssid))
        data = sniff_rssi(args.iface, ssid, args.amount)
        data_dict[ssid] = data

    # save to json
    print("saving to: {}".format(args.output))
    with open(args.output, 'a') as o:
        o.write(json.dumps(data_dict) + '\n')


if __name__ == "__main__":
    main()

