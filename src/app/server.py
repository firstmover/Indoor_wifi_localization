import socket
import threading
import time
from datetime import datetime
import random

class Server():
    """Server process class"""
    def __init__(self, addr_type, serv_type, addr):
        """ addr_type: str, can be 'ipv4' or 'ipv6'
            serv_type: str, can be 'tcp' or 'udp'
            addr: needed only when serv_type == 'tcp'"""
        if addr_type == 'ipv4':
            self.addr_type = socket.AF_INET
        elif addr_type == 'ipv6':
            self.addr_type = socket.AF_INET6
        else:
            raise Exception("invalid addr_type", addr_type, "should be 'ipv4' or 'ipv6'")

        if serv_type == 'tcp':
            self.serv_type = socket.SOCK_STREAM
        elif serv_type == 'udp':
            self.serv_type = socket.SOCK_DGRAM
        else:
            raise Exception("invalid serv_type", serv_type, "should be 'tcp' or 'udp'")

        self.addr = addr
        self.sock = socket.socket(self.addr_type, self.serv_type)
        self.sock.bind(addr)
        print("[{}] Server: creates a socket at address: {}".format(datetime.now(), self.addr))

    def start(self, max_queue_num=5, bufsize=4096):
        self.bufsize = bufsize
        thread = threading.Thread(target=self._udp_start)
        thread.start()
        while thread.isAlive():
            thread.join(0.1)
        self.sock.close()
        print("[{}] Server: socket closed, server exit".format(datetime.now()))

    def _udp_start(self):
        print("[{}] Server: started at address {}...".format(datetime.now(), self.addr))
        msg1 = '{"Xiaomi_8334": [0.5, 0],"Wireless PKU": [0.99, 0.5], "PKU Visitor":[0.5, 0.99]}'
        cnt = 0
        try:
            while 1:
                # receive data and send back
                data, clientaddr = self.sock.recvfrom(self.bufsize)
                print("[{}] Server receive:{}({})".format(datetime.now(), data, clientaddr))
                if data:
                    choice = input("send msg number")
                    if choice == 1:
                        msg = msg1
                    else:
                        x = random.uniform(0.1, 0.9)
                        y = random.uniform(0.1, 0.9)
                        msg = '{"x": %f, "y": %f}'%(x, y)
                    self.sock.sendto(msg, clientaddr)
                    print("[{}] Server send: {}({})".format(datetime.now(), msg, clientaddr))
        except Exception as e:
            print("[{}] Server : error '{}' occured".format(datetime.now(), e))
        '''
        thread = threading.Thread(target=self._udp_serv)
        thread.start()
        while thread.isAlive():
            thread.join(1.0)
        '''

if __name__ == "__main__":
    addr_type = "ipv4"
    serv_type = "udp"
    addr = ("127.0.0.1", 12138)
    server = Server(addr_type, serv_type, addr)
    server.start()

