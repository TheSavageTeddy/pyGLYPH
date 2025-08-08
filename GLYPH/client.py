import socket
from rlwe import RLWE

HOST = '127.0.0.1'
PORT = 1337

class DemoClient:
    def __init__(self, s:socket):
        self.s = s
    
    def sendResource(self, resource):
        self.s.sendall(resource)
        print(f"SYSTEM: Resource sent - {resource.decode()}")

    def recvPk(self):
        data = self.s.recv(4096)
        self.pubkey = data
        print(f"Received public key: {self.pubkey}")
    
if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        rlwe = RLWE()
        server = DemoClient(s)
        
        ## Receive pk
        server.recvPk()

        ## Request resource
        server.sendResource(b"Hello, World!")

        ## Receive resource and signature
        resource = s.recv(1024)
        signature = s.recv(9000)

        ## Verify signature
        if rlwe.verify(resource, signature, server.pubkey):
            print("SYSTEM: resource received")
        else:
            print("SYSTEM: signature verification failed")