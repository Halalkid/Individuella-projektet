#!/usr/bin/python3
import logging
import socket
import threading
from queue import Queue

def setup_logging():

    logging.basicConfig(level= logging.INFO, filename = "port_scanner.log", filemode= "a",
                        format = "%(asctime)s -  %(levelname)s - %(message)s")

    logging.info("PORT SCANNER INITIALIZING ")

    return "port_scanner.log"

def e_control():
    print("\n [*] RUNNING ENVIRONMENT CHECKS ....")
    logging.info("RUNNING ENVIRONMENT")
    
    python_v = sys.version_info

    if python_v < (3, 6):
        error_msg = f"Python 3.6+ required. Your version: {sys.version}"
        logging.error(error_msg)
        print("[-] ERROR: ", error_msg)
        return False

    print("[+]  PYTHON VERSION COMPATIBLE: ", sys.version.split()[0])
    logging.info(f"PYTHON VERSION:  {sys.version}")
    return True         










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

def main():
    while True:
        choice = meny()  # <-- FUNKAR NU! (meny() istället för show_menu())
        
        if choice == 5:
            print("Ending...")
            break
        
        if choice == 1:
            target = "127.0.0.1"
            print(f"\nScanning localhost ({target})...")
            
        elif choice == 2:
            target = "192.168.1.1"  # Vanlig router IP
            print(f"\nScanning router ({target})...")
            print("Attention: Your router can have another IP!")
            
        elif choice == 3:
            target = input("Enter IP-adress or domainname: ")
            print(f"\nScanning {target}...")
            
        elif choice == 4:
            target = input("Enter IP-adress: ")
            port = int(input("Enter port to test: "))
            
            # Testa bara en port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((target, port))
            sock.close()
            
            if result == 0:
                print(f"\n[+] Port {port} is OPEN on {target}")
                try:
                    service = socket.getservbyport(port)
                    print(f"    Service: {service}")
                except:
                    print("    Service: Unknown")  
            else:
                print(f"\n[-] Port {port} is CLOSED on {target}")
            
            input("\nPress Enter to CONTINUE...")  
            continue
        
        # Kör scanning
        open_ports = scan_target(target)
        
        # Visa resultat
        print(f"\n{'='*50}")
        if open_ports:
            open_ports.sort()
            print(f"Found {len(open_ports)} open ports:")
            for port in open_ports:
                print(f"  • Port {port}")
        else:
            print("No available ports found")  
        print('='*50)
        
        input("\nPress Enter to CONTINUE...")  

if __name__ == "__main__":
    main()

