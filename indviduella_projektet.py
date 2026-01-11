#!/usr/bin/python3

import socket
import threading
from queue import Queue


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


def scan_target(ip, start_port=1, end_port=1024):
    """Kör port scanning på en IP"""
    queue = Queue()
    open_ports = []
    
    def portscan(port):
        try:
            s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s1.settimeout(0.5)
            result = s1.connect_ex((ip, port))
            s1.close()
            return result == 0
        except:
            return False
    
    def worker():
        while not queue.empty():
            port = queue.get()
            if portscan(port):
                print(f"  Port {port}")
                open_ports.append(port)
            queue.task_done()

    # Fyll kön
    for port in range(start_port, end_port + 1):
        queue.put(port)
    
    # Starta trådar
    threads = []
    for i in range(min(100, (end_port - start_port + 1))):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        threads.append(t)
    
    # Vänta
    queue.join()
    
    return open_ports
