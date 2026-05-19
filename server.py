import socket
import threading
import json
import uuid

HOST = '0.0.0.0'
PORT = 8721
TIMEOUT = 5.0

clients = {}
tasks = {}
lock = threading.RLock()

def broadcast_client_list():
    """Trimite lista actualizata de clienti catre toti cei conectati."""
    with lock:
        client_list = [{"nume": c, "ip": clients[c]['ip']} for c in clients]
        msg = {"type": "client_list", "clients": client_list}
        data = json.dumps(msg) + "\n"
        
        for c_name, c_info in list(clients.items()):
            try:
                c_info['conn'].sendall(data.encode('utf-8'))
            except:
                pass

def handle_client(conn, addr):
    name = None
    buffer = ""
    try:
        data = conn.recv(1024).decode('utf-8')
        if not data: return
        
        req = json.loads(data.strip())
        if req.get("type") != "register": return
        
        name = req["name"].strip()
        ip = req.get("ip", addr[0])
        
        with lock:
            if name in clients:
                err_msg = json.dumps({"type": "error", "msg": "Numele exista deja!"}) + "\n"
                conn.sendall(err_msg.encode('utf-8'))
                return
            clients[name] = {'conn': conn, 'ip': ip}
        
        conn.sendall((json.dumps({"type": "info", "msg": "Te-ai conectat cu succes!"}) + "\n").encode('utf-8'))
        broadcast_client_list()
        
        while True:
            data = conn.recv(4096).decode('utf-8')
            if not data: break
            buffer += data
            
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                if not line.strip(): continue
                
                msg = json.loads(line)
                mtype = msg.get("type")
                
                if mtype == "query":
                    target = msg.get("target")
                    cmd = msg.get("cmd")
                    task_id = str(uuid.uuid4())
                    
                    targets = []
                    with lock:
                        if target == "all":
                            targets = list(clients.keys())
                        elif target in clients:
                            targets = [target]
                        else:
                            conn.sendall((json.dumps({"type": "info", "msg": f"Tinta '{target}' nu exista."}) + "\n").encode('utf-8'))
                            continue
                        
                        tasks[task_id] = {
                            'results': {}, 
                            'expected': len(targets), 
                            'event': threading.Event()
                        }
                        
                        exec_msg = json.dumps({"type": "exec", "task_id": task_id, "cmd": cmd}) + "\n"
                        for t in targets:
                            try:
                                clients[t]['conn'].sendall(exec_msg.encode('utf-8'))
                            except:
                                tasks[task_id]['results'][t] = "Eroare: Conexiune pierduta"
                    
                    tasks[task_id]['event'].wait(TIMEOUT)
                    
                    with lock:
                        for t in targets:
                            if t not in tasks[task_id]['results']:
                                tasks[task_id]['results'][t] = "TIMEOUT (Tinta nu a raspuns in timp util)"
                        
                        final_results = tasks[task_id]['results']
                        del tasks[task_id]
                    
                    res_msg = json.dumps({"type": "query_result", "cmd": cmd, "results": final_results}) + "\n"
                    conn.sendall(res_msg.encode('utf-8'))
                    
                elif mtype == "result":
                    task_id = msg.get("task_id")
                    res = msg.get("result")
                    
                    with lock:
                        if task_id in tasks:
                            tasks[task_id]['results'][name] = res
                            if len(tasks[task_id]['results']) == tasks[task_id]['expected']:
                                tasks[task_id]['event'].set()

    except Exception as e:
        pass 
    finally:
        # 3. Deconectare
        if name and name in clients:
            with lock:
                del clients[name]
            broadcast_client_list()
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server pornit pe portul {PORT}...")
    
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()