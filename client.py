import socket
import threading
import json
import sys
import time
import platform

HOST = '127.0.0.1'
PORT = 8721

def simuleaza_comanda(cmd):
    """Functie care simuleaza un subset de comenzi tip WMI/Sistem."""
    cmd = cmd.lower()
    if cmd == "os":
        return f"{platform.system()} {platform.release()}"
    elif cmd == "time":
        return time.ctime()
    elif cmd == "ping":
        return "PONG!"
    else:
        return f"Eroare: Comanda '{cmd}' invalida. (Folositi: os, time, ping)"

def asculta_server(sock):
    """Thread separat: Asculta si proceseaza mesajele venite de la server."""
    buffer = ""
    while True:
        try:
            data = sock.recv(4096).decode('utf-8')
            if not data: break
            buffer += data
            
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                if not line.strip(): continue
                
                msg = json.loads(line)
                mtype = msg.get("type")
                
                if mtype in ["info", "error"]:
                    print(f"\n[SERVER] {msg.get('msg')}\n> ", end="")
                
                elif mtype == "client_list":
                    print("\n[SERVER] --- Lista Clienti Actualizata ---")
                    for c in msg.get("clients", []):
                        print(f"  - {c['nume']} (IP: {c['ip']})")
                    print("> ", end="")
                    
                elif mtype == "exec":
                    task_id = msg.get("task_id")
                    cmd = msg.get("cmd")
                    
                    rezultat = simuleaza_comanda(cmd)
                    
                    raspuns = {"type": "result", "task_id": task_id, "result": rezultat}
                    sock.sendall((json.dumps(raspuns) + "\n").encode('utf-8'))
                    
                elif mtype == "query_result":
                    print(f"\n[REZULTATE INTEROGARE: '{msg.get('cmd')}']")
                    for tinta, rez in msg.get("results", {}).items():
                        print(f"  [{tinta}]: {rez}")
                    print("> ", end="")
                    
        except Exception:
            break
            
    print("\nDeconectat de la server.")
    sys.exit(0)

def main():
    nume = input("Introdu numele tau: ")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except:
        print("Eroare: Serverul nu este pornit!")
        return
        
    my_ip = socket.gethostbyname(socket.gethostname())
    reg_msg = {"type": "register", "name": nume, "ip": my_ip}
    sock.sendall((json.dumps(reg_msg) + "\n").encode('utf-8'))
    
    threading.Thread(target=asculta_server, args=(sock,), daemon=True).start()
    
    print("Comenzi disponibile (Operator):")
    print("  query all <comanda>")
    print("  query <nume_tinta> <comanda>")
    print("  (Comenzi suportate: os, time, ping)")
    
    while True:
        try:
            text = input("> ").strip()
            if not text: continue
            
            parti = text.split(maxsplit=2)
            if len(parti) == 3 and parti[0].lower() == "query":
                tinta = parti[1]
                cmd = parti[2]
                
                req = {"type": "query", "target": tinta, "cmd": cmd}
                sock.sendall((json.dumps(req) + "\n").encode('utf-8'))
            else:
                print("Format gresit. Exemplu: query all os  SAU  query Client2 ping")
        except KeyboardInterrupt:
            break
            
    sock.close()

if __name__ == "__main__":
    main()