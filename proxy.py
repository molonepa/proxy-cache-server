import socket
import _thread

proxy_addr = '127.0.0.1'
port = 8080

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((proxy_addr, port))
    while True:
        # listen forever for incoming connections
        s.listen()
        client_to_proxy, addr = s.accept()
        with client_to_proxy:
            print('connected by', addr)
            data = client_to_proxy.recv(1024)
            if not data:
                # if no data received, loop again
                break
            else:
                data = data.decode()
                print('received ', data)

