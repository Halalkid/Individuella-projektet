#!/usr/bin/python3

#CS25
#FSH
#Halalkid1: Haider
#Cyber security project: Port Scanner



import socket
import threading
import logging
import sys
import time
from queue import Queue
import argparse  

def setup_logging():
    # Konfigurerar logging-systemet med basic inställningar
    logging.basicConfig(level= logging.INFO, filename = "port_scanner.log", filemode= "a",
                        format = "%(asctime)s -  %(levelname)s - %(message)s")

    logging.info("PORT SCANNER INITIALIZING")
    return "port_scanner.log"

def parse_arguments():
    # Hanterar kommandoradsargument 
    parser = argparse.ArgumentParser(
        description="Port Scanner - Educational Tool by Halalkid1",
        epilog="Example: python port_scanner.py -t 192.168.1.1 -p 80,443"
    )
    
    
    parser.add_argument("-t", "--target", 
                       help="Target IP address or hostname to scan")
    parser.add_argument("-p", "--ports", default="1-1024",
                       help="Port range (1-1000) or list (80,443,22)")
    parser.add_argument("-v", "--version", action="store_true",
                       help="Show version information")
    parser.add_argument("--help-menu", action="store_true",
                       help="Show help information")
    
    return parser.parse_args()

def e_control():
    # Kontrollerar miljön innan programmet startar
    print("\n[*]RUNNING ENVIRONMENT CHECKS ....")
    logging.info("RUNNING ENVIRONMENT")
    
    # KONTROLL 1: Python version check
    python_v = sys.version_info

    if python_v < (3, 6):
        error_msg = f"Python 3.6+ required. Your version: {sys.version}"
        logging.error(error_msg)
        print("[-] ERROR: ", error_msg)
        return False

    print("[+]PYTHON VERSION COMPATIBLE: ", sys.version.split()[0])
    logging.info(f"PYTHON VERSION: {sys.version}")
    
    # KONTROLL 2: Network access check 
    try:
        socket.gethostbyname("localhost")
        print("[+]NETWORK ACCESS COMPLETE")
        logging.info("NETWORK ACCESS VERIFIED")
        return True
    except socket.error as e:
        error_msg = f"NO NETWORK ACCESS: {e}"
        logging.error(error_msg)
        print("[-] ERROR: NO NETWORK ACCESS")
        print("====CHECK YOUR NETWORK CONNECTION====")
        return False

def meny():  
    # Visar huvudmenyn för användaren
    print("What do you want to scan:")
    print("1. Your own PC(local host)")
    print("2. Your router")
    print("3. Enter you own IP-address")
    print("4. Try a specific port")
    print("5. Show command line help")
    print("6. End the program")

    while True:
        try:
            choice = int(input("choose (1-6): "))
            if 1 <= choice <= 6:
                logging.info(f"User selected menu option {choice}")
                return choice
            else:
                print("Choose between 1 and 6")
        except ValueError:
            print("Enter a number")

def portscan(ip, port):
    # Funktion för att skanna en enskild port
    try:
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.settimeout(0.5)
        result = s1.connect_ex((ip, port))
        s1.close()

        if result == 0:
            logging.info(f"Port {port} is OPEN on {ip}")
        else:
            logging.debug(f"Port {port} is CLOSED on {ip}")
            
        return result == 0
    except socket.timeout:
        logging.debug(f"Port {port} timeout on {ip}")
        return False
    except ConnectionRefusedError:
        logging.debug(f"Port {port} connection refused on {ip}")
        return False
    except Exception as e:
        logging.error(f"Error scanning port {port} on {ip}: {e}")
        return False

def scan_target(ip, start_port=1, end_port=1024):
    """Kör port scanning på en IP"""
    queue = Queue()
    open_ports = []
    
    def worker():
        # Worker-funktion som körs i varje tråd
        while not queue.empty():
            port = queue.get()
            if portscan(ip, port):
                print(f"  Port {port}")
                open_ports.append(port)
            queue.task_done()
    
    # Logga scanning start
    logging.info(f"Starting scan of {ip} (ports {start_port}-{end_port})")
    print(f"\n[*] Scanning {ip} (ports {start_port}-{end_port})...")
    print("[*] This may take a moment...\n")

    # Fyll kön med portar att skanna
    for port in range(start_port, end_port + 1):
        queue.put(port)
    
    # Starta trådar för parallell scanning
    threads = []
    for i in range(min(100, (end_port - start_port + 1))):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        threads.append(t)
    
    # Vänta på att alla trådar ska bli klara
    queue.join()
    logging.info(f"Scan complete. Found {len(open_ports)} open ports")
    return open_ports

def banner_grab(ip, port, timeout=2):
    """Försöker hämta banner från en tjänst"""
    try:
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.settimeout(timeout)
        s2.connect((ip, port))
        
        # Skicka något för att få svar
        if port == 80 or port == 443:
            sock.send(b"GET / HTTP/1.0\r\n\r\n")
        elif port == 21:
            sock.send(b"\r\n")
        elif port == 22:
            sock.send(b"SSH-2.0-Client\r\n")
        else:
            sock.send(b"\r\n")
        
        # Ta emot banner
        banner = sock.recv(1024).decode('utf-8', errors='ignore')
        sock.close()
        
        if banner:
            logging.info(f"Banner from {ip}:{port}: {banner[:100]}...")
        
        return banner.strip()[:200]
        
    except Exception as e:
        logging.warning(f"Could not grab banner from {ip}:{port}: {e}")
        return f"No banner or error: {e}"

def command_line_mode(args):
    """Kör programmet i kommandoradsläge med flaggor"""
    print("\n" + "="*60)
    print("        PORT SCANNER - COMMAND LINE MODE")
    print("="*60)
    
    if args.version:
        # Visa version  -v/--version flagga
        print("Port Scanner v1.0")
        print("Created by: Halalkid1 (Haider)")
        print("Educational use only!")
        return
    
    if args.help_menu:
        # Visa hjälp  -h/--help flagga
        print("\nCommand Line Usage:")
        print("  python port_scanner.py -t TARGET [-p PORTS]")
        print("\nExamples:")
        print("  python port_scanner.py -t 192.168.1.1")
        print("  python port_scanner.py -t google.com -p 80,443")
        print("  python port_scanner.py --help-menu")
        print("  python port_scanner.py --version")
        print("\nUse without arguments for interactive mode")
        return
    
    if not args.target:
        print("[-] ERROR: No target specified")
        print("[*] Use: python port_scanner.py -t TARGET")
        return
    
    target = args.target
    print(f"[*] Target: {target}")
    
    # Parse port range från argument
    ports_to_scan = []
    if "-" in args.ports:
        try:
            start, end = map(int, args.ports.split("-"))
            ports_to_scan = list(range(start, end + 1))
        except:
            ports_to_scan = list(range(1, 1025))
    elif "," in args.ports:
        try:
            ports_to_scan = [int(p) for p in args.ports.split(",")]
        except:
            ports_to_scan = [80, 443, 22]
    else:
        try:
            ports_to_scan = [int(args.ports)]
        except:
            ports_to_scan = list(range(1, 1025))
    
    print(f"[*] Ports to scan: {len(ports_to_scan)} ports")
    
    # Starta logging
    log_file = setup_logging()
    print(f"[*]Logging to: {log_file}")
    
    # Kör miljökontroller
    if not e_control():
        print("\n[-] Cannot continue due to environment issues")
        logging.error("Exiting due to failed environment checks")
        return
    
    # Kör scanning
    if len(ports_to_scan) > 1:
        start_port = min(ports_to_scan)
        end_port = max(ports_to_scan)
        open_ports = scan_target(target, start_port, end_port)
    else:
        # För enskild port
        port = ports_to_scan[0]
        print(f"\n[*] Testing {target}:{port}...")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((target, port))
        sock.close()
        
        if result == 0:
            print(f"[+] Port {port} is OPEN on {target}")
            open_ports = [port]
        else:
            print(f"[-] Port {port} is CLOSED on {target}")
            open_ports = []
    
    # Visa resultat
    if open_ports:
        print(f"\nFound {len(open_ports)} open ports:")
        for port in sorted(open_ports):
            print(f"  • Port {port}")
    else:
        print("\nNo open ports found")
    
    print(f"\n[*] Scan complete. Log saved to: {log_file}")

def main():
    # Huvudfunktionen som startar programmet
    
    
    args = parse_arguments()
    
   
    if any([args.target, args.version, args.help_menu]):
        command_line_mode(args)
        return
    
    
    print(r"""
 ██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗
 ██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝
 ██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗  
 ██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝  
 ╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗
  ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝   

      ░░░░░░░░░░░░░░░░░░░░░░░░░░░
      ░ PORT  SCANNER PROJECT   ░
      ░░░░░░░░░░░░░░░░░░░░░░░░░░░

        !!! ATTENTON:IM NOT LIABLE FOR YOUR USE OF THE PROGRAM:
        USE THIS ONLY FOR EDUCATIONAL PURPOSES (USE WITH CAUTION)!!!


       >>> MADE BY: HALALKID1 :: HAIDER <<<
""")

    # 1. Setup logging
    log_file = setup_logging()
    print(f"[*]Logging to: {log_file}")
    
    # 2. Check environment 
    if not e_control():
        print("\n[-] Cannot continue due to environment issues")
        logging.error("Exiting due to failed environment checks")
        return
    
    print("\n" + "="*60)
    print("        WELCOME TO PORT SCANNER")
    print("="*60)
    logging.info("Port Scanner started successfully")

    while True:
        choice = meny()
        
        if choice == 6:
            print("Ending...")
            print(f"[*] Log saved to: {log_file}")
            logging.info("Program ending normally")
            break
        
        if choice == 5:
            # Visa kommandorads-hjälp
            print("\n" + "="*60)
            print("COMMAND LINE USAGE:")
            print("="*60)
            print("You can also use command line mode:")
            print("\n  python port_scanner.py -t 192.168.1.1")
            print("  python port_scanner.py -t google.com -p 80,443")
            print("  python port_scanner.py --help-menu")
            print("  python port_scanner.py --version")
            print("\nUse -h or --help for more information")
            print("="*60)
            input("\nPress Enter to continue...")
            continue
        
        if choice == 1:
            target = "127.0.0.1"
            logging.info(f"\nScanning localhost ({target})...")
            
        elif choice == 2:
            target = "192.168.1.1"
            print(f"\nScanning router ({target})...")
            print("Attention: Your router can have another IP!")
            logging.info(f"Scanning router ({target})")

        elif choice == 3:
            target = input("Enter IP-adress or domainname: ")
            print(f"\nScanning {target}...")
            logging.info(f"Scanning custom target: {target}")

        elif choice == 4:
            target = input("Enter IP-adress: ")
            if not target:
                target = "127.0.0.1"
            try:
                port = int(input("Enter port to test (1-65535): "))
                if port < 1 or port > 65535:
                    print("[-] Invalid port, using 80")
                    port = 80
            except ValueError:
                print("[-] Invalid port, using 80")
                port = 80

            logging.info(f"Testing single port {port} on {target}")
            print(f"\n[*] Testing {target}:{port}...")
            
            # Testa en port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((target, port))
            sock.close()

            if result == 0:
                print(f"\n[+] Port {port} is OPEN on {target}")
                logging.info(f"Port {port} is OPEN on {target}")

                banner = banner_grab(target, port)
                if banner and "No banner" not in banner:
                    print(f"    Banner: {banner[:100]}...")

                try:
                    service = socket.getservbyport(port)
                    print(f"    Service: {service}")
                    logging.info(f"Service on port {port}: {service}")
                except:
                    print("    Service: Unknown")
                    logging.info(f"Service on port {port}: Unknown")
            else:
                print(f"\n[-] Port {port} is CLOSED on {target}")
                logging.info(f"Port {port} is CLOSED on {target}")
                
            input("\nPress Enter to CONTINUE...")
            continue

        # Fråga om portintervall för scanning
        print("\n[*] Port range settings:")
        
        try:
            start = int(input("Start port (1-65535) [default 1]: ") or "1")
            if start < 1 or start > 65535:
                print("[!] Invalid, using 1")
                logging.warning(f"Invalid start port, using 1")
                start = 1
        except ValueError:
            print("[!] Invalid, using 1")
            logging.warning("Invalid start port input, using 1")
            start = 1
        
        try:
            end = int(input(f"End port ({start}-65535) [default 1024]: ") or "1024")
            if end < start or end > 65535:
                print(f"[!] Invalid, using {min(start + 1023, 65535)}")
                logging.warning(f"Invalid end port, using {min(start + 1023, 65535)}")
                end = min(start + 1023, 65535)
        except ValueError:
            print(f"[!] Invalid, using {min(start + 1023, 65535)}")
            logging.warning("Invalid end port input, using default")
            end = min(start + 1023, 65535)
            
        # Kör scanning
        open_ports = scan_target(target, start, end)
        
        # Visa resultat
        print(f"\n{'='*50}")
        if open_ports:
            open_ports.sort()
            print(f"Found {len(open_ports)} open ports:")
            logging.info(f"Open ports found: {open_ports}")

            for port in open_ports:
                # Försök identifiera tjänst
                try:
                    service = socket.getservbyport(port)
                    print(f"  • Port {port:5} - {service}")
                    
                    # Försök hämta banner för viktiga portar
                    if port in [21, 22, 23, 25, 80, 443]:
                        banner = banner_grab(target, port)
                        if banner and "No banner" not in banner:
                            print(f"      Banner: {banner[:80]}...")
                except:
                    print(f"  • Port {port:5} - Unknown service")
        else:
            print("\n[-] No open ports found")
            logging.info("No open ports found")
        
        print('='*60)
        
        input("\n[*] Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] Program interrupted by user")
        logging.warning("Program interrupted by user")
    except Exception as e:
        print(f"\n[-] Unexpected error: {e}")
        logging.critical(f"Unexpected error: {e}")

