import socket
from sage.repl.load import load

# import GLYPH
prev_name = __name__
__name__ = None
load("GLYPH/glyph.sage", globals())
__name__ = prev_name

HOST = '127.0.0.1'
PORT = 1337

class DemoClient:
    def __init__(self, s:socket):
        self.s = s
    
    def sendResource(self, resource):
        self.s.sendall(resource)
        print(f"SYSTEM: Resource sent - {resource.decode()}\n")

    def recvPk(self):
        data = self.s.recv(4096)
        self.pubkey = data
        print(f"Received public key: {self.pubkey}\n")
    
if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("""
        =======================================
        ============ DEMO VERIFIED ============
        =======================================      
        """)
        s.connect((HOST, PORT))

        glyph = GLYPH()
        server = DemoClient(s)
        
        ## Receive pk
        server.recvPk()

        ## Request resource
        server.sendResource(b"Hello, World!")

        ## Receive resource and signature
        resource = s.recv(1024)
        signature = s.recv(9000)

        ## Verify signature
        if glyph.verify(resource, signature, server.pubkey):
            print("SYSTEM: resource received and verified\n")
        else:
            print("SYSTEM: signature verification failed\n")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("""\n\n
        =======================================
        =========== DEMO UNVERIFIED ===========
        =======================================      
        """)

        s.connect((HOST, PORT))

        glyph = GLYPH()
        server = DemoClient(s)
        
        ## Receive pk
        server.recvPk()

        ## Request resource
        server.sendResource(b"Hello, World!")

        ## Receive resource and signature
        resource = s.recv(1024)
        signature = s.recv(9000)

        resource = b"MALICIOUS WORLD"

        ## Verify signature
        print(f"{resource = }\n")
        if glyph.verify(resource, signature, server.pubkey):
            print("SYSTEM: resource verified\n")
        else:
            print("SYSTEM: signature verification failed\n")