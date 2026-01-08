#!/usr/bin/python3

import socket
import threading
from queue import Queue
import ipaddress



target = input("Ange IP-adress at skanna: ")

try:
    ipaddress.ip_address(target)
    queue = Queue()
    open_ports = []

    def portscan(port):
        try:
            s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s1.settimeout(1)
            s1.connect((target, port))
            return True
        except:
            return False

    def fill_queue(port_list):
        for port in port_list:
            queue.put(port)

    def worker():
        while not queue.empty():
            port = queue.get()
            if portscan(port):
                    print("Port{} is open!".format(port))
                    open_ports.append(port)                        
    port_list = range(1, 1024)
    fill_queue(port_list)
    open_ports.sort()

    thread_list = []

    for i in range(100):
        thread = threading.Thread(target=worker)
        thread_list.append(thread)

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

    print("Open ports are: ", open_ports)

except ValueError:
    print("Please only enter a valid IP-address")