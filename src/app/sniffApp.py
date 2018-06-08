#!/usr/bin/env python3
import sys
sys.path.insert(0, '../sniff_network')
sys.path.insert(0, '..')
import platform
PLATFORM = platform.system()


import socket
import json
import scapy.all as sca
from sniff_rssi import sniff_rssi
from sniff_rssi_cmd import sniff_rssi_cmd 
import process

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, InstructionGroup
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.config import Config
Config.set("graphics", "width", '600')
Config.set("graphics", "height", "1000")
from kivy.core.window import Window

PLATFORM = platform.system()
# only support MacOS and Linux 
if PLATFORM not in ['Linux', 'Darwin']:
    raise ValueError('only support Linux or MacOS system.')

class DynamicBtn(Button):
    
    def __init__(self, **kwargs):
        kwargs["text"] = "Start"
        super(DynamicBtn, self).__init__(**kwargs)
        # flag used to indicate the status
        # initial -1 means not yet pressed
        # once pressed, the flag can only have 2 states: 0 and 1
        # 0: means the button has been pressed for even times
        # thus the text shown should be "Resume" 
        # 1: otherwise, show "Pause"
        # NOTE: once another "Clear" button has been pressed
        # this button re-initialize to -1 and show "Start"
        self.flag = -1

    def reinit(self):
        self.text = "Start"
        self.flag = -1


class sniffWidget(Widget):
    
    # two button as property
    btn1 = ObjectProperty(None)
    btn2 = ObjectProperty(None)
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
        #self.visual_aps()

        # initial coords
        self.coords = (0, 0)
    
        # used to record all instructions that draw user-dots
        self.obj = InstructionGroup()
        self.objects = []

        # used to indicate whether update should be down actually
        self.update_flag = 0
    
        # children widget, 2 buttons
        # define event behavior for those two
        def _on_press1(instance):
            # change the text and flag
            if instance.flag == -1:
                instance.flag = 1
                instance.text = "Pause"
                instance.parent.set_flag()
            elif instance.flag == 0:
                instance.flag = 1
                instance.text = "Pause"
                instance.parent.set_flag()
            elif instance.flag == 1:
                instance.flag = 0  
                instance.text = "Resume"
                instance.parent.unset_flag()

        def _on_press2(instance):
            # clear the canvas and re-initial btn1
            instance.parent.clear()
            instance.parent.btn1.reinit()
            instance.parent.unset_flag()
        
        self.btn1.bind(on_press=_on_press1)
        self.btn2.bind(on_press=_on_press2)

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

        # if fail, then exit
        raise Exception("connect to server {} failed, please \
                         check your network connection and try again".format(self.serv_addr))
        sys.exit()
    
    def visual_aps(self):
        with self.canvas:
            Color(1, 0, 0)
            d = 20.0
            for ssid in self.ssids:
                x, y = self.config_dict[ssid]
                print(x*Window.size[0])
                print(y*Window.size[1])
                Ellipse(pos=(x*Window.size[0], y*Window.size[1]), size=(d, d))

    def sniff(self, dt):
        '''
        num = len(self.ssids)
        for ssid in self.ssids:
            data = sniff_rssi_cmd(self.iface, ssid, 1, dt)
            self.rssi_dict[ssid] += data
        '''
        data_dict = sniff_rssi_cmd_list(self.iface, self.ssids, 1, dt)
        for ssid in self.ssids:
            self.rssi_dict[ssid] += data_dict[ssid]
        

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
        self.obj = InstructionGroup()
        d = 20.
        x, y = self.coords
        self.obj.add(Color(0,1,0))
        self.obj.add(Ellipse(pos=(x*Window.size[0], y*Window.size[1]), size=(d, d)))
        self.canvas.add(self.obj)
        self.objects.append(self.obj)

    def clear(self):
        # clear all user dots
        for obj in self.objects:
            self.canvas.remove(obj)
        self.objects = []

    def set_flag(self):
        self.update_flag = 1

    def unset_flag(self):
        self.update_flag = 0

    def update(self, dt):
        print("in update")
        if self.update_flag:
            # update periodic of interval dt(s)
            # 1.sniff
            self.sniff(dt*0.08/len(self.ssids))
            # 2.aging
            self.aging()
            print(self.rssi_dict)
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
    if PLATFORM == 'Darwin':
        iface = "en0" 
    elif PLATFORM == 'Linux':
        iface = "wlp3s0"
    else:
        raise ValueError('unsupported system.')
    amount = 3
    tag = "zxz"
    func = process.__dict__["data_"+"median"]
    serv_addr = ("127.0.0.1", 12138)
    sniffApp(iface, amount, tag, func, serv_addr).run()


