#!/usr/bin/env python3
import platform
import argparse
import json 
import subprocess 
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
                            and pkt.info in [i.encode('utf-8') for i in self.ssids]


def sniff_rssi_cmd(interface, ssid, amount):
    import time 
    if PLATFORM == 'Darwin':
        data = []
        while True:
            std_out = subprocess.check_output(['airport', '-s'])
            std_out = std_out.decode('utf-8').split('\n')
            # not sure what happens when ssid is Chinese.
            std_out = std_out[1:]
            ssid_sniffed = [i[:32].strip() for i in std_out if len(i) > 32]
            for i, s in enumerate(ssid_sniffed):
                if s == ssid:
                    data.append(int(std_out[i][51:54]))
                    break 
            if len(data) >= amount:
                break 
        return data 

    elif PLATFORM == 'Linux':
        raise NotImplementedError('Linux cmd sniffing not implemented.')
    else:
        raise ValueError('unknown system.')


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
        data = sniff_rssi_cmd(args.iface, ssid, args.amount)
        data_dict[ssid] = data

    # save to json
    print("saving to: {}".format(args.output))
    with open(args.output, "a") as o:
        o.write(json.dumps(data_dict) + '\n')


if __name__ == "__main__":
    main()

