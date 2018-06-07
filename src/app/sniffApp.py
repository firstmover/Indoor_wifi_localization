#!/usr/bin/env python3
import sys
sys.path.insert(0, '../sniff_network')
sys.path.insert(0, '..')
import platform
import socket
import json
import scapy.all as sca
from sniff_rssi import sniff_rssi
import process

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.config import Config
Config.set("graphics", "width", '300')
Config.set("graphics", "height", "500")
from kivy.core.window import Window

PLATFORM = platform.system()
# only support MacOS and Linux 
if PLATFORM not in ['Linux', 'Darwin']:
    raise ValueError('only support Linux or MacOS system.')

class sniffWidget(Widget):
    
    def __init__(self, iface, amount, tag, func, serv_addr, bufsize=1024):
        """
            iface: interface to sniff on
            amount: max amount of latest rssis to maintain
            tag: value for tag field, used as sign
            func: function to process rssi list, should takes list of rssis in 
                  and output another list of single output value
            serv_addr: server addr, format as (HOST, PORT)
            bufsize: max size of receive buf, should be big enough
        """
        super(sniffWidget, self).__init__()
        self.iface = iface
        self.amount = amount
        self.tag = tag
        self.rssi_dict = {}
        self.rssi_dict["tag"] = tag
        self.prcs_dict = {}
        self.prcs_dict["tag"] = self.tag

        self.func = func

        # server addr
        self.serv_addr = serv_addr
        self.bufsize = bufsize

        # client socket
        # use ipv4 udp
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.sock.settimeout(3.0) 

        # initial communication with server
        self.config()
        
        # visualize aps
        self.visual_aps()

        # initial coords
        self.coords = (0, 0)

    def config(self):
        name_dict = {"tag": self.tag}
        # send the tag 
        self.sock.sendto(json.dumps(name_dict).encode('utf-8'), self.serv_addr)
        # receive the configuration of APs
        recv_msg, addr = self.sock.recvfrom(self.bufsize)
        recv_msg = str(recv_msg, encoding="utf-8")
        if addr == self.serv_addr:
            self.config_dict = json.loads(recv_msg)
            self.ssids = self.config_dict.keys()
            for ssid in self.ssids:
                self.rssi_dict[ssid] = []
                self.prcs_dict[ssid] = []
            return

        # try 10 times
        # if fail, then exit
        raise Exception("connect to server {} failed, please \
                         check your network connection and try again".format(self.serv_addr))
        sys.exit()
    
    def visual_aps(self):
        with self.canvas:
            Color(1, 0, 0)
            d = 30.0
            for ssid in self.ssids:
                x, y = self.config_dict[ssid]
                Ellipse(pos=(x*Window.size[0], y*Window.size[1]), size=(d, d))

    def sniff(self, dt):
        num = len(self.ssids)
        for ssid in self.ssids:
            data = sniff_rssi(self.iface, ssid, 1, dt)
            self.rssi_dict[ssid] += data

    def aging(self):
        """
            only keep the latest "amount" rssi values
        """
        for ssid in self.ssids:
            if len(self.rssi_dict[ssid]) > self.amount:
                self.rssi_dict[ssid] = self.rssi_dict[ssid][-1*self.amount:]

    def process(self):
        """
            process the rssis
        """
        for ssid in self.ssids:
            self.prcs_dict[ssid] = self.func(self.rssi_dict[ssid])
    
    def sendrecv(self):
        msg = json.dumps(self.prcs_dict)
        # send
        self.sock.sendto(msg.encode("utf-8"), self.serv_addr)
        # recv
        recv_msg, addr = self.sock.recvfrom(self.bufsize)
        recv_msg = str(recv_msg, encoding="utf-8")
        if addr == self.serv_addr:
            recv_dict = json.loads(recv_msg)
            self.coords = (recv_dict["x"], recv_dict["y"])

    def visualize(self):
        with self.canvas:
            Color = (1, 1, 0)
            d = 30.
            x, y = self.coords
            Ellipse(pos=(x*Window.size[0], y*Window.size[1]), size=(d, d))

    def update(self, dt):
        # update periodic of interval dt(s)
        # 1.sniff
        self.sniff(dt*0.8/len(self.ssids))
        # 2.aging
        self.aging()
        # 3.process
        self.process()
        # 4.sendrecv
        self.sendrecv()
        # 5.visualize
        self.visualize()

class sniffApp(App):

    def __init__(self, iface, amount, tag, func, serv_addr, bufsize=1024):
        super(sniffApp, self).__init__()
        self.iface = iface
        self.amount = amount
        self.tag = tag
        self.func = func
        self.serv_addr = serv_addr
        self.bufsize = bufsize

    def build(self):
        sniffer = sniffWidget(self.iface, self.amount, self.tag, self.func, self.serv_addr, self.bufsize)
        Clock.schedule_interval(sniffer.update, 5.0)
        return sniffer

if __name__ == "__main__":
    iface = "wlp3s0"
    amount = 3
    tag = "zxz"
    func = process.__dict__["data_"+"median"]
    serv_addr = ("127.0.0.1", 12138)
    sniffApp(iface, amount, tag, func, serv_addr).run()


