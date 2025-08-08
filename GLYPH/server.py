import socket
from rlwe import RLWE

import time

HOST = '127.0.0.1'
PORT = 1337

class DemoServer:
    def __init__(self, conn):
        self.conn = conn
        self.pubkey, self.privkey = rlwe.keygen()

    def keygen(self):
        self.conn.sendall(self.pubkey)
        print("SYSTEM:\tPublic key sent")

    def recvResource(self):
        data = self.conn.recv(1024)
        print(f"Received resource: {data.decode()}")
        return data
    
    def sendResource(self, m):
        print(f"SYSTEM: Sending resource: {m.decode()}")
        sign = rlwe.sign(m, self.privkey)

        self.conn.sendall(m)
        print("SYSTEM:\tMessage sent")
        time.sleep(0.5)

        self.conn.sendall(sign)
        print("SYSTEM:\tSignature sent")

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))

        while True:
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('SYSTEM: Connected by', addr)

                rlwe = RLWE()
                pubkey, privkey = rlwe._keygen()
                client = DemoServer(conn)

                ## Send public key
                client.keygen()

                ## Client requests resource
                req = client.recvResource()

                ## Send resource and proof
                client.sendResource("Hello, World".encode())

                while True:
                    pass