#!/usr/bin/python3

import socket
import threading
from queue import Queue

target = ""
queue = Queue()
open_ports = []

def meny():
    print("What do you want to scan:")
    print("1. Your own PC(local host)")
    print("2. Your router")
    print("3. Enter you own IP-address")
    print("4. Try a specific port")
    print("5. End the program")

    while True:
        try:
            choice = int(input("choose (1-5): "))
            if 1 <= choice <= 5:
                return choice
            else:
                print("Choose between 1 och 5")
        except:
            print("Enter a number")


def portscan(port):
    try:
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                open_port.append(port)

port_list = range(1, 1024)
fill_queue(port_list)

thread_list = []

for i in range(100):
    thread = threading.Thread(target=worker)
    thread_list.append(thread)

for thread in thread_list:
    thread.start()

for thread in thread_list:
    thread.join()

print("Open ports are: ", open_ports)
